# 📱 Phone Stock Manager

A full CRUD stock management system built for a small phone reselling business in Johannesburg. Replaces manual pen-and-paper tracking with a clean web dashboard.

**Built with:** Python, Flask, SQLite, HTML/CSS, JavaScript, Chart.js

---

## Features

- **Dashboard** — live KPIs: stock value, revenue, gross/net profit, active repairs + 4 analytics charts
- **Stock** — full CRUD for phone inventory with IMEI tracking, condition grading, buy/sell price, supplier linking
- **Sales** — record sales, auto-mark stock as sold, profit calculated per transaction
- **Repairs** — log repair jobs, track status (Pending / In Progress / Done), link to stock items
- **Expenses** — track business costs by category (Rent, Electricity, Marketing, etc.)
- **Suppliers** — manage supplier contacts, link phones to source

## Tech Stack

| Layer      | Technology             |
|------------|------------------------|
| Backend    | Python, Flask          |
| Database   | SQLite (5 tables)      |
| Frontend   | HTML, CSS, JavaScript  |
| Charts     | Chart.js               |
| Theme      | Black & green terminal |

## Setup

```bash
# 1. Install dependencies
pip install flask pandas

# 2. Set up database and seed sample data
cd database
python setup_db.py

# 3. Run the app
cd ..
python app.py

# 4. Open in browser
# http://localhost:5000
```

## Database Schema

```
suppliers  — id, name, contact, phone, email, address
stock      — id, brand, model, imei, storage, colour, condition, buy_price, sell_price, status, supplier_id
sales      — id, stock_id, sell_price, platform, buyer_name, buyer_phone, sale_date
repairs    — id, stock_id, device_name, issue, repair_cost, status, customer_name
expenses   — id, category, description, amount, date
```

---

*Portfolio project — Fayaaz Vally | [github.com/VisioneGT](https://github.com/VisioneGT)*
