"""
PhoneStockManager — Flask backend
Run: python app.py
"""
import sqlite3
import os
import json
from datetime import date
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'stock.db')

# ── DB HELPER ─────────────────────────────────────────────────────────────

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def rows(conn, sql, params=()):
    return [dict(r) for r in conn.execute(sql, params).fetchall()]

def one(conn, sql, params=()):
    r = conn.execute(sql, params).fetchone()
    return dict(r) if r else None

# ── PAGES ─────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    conn = db()
    # KPIs
    total_stock   = one(conn, "SELECT COUNT(*) c FROM stock WHERE status='In Stock'")["c"]
    sold_count    = one(conn, "SELECT COUNT(*) c FROM stock WHERE status='Sold'")["c"]
    total_revenue = one(conn, "SELECT COALESCE(SUM(sell_price),0) s FROM sales")["s"]
    total_cost    = one(conn, "SELECT COALESCE(SUM(buy_price),0) s FROM stock WHERE status='Sold'")["s"]
    gross_profit  = total_revenue - total_cost
    repair_count  = one(conn, "SELECT COUNT(*) c FROM repairs WHERE status IN ('Pending','In Progress')")["c"]
    total_expenses= one(conn, "SELECT COALESCE(SUM(amount),0) s FROM expenses")["s"]
    net_profit    = gross_profit - total_expenses
    stock_value   = one(conn, "SELECT COALESCE(SUM(buy_price),0) s FROM stock WHERE status='In Stock'")["s"]

    # Charts data
    # Sales by platform
    platform_data = rows(conn, """
        SELECT platform, COUNT(*) cnt, SUM(sell_price) revenue
        FROM sales GROUP BY platform ORDER BY cnt DESC
    """)
    # Monthly profit (last 6 months)
    monthly = rows(conn, """
        SELECT strftime('%Y-%m', s.sale_date) mo,
               SUM(s.sell_price) revenue,
               SUM(st.buy_price) cost,
               SUM(s.sell_price - st.buy_price) profit
        FROM sales s JOIN stock st ON s.stock_id=st.id
        GROUP BY mo ORDER BY mo DESC LIMIT 6
    """)
    monthly.reverse()
    # Top brands by units sold
    brand_data = rows(conn, """
        SELECT st.brand, COUNT(*) sold
        FROM sales s JOIN stock st ON s.stock_id=st.id
        GROUP BY st.brand ORDER BY sold DESC
    """)
    # Stock by condition
    condition_data = rows(conn, """
        SELECT condition, COUNT(*) cnt FROM stock
        WHERE status='In Stock' GROUP BY condition
    """)
    # Recent sales
    recent_sales = rows(conn, """
        SELECT s.sale_date, st.brand||' '||st.model model,
               s.sell_price, st.buy_price,
               s.sell_price - st.buy_price profit,
               s.platform, s.buyer_name
        FROM sales s JOIN stock st ON s.stock_id=st.id
        ORDER BY s.sale_date DESC LIMIT 8
    """)
    # Low stock alert (only 1 of model)
    low_stock = rows(conn, """
        SELECT brand||' '||model model, COUNT(*) cnt
        FROM stock WHERE status='In Stock'
        GROUP BY brand,model HAVING cnt <= 1
        ORDER BY brand LIMIT 5
    """)
    conn.close()
    return render_template("dashboard.html",
        kpis=dict(
            total_stock=total_stock, sold_count=sold_count,
            total_revenue=total_revenue, gross_profit=gross_profit,
            net_profit=net_profit, repair_count=repair_count,
            stock_value=stock_value
        ),
        platform_data=json.dumps(platform_data),
        monthly=json.dumps(monthly),
        brand_data=json.dumps(brand_data),
        condition_data=json.dumps(condition_data),
        recent_sales=recent_sales,
        low_stock=low_stock
    )

@app.route("/stock")
def stock_page():
    conn = db()
    search  = request.args.get("q", "")
    status  = request.args.get("status", "")
    brand   = request.args.get("brand", "")
    sql = """
        SELECT s.*, sup.name supplier_name
        FROM stock s LEFT JOIN suppliers sup ON s.supplier_id=sup.id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (s.brand||' '||s.model LIKE ? OR s.imei LIKE ? OR s.colour LIKE ?)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if status:
        sql += " AND s.status=?"
        params.append(status)
    if brand:
        sql += " AND s.brand=?"
        params.append(brand)
    sql += " ORDER BY s.date_purchased DESC"
    stock_list = rows(conn, sql, params)
    suppliers  = rows(conn, "SELECT id, name FROM suppliers ORDER BY name")
    brands     = rows(conn, "SELECT DISTINCT brand FROM stock ORDER BY brand")
    conn.close()
    return render_template("stock.html", stock=stock_list, suppliers=suppliers,
                           brands=brands, search=search, filter_status=status, filter_brand=brand)

@app.route("/stock/add", methods=["POST"])
def add_stock():
    d = request.form
    conn = db()
    conn.execute("""
        INSERT INTO stock (brand,model,imei,storage,colour,condition,buy_price,sell_price,status,supplier_id,date_purchased,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (d["brand"], d["model"], d.get("imei") or None, d.get("storage"),
          d.get("colour"), d["condition"], float(d["buy_price"]),
          float(d["sell_price"]) if d.get("sell_price") else None,
          d.get("status","In Stock"),
          int(d["supplier_id"]) if d.get("supplier_id") else None,
          d.get("date_purchased") or date.today().isoformat(),
          d.get("notes")))
    conn.commit()
    conn.close()
    return redirect(url_for("stock_page"))

@app.route("/stock/edit/<int:sid>", methods=["POST"])
def edit_stock(sid):
    d = request.form
    conn = db()
    conn.execute("""
        UPDATE stock SET brand=?,model=?,imei=?,storage=?,colour=?,condition=?,
        buy_price=?,sell_price=?,status=?,supplier_id=?,date_purchased=?,notes=?
        WHERE id=?
    """, (d["brand"], d["model"], d.get("imei") or None, d.get("storage"),
          d.get("colour"), d["condition"], float(d["buy_price"]),
          float(d["sell_price"]) if d.get("sell_price") else None,
          d.get("status","In Stock"),
          int(d["supplier_id"]) if d.get("supplier_id") else None,
          d.get("date_purchased") or date.today().isoformat(),
          d.get("notes"), sid))
    conn.commit()
    conn.close()
    return redirect(url_for("stock_page"))

@app.route("/stock/delete/<int:sid>", methods=["POST"])
def delete_stock(sid):
    conn = db()
    conn.execute("DELETE FROM stock WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return redirect(url_for("stock_page"))

@app.route("/stock/get/<int:sid>")
def get_stock(sid):
    conn = db()
    item = one(conn, "SELECT * FROM stock WHERE id=?", (sid,))
    conn.close()
    return jsonify(item)

# ── SALES ─────────────────────────────────────────────────────────────────

@app.route("/sales")
def sales_page():
    conn = db()
    sales_list = rows(conn, """
        SELECT s.*, st.brand||' '||st.model model, st.buy_price,
               s.sell_price - st.buy_price profit
        FROM sales s JOIN stock st ON s.stock_id=st.id
        ORDER BY s.sale_date DESC
    """)
    available = rows(conn, """
        SELECT id, brand||' '||model||' ('||COALESCE(storage,'')||' '||colour||')' label, sell_price
        FROM stock WHERE status='In Stock' ORDER BY brand,model
    """)
    conn.close()
    return render_template("sales.html", sales=sales_list, available=available)

@app.route("/sales/add", methods=["POST"])
def add_sale():
    d = request.form
    conn = db()
    conn.execute("""
        INSERT INTO sales (stock_id,sell_price,platform,buyer_name,buyer_phone,sale_date,notes)
        VALUES (?,?,?,?,?,?,?)
    """, (int(d["stock_id"]), float(d["sell_price"]),
          d.get("platform"), d.get("buyer_name"), d.get("buyer_phone"),
          d.get("sale_date") or date.today().isoformat(), d.get("notes")))
    conn.execute("UPDATE stock SET status='Sold' WHERE id=?", (int(d["stock_id"]),))
    conn.commit()
    conn.close()
    return redirect(url_for("sales_page"))

@app.route("/sales/delete/<int:sid>", methods=["POST"])
def delete_sale(sid):
    conn = db()
    sale = one(conn, "SELECT stock_id FROM sales WHERE id=?", (sid,))
    if sale:
        conn.execute("DELETE FROM sales WHERE id=?", (sid,))
        conn.execute("UPDATE stock SET status='In Stock' WHERE id=?", (sale["stock_id"],))
        conn.commit()
    conn.close()
    return redirect(url_for("sales_page"))

# ── REPAIRS ───────────────────────────────────────────────────────────────

@app.route("/repairs")
def repairs_page():
    conn = db()
    repairs_list = rows(conn, """
        SELECT r.*, st.brand||' '||st.model stock_model
        FROM repairs r LEFT JOIN stock st ON r.stock_id=st.id
        ORDER BY r.date_received DESC
    """)
    stock_items = rows(conn, """
        SELECT id, brand||' '||model||' ('||COALESCE(imei,'no IMEI')||')' label
        FROM stock ORDER BY brand,model
    """)
    conn.close()
    return render_template("repairs.html", repairs=repairs_list, stock_items=stock_items)

@app.route("/repairs/add", methods=["POST"])
def add_repair():
    d = request.form
    conn = db()
    conn.execute("""
        INSERT INTO repairs (stock_id,device_name,imei,issue,technician,repair_cost,status,date_received,customer_name,customer_phone,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (int(d["stock_id"]) if d.get("stock_id") else None,
          d["device_name"], d.get("imei"), d["issue"],
          d.get("technician"), float(d.get("repair_cost") or 0),
          d.get("status","Pending"),
          d.get("date_received") or date.today().isoformat(),
          d.get("customer_name"), d.get("customer_phone"), d.get("notes")))
    conn.commit()
    conn.close()
    return redirect(url_for("repairs_page"))

@app.route("/repairs/edit/<int:rid>", methods=["POST"])
def edit_repair(rid):
    d = request.form
    completed = d.get("date_completed") or (date.today().isoformat() if d.get("status") == "Done" else None)
    conn = db()
    conn.execute("""
        UPDATE repairs SET device_name=?,imei=?,issue=?,technician=?,repair_cost=?,
        status=?,date_received=?,date_completed=?,customer_name=?,customer_phone=?,notes=?
        WHERE id=?
    """, (d["device_name"], d.get("imei"), d["issue"], d.get("technician"),
          float(d.get("repair_cost") or 0), d.get("status","Pending"),
          d.get("date_received"), completed,
          d.get("customer_name"), d.get("customer_phone"), d.get("notes"), rid))
    conn.commit()
    conn.close()
    return redirect(url_for("repairs_page"))

@app.route("/repairs/delete/<int:rid>", methods=["POST"])
def delete_repair(rid):
    conn = db()
    conn.execute("DELETE FROM repairs WHERE id=?", (rid,))
    conn.commit()
    conn.close()
    return redirect(url_for("repairs_page"))

@app.route("/repairs/get/<int:rid>")
def get_repair(rid):
    conn = db()
    r = one(conn, "SELECT * FROM repairs WHERE id=?", (rid,))
    conn.close()
    return jsonify(r)

# ── EXPENSES ──────────────────────────────────────────────────────────────

@app.route("/expenses")
def expenses_page():
    conn = db()
    exp_list = rows(conn, "SELECT * FROM expenses ORDER BY date DESC")
    total    = one(conn, "SELECT COALESCE(SUM(amount),0) t FROM expenses")["t"]
    by_cat   = rows(conn, "SELECT category, SUM(amount) total FROM expenses GROUP BY category ORDER BY total DESC")
    conn.close()
    return render_template("expenses.html", expenses=exp_list, total=total,
                           by_cat=by_cat, by_cat_json=json.dumps(by_cat))

@app.route("/expenses/add", methods=["POST"])
def add_expense():
    d = request.form
    conn = db()
    conn.execute("INSERT INTO expenses (category,description,amount,date,notes) VALUES (?,?,?,?,?)",
                 (d["category"], d["description"], float(d["amount"]),
                  d.get("date") or date.today().isoformat(), d.get("notes")))
    conn.commit()
    conn.close()
    return redirect(url_for("expenses_page"))

@app.route("/expenses/delete/<int:eid>", methods=["POST"])
def delete_expense(eid):
    conn = db()
    conn.execute("DELETE FROM expenses WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return redirect(url_for("expenses_page"))

# ── SUPPLIERS ─────────────────────────────────────────────────────────────

@app.route("/suppliers")
def suppliers_page():
    conn = db()
    sup_list = rows(conn, """
        SELECT s.*, COUNT(st.id) phone_count
        FROM suppliers s LEFT JOIN stock st ON s.id=st.supplier_id
        GROUP BY s.id ORDER BY s.name
    """)
    conn.close()
    return render_template("suppliers.html", suppliers=sup_list)

@app.route("/suppliers/add", methods=["POST"])
def add_supplier():
    d = request.form
    conn = db()
    conn.execute("INSERT INTO suppliers (name,contact,phone,email,address,notes) VALUES (?,?,?,?,?,?)",
                 (d["name"], d.get("contact"), d.get("phone"), d.get("email"),
                  d.get("address"), d.get("notes")))
    conn.commit()
    conn.close()
    return redirect(url_for("suppliers_page"))

@app.route("/suppliers/edit/<int:sid>", methods=["POST"])
def edit_supplier(sid):
    d = request.form
    conn = db()
    conn.execute("UPDATE suppliers SET name=?,contact=?,phone=?,email=?,address=?,notes=? WHERE id=?",
                 (d["name"], d.get("contact"), d.get("phone"), d.get("email"),
                  d.get("address"), d.get("notes"), sid))
    conn.commit()
    conn.close()
    return redirect(url_for("suppliers_page"))

@app.route("/suppliers/delete/<int:sid>", methods=["POST"])
def delete_supplier(sid):
    conn = db()
    conn.execute("DELETE FROM suppliers WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return redirect(url_for("suppliers_page"))

@app.route("/suppliers/get/<int:sid>")
def get_supplier(sid):
    conn = db()
    s = one(conn, "SELECT * FROM suppliers WHERE id=?", (sid,))
    conn.close()
    return jsonify(s)

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found. Run: python database/setup_db.py first")
    app.run(debug=True, port=5000)

@app.template_filter('fromjson')
def fromjson_filter(s):
    return json.loads(s)

@app.context_processor
def inject_repair_badge():
    try:
        conn = db()
        count = one(conn, "SELECT COUNT(*) c FROM repairs WHERE status IN ('Pending','In Progress')")["c"]
        conn.close()
        return dict(repair_badge=count if count > 0 else None)
    except Exception:
        return dict(repair_badge=None)
