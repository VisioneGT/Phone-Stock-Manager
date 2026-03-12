"""
PhoneStockManager — database setup and realistic seed data
6 months of business history: Oct 2024 – Mar 2025
Run once: python database/setup_db.py
"""
import sqlite3
import os
from datetime import date, timedelta
import random

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock.db')

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def create_tables():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS suppliers (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        contact     TEXT,
        phone       TEXT,
        email       TEXT,
        address     TEXT,
        notes       TEXT,
        created_at  TEXT DEFAULT (date('now'))
    );

    CREATE TABLE IF NOT EXISTS stock (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL,
        model           TEXT NOT NULL,
        imei            TEXT UNIQUE,
        storage         TEXT,
        colour          TEXT,
        condition       TEXT CHECK(condition IN ('New','Excellent','Good','Fair','Poor')),
        buy_price       REAL NOT NULL,
        sell_price      REAL,
        status          TEXT DEFAULT 'In Stock' CHECK(status IN ('In Stock','Sold','Reserved','Repair')),
        supplier_id     INTEGER REFERENCES suppliers(id),
        date_purchased  TEXT DEFAULT (date('now')),
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS sales (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id    INTEGER NOT NULL REFERENCES stock(id),
        sell_price  REAL NOT NULL,
        platform    TEXT CHECK(platform IN ('Walk-in','Facebook','WhatsApp','Gumtree','Takealot','Other')),
        buyer_name  TEXT,
        buyer_phone TEXT,
        sale_date   TEXT DEFAULT (date('now')),
        notes       TEXT
    );

    CREATE TABLE IF NOT EXISTS repairs (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id        INTEGER REFERENCES stock(id),
        device_name     TEXT NOT NULL,
        imei            TEXT,
        issue           TEXT NOT NULL,
        technician      TEXT,
        repair_cost     REAL DEFAULT 0,
        status          TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','In Progress','Done','Cancelled')),
        date_received   TEXT DEFAULT (date('now')),
        date_completed  TEXT,
        customer_name   TEXT,
        customer_phone  TEXT,
        notes           TEXT
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        category    TEXT CHECK(category IN ('Rent','Electricity','Transport','Marketing','Tools','Other')),
        description TEXT NOT NULL,
        amount      REAL NOT NULL,
        date        TEXT DEFAULT (date('now')),
        notes       TEXT
    );
    """)
    conn.commit()
    conn.close()
    print("Tables created.")


def seed_data():
    conn = get_db()
    if conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0] > 0:
        print("Data already seeded.")
        conn.close()
        return

    def d(year, month, day):
        return date(year, month, day).isoformat()

    def make_imei(seed):
        random.seed(seed * 7919)
        digits = [str(random.randint(0, 9)) for _ in range(13)]
        random.seed()
        return "35" + "".join(digits)

    # ── SUPPLIERS ─────────────────────────────────────────────────────────
    suppliers = [
        ("TechSource JHB",     "Sipho Ndlovu",    "011 234 5678", "sipho@techsource.co.za",    "14 Rivonia Rd, Sandton",      "Main iPhone supplier. Bulk discounts on 5+ units. Pay within 3 days."),
        ("MobileWorld SA",     "Priya Naidoo",    "011 876 5432", "priya@mobileworld.co.za",   "32 Oxford Rd, Rosebank",      "Best Samsung pricing in JHB. Warranty on all New stock."),
        ("DropShip Direct",    "Carlos Ferreira", "072 111 2233", "carlos@dropship.co.za",     "Online — ships from Cape Town","Xiaomi and Oppo. 2-3 day delivery. Good for budget models."),
        ("SecondHandHub",      "Thabo Molefe",    "083 456 7890", "thabo@secondhandhub.co.za", "Soweto Dobsonville Mall",     "Pre-owned stock. Always negotiate — usually 10% off listed."),
        ("iRepair Wholesale",  "Fatima Cassim",   "082 900 1122", "fatima@irepair.co.za",      "78 Commissioner St, CBD JHB", "Screen and battery parts wholesale. Fast turnaround on spares."),
    ]
    for s in suppliers:
        conn.execute("INSERT INTO suppliers (name,contact,phone,email,address,notes) VALUES (?,?,?,?,?,?)", s)
    conn.commit()

    # ── STOCK ─────────────────────────────────────────────────────────────
    # brand, model, imei_seed, storage, colour, condition, buy_price, sell_price, supplier_id, date_purchased, status, notes
    phones_data = [
        # Oct 2024
        ("Apple",   "iPhone 13",        1,  "128GB", "Midnight",         "Good",      9500,  13000, 1, d(2024,10,3),  "Sold",     "Minor scratches on back"),
        ("Apple",   "iPhone 11",        2,  "64GB",  "Black",            "Good",      5200,  7000,  1, d(2024,10,3),  "Sold",     ""),
        ("Samsung", "Galaxy A54",       3,  "128GB", "Awesome Graphite", "New",       4100,  5600,  2, d(2024,10,5),  "Sold",     "Sealed box"),
        ("Samsung", "Galaxy A34",       4,  "128GB", "Awesome Silver",   "New",       3000,  4100,  2, d(2024,10,5),  "Sold",     "Sealed box"),
        ("Xiaomi",  "Redmi Note 12",    5,  "128GB", "Ice Blue",         "New",       2100,  3000,  3, d(2024,10,8),  "Sold",     ""),
        ("Apple",   "iPhone 12",        6,  "64GB",  "White",            "Good",      7000,  9500,  4, d(2024,10,10), "Sold",     "Battery at 87%"),
        ("Samsung", "Galaxy S22",       7,  "128GB", "Phantom White",    "Excellent", 8200,  11500, 2, d(2024,10,12), "Sold",     ""),
        ("Huawei",  "P30 Lite",         8,  "128GB", "Pearl White",      "Good",      1900,  2700,  4, d(2024,10,15), "Sold",     ""),
        ("Apple",   "iPhone SE 2022",   9,  "64GB",  "Starlight",        "New",       6200,  8500,  1, d(2024,10,18), "Sold",     ""),
        ("Samsung", "Galaxy A23",       10, "64GB",  "Black",            "Good",      1600,  2300,  4, d(2024,10,20), "Sold",     "Small crack on corner"),
        ("Xiaomi",  "Redmi 10C",        11, "64GB",  "Mint Green",       "New",       1400,  2000,  3, d(2024,10,22), "Sold",     ""),
        ("Apple",   "iPhone 14",        12, "128GB", "Blue",             "Excellent", 12000, 16000, 1, d(2024,10,25), "Sold",     ""),
        # Nov 2024
        ("Apple",   "iPhone 13 Pro",    13, "256GB", "Sierra Blue",      "Excellent", 14500, 19500, 1, d(2024,11,1),  "Sold",     ""),
        ("Samsung", "Galaxy S23",       14, "256GB", "Phantom Black",    "Excellent", 10800, 15000, 2, d(2024,11,2),  "Sold",     ""),
        ("Samsung", "Galaxy A54",       15, "128GB", "Awesome Violet",   "New",       4100,  5600,  2, d(2024,11,4),  "Sold",     "Sealed box"),
        ("Xiaomi",  "Poco X5 Pro",      16, "256GB", "Black",            "New",       3700,  5200,  3, d(2024,11,6),  "Sold",     ""),
        ("Apple",   "iPhone 12 mini",   17, "64GB",  "Red",              "Good",      5800,  8000,  4, d(2024,11,8),  "Sold",     "Battery at 82%"),
        ("Samsung", "Galaxy A14",       18, "64GB",  "Black",            "New",       1800,  2600,  2, d(2024,11,10), "Sold",     ""),
        ("Huawei",  "Nova 5T",          19, "128GB", "Midsummer Purple", "Good",      2200,  3100,  4, d(2024,11,12), "Sold",     ""),
        ("Apple",   "iPhone 11 Pro",    20, "256GB", "Space Grey",       "Good",      7800,  10500, 4, d(2024,11,15), "Sold",     "Battery at 78% — sold as-is"),
        ("Samsung", "Galaxy S21 FE",    21, "128GB", "Lavender",         "Good",      6000,  8200,  2, d(2024,11,18), "Sold",     ""),
        ("Xiaomi",  "Redmi Note 11",    22, "128GB", "Graphite Grey",    "New",       2000,  2900,  3, d(2024,11,20), "Sold",     ""),
        ("Apple",   "iPhone 14",        23, "256GB", "Midnight",         "Excellent", 13500, 18000, 1, d(2024,11,22), "Sold",     ""),
        ("Samsung", "Galaxy A73",       24, "256GB", "White",            "Excellent", 5500,  7500,  2, d(2024,11,25), "Sold",     ""),
        # Dec 2024 — festive season, busiest month
        ("Apple",   "iPhone 14 Pro",    25, "256GB", "Deep Purple",      "Excellent", 17000, 22500, 1, d(2024,12,1),  "Sold",     ""),
        ("Apple",   "iPhone 15",        26, "128GB", "Black",            "New",       19500, 26000, 1, d(2024,12,2),  "Sold",     "Sealed — Christmas stock"),
        ("Apple",   "iPhone 15",        27, "128GB", "Pink",             "New",       19500, 26000, 1, d(2024,12,2),  "Sold",     "Sealed — Christmas stock"),
        ("Samsung", "Galaxy S24",       28, "256GB", "Cobalt Violet",    "New",       17500, 23000, 2, d(2024,12,3),  "Sold",     "Sealed box"),
        ("Samsung", "Galaxy S23",       29, "128GB", "Cream",            "Excellent", 10500, 14500, 2, d(2024,12,5),  "Sold",     ""),
        ("Apple",   "iPhone 13",        30, "128GB", "Pink",             "Good",      9200,  12800, 1, d(2024,12,7),  "Sold",     ""),
        ("Apple",   "iPhone 13",        31, "256GB", "Starlight",        "Excellent", 10000, 14000, 1, d(2024,12,7),  "Sold",     ""),
        ("Samsung", "Galaxy A54",       32, "128GB", "Awesome Lime",     "New",       4100,  5600,  2, d(2024,12,9),  "Sold",     ""),
        ("Xiaomi",  "Redmi Note 12",    33, "256GB", "Onyx Grey",        "New",       2500,  3500,  3, d(2024,12,10), "Sold",     ""),
        ("Apple",   "iPhone 12",        34, "128GB", "Purple",           "Good",      7500,  10000, 4, d(2024,12,12), "Sold",     ""),
        ("Samsung", "Galaxy S22 Ultra", 35, "256GB", "Phantom Black",    "Excellent", 13500, 18500, 2, d(2024,12,14), "Sold",     ""),
        ("Apple",   "iPhone 14 Pro Max",36, "256GB", "Gold",             "Excellent", 20000, 27000, 1, d(2024,12,15), "Sold",     ""),
        ("Apple",   "iPhone SE 2022",   37, "128GB", "Midnight",         "New",       6800,  9200,  1, d(2024,12,17), "Sold",     ""),
        ("Samsung", "Galaxy A34",       38, "64GB",  "Awesome Peach",    "New",       2900,  4000,  2, d(2024,12,18), "Sold",     ""),
        ("Huawei",  "P40 Lite",         39, "128GB", "Sakura Pink",      "Good",      2500,  3500,  4, d(2024,12,20), "Sold",     ""),
        # Jan 2025
        ("Apple",   "iPhone 15 Pro",    40, "256GB", "Natural Titanium", "New",       25000, 33000, 1, d(2025,1,6),   "Sold",     ""),
        ("Samsung", "Galaxy S24+",      41, "256GB", "Marble Grey",      "New",       19000, 25500, 2, d(2025,1,7),   "Sold",     ""),
        ("Apple",   "iPhone 13",        42, "128GB", "Blue",             "Good",      9000,  12500, 4, d(2025,1,9),   "Sold",     ""),
        ("Samsung", "Galaxy A54",       43, "256GB", "Awesome Graphite", "New",       4600,  6200,  2, d(2025,1,10),  "Sold",     ""),
        ("Xiaomi",  "Redmi Note 13",    44, "256GB", "Arctic White",     "New",       3200,  4500,  3, d(2025,1,13),  "Sold",     ""),
        ("Apple",   "iPhone 12",        45, "64GB",  "Green",            "Fair",      5800,  7800,  4, d(2025,1,15),  "Sold",     "Cracked back glass — priced accordingly"),
        ("Samsung", "Galaxy S23 FE",    46, "128GB", "Graphite",         "New",       8500,  11500, 2, d(2025,1,17),  "Sold",     ""),
        ("Huawei",  "P30 Pro",          47, "128GB", "Aurora",           "Good",      4500,  6200,  4, d(2025,1,20),  "Sold",     ""),
        # Feb 2025
        ("Apple",   "iPhone 14",        48, "128GB", "Starlight",        "Good",      11500, 15500, 1, d(2025,2,3),   "Sold",     ""),
        ("Samsung", "Galaxy A25",       49, "128GB", "Blue",             "New",       2800,  3900,  2, d(2025,2,5),   "Sold",     ""),
        ("Apple",   "iPhone 13 mini",   50, "128GB", "Midnight",         "Good",      7500,  10200, 4, d(2025,2,8),   "Sold",     ""),
        ("Xiaomi",  "Poco M6 Pro",      51, "256GB", "Black",            "New",       2900,  4100,  3, d(2025,2,10),  "Sold",     ""),
        ("Samsung", "Galaxy S22",       52, "128GB", "Bora Purple",      "Excellent", 8000,  11000, 2, d(2025,2,14),  "Sold",     "Valentine's Day sale"),
        ("Apple",   "iPhone 15",        53, "128GB", "Yellow",           "New",       19500, 26000, 1, d(2025,2,17),  "Sold",     ""),
        # Mar 2025 — current stock (mix sold and in stock)
        ("Apple",   "iPhone 15 Pro",    54, "128GB", "Black Titanium",   "New",       24500, 32000, 1, d(2025,3,3),   "In Stock", ""),
        ("Apple",   "iPhone 14 Pro",    55, "128GB", "Space Black",      "Excellent", 16500, 22000, 1, d(2025,3,3),   "In Stock", ""),
        ("Samsung", "Galaxy S24",       56, "256GB", "Onyx Black",       "New",       17500, 23000, 2, d(2025,3,5),   "Sold",     ""),
        ("Apple",   "iPhone 13",        57, "128GB", "Green",            "Good",      9000,  12500, 4, d(2025,3,5),   "In Stock", ""),
        ("Samsung", "Galaxy A55",       58, "128GB", "Awesome Navy",     "New",       5200,  7000,  2, d(2025,3,7),   "In Stock", ""),
        ("Samsung", "Galaxy A55",       59, "256GB", "Awesome Iceblue",  "New",       5800,  7800,  2, d(2025,3,7),   "In Stock", ""),
        ("Xiaomi",  "Redmi Note 13",    60, "128GB", "Fusion Black",     "New",       2900,  4000,  3, d(2025,3,8),   "In Stock", ""),
        ("Apple",   "iPhone 12",        61, "128GB", "Blue",             "Good",      7200,  9800,  4, d(2025,3,8),   "In Stock", ""),
        ("Samsung", "Galaxy S23 FE",    62, "256GB", "Mint",             "New",       9000,  12000, 2, d(2025,3,10),  "In Stock", ""),
        ("Huawei",  "Nova 11",          63, "256GB", "Black",            "New",       4500,  6200,  3, d(2025,3,10),  "In Stock", ""),
        ("Apple",   "iPhone 11",        64, "64GB",  "White",            "Fair",      4500,  6200,  4, d(2025,3,11),  "In Stock", "Battery at 75%"),
        ("Samsung", "Galaxy A34",       65, "128GB", "Silver",           "New",       3100,  4300,  2, d(2025,3,11),  "In Stock", ""),
        ("Xiaomi",  "Poco X6 Pro",      66, "256GB", "Black",            "New",       4800,  6500,  3, d(2025,3,12),  "In Stock", ""),
        ("Apple",   "iPhone 14",        67, "256GB", "Purple",           "Excellent", 13000, 17500, 1, d(2025,3,12),  "In Stock", ""),
        ("Samsung", "Galaxy S24 Ultra", 68, "256GB", "Titanium Black",   "New",       29000, 38000, 2, d(2025,3,12),  "In Stock", "Flagship — top shelf"),
        ("Apple",   "iPhone 15 Plus",   69, "256GB", "Green",            "New",       22000, 29500, 1, d(2025,3,12),  "In Stock", ""),
        ("Xiaomi",  "Redmi 12",         70, "128GB", "Moonstone Silver", "New",       1900,  2700,  3, d(2025,3,12),  "In Stock", ""),
        ("Huawei",  "P50 Lite",         71, "128GB", "Black",            "Good",      3800,  5200,  4, d(2025,3,12),  "In Stock", ""),
        ("Samsung", "Galaxy A15",       72, "128GB", "Blue",             "New",       2100,  3000,  2, d(2025,3,12),  "In Stock", ""),
        ("Apple",   "iPhone 13 Pro",    73, "128GB", "Alpine Green",     "Good",      13000, 17500, 4, d(2025,3,12),  "In Stock", "Minor wear on sides"),
    ]

    stock_ids = {}
    for p in phones_data:
        brand, model, seed, storage, colour, cond, buy, sell, sup, dp, status, notes = p
        r = conn.execute(
            "INSERT INTO stock (brand,model,imei,storage,colour,condition,buy_price,sell_price,status,supplier_id,date_purchased,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (brand, model, make_imei(seed), storage, colour, cond, buy, sell, status, sup, dp, notes)
        )
        stock_ids[seed] = r.lastrowid
    conn.commit()

    # ── SALES ─────────────────────────────────────────────────────────────
    sales_data = [
        # seed, sell_price, platform, buyer_name, buyer_phone, date, notes
        # Oct 2024
        (1,  13000, "Walk-in",  "Lerato Mokoena",      "082 312 4455", d(2024,10,6),  ""),
        (2,  7000,  "Facebook", "David van Wyk",        "083 221 7788", d(2024,10,8),  "Picked up same day"),
        (3,  5600,  "Walk-in",  "Nomsa Dlamini",        "076 445 6677", d(2024,10,9),  ""),
        (4,  4100,  "WhatsApp", "Sipho Mahlangu",       "071 334 5566", d(2024,10,11), ""),
        (5,  3000,  "Gumtree",  "Ahmed Patel",          "073 556 7788", d(2024,10,14), "Paid cash"),
        (6,  9200,  "Walk-in",  "Zandile Khumalo",      "084 112 2233", d(2024,10,16), ""),
        (7,  11200, "Facebook", "Pieter de Villiers",   "082 667 8899", d(2024,10,19), "Negotiated R300 off"),
        (8,  2700,  "Walk-in",  "Precious Sithole",     "079 998 1122", d(2024,10,22), ""),
        (9,  8500,  "WhatsApp", "Farouk Hendricks",     "072 443 5566", d(2024,10,24), ""),
        (10, 2200,  "Facebook", "Thandi Nkosi",         "083 778 9900", d(2024,10,26), "Sold as-is"),
        (11, 2000,  "Gumtree",  "Marco Ferreira",       "076 889 0011", d(2024,10,28), ""),
        (12, 15800, "Walk-in",  "Kefilwe Molefe",       "082 001 2233", d(2024,10,31), ""),
        # Nov 2024
        (13, 19200, "Walk-in",  "Rethabile Mosia",      "074 223 3344", d(2024,11,4),  ""),
        (14, 14800, "Facebook", "Brandon Swanepoel",    "083 334 4455", d(2024,11,7),  ""),
        (15, 5600,  "Walk-in",  "Ayanda Cele",          "071 445 5566", d(2024,11,9),  ""),
        (16, 5000,  "WhatsApp", "Tanvir Osman",         "076 556 6677", d(2024,11,11), ""),
        (17, 7800,  "Gumtree",  "Cynthia Botha",        "082 667 7788", d(2024,11,14), "Battery warning given to buyer"),
        (18, 2600,  "Walk-in",  "Lwazi Zulu",           "079 778 8899", d(2024,11,16), ""),
        (19, 3000,  "Facebook", "Samantha du Plessis",  "072 889 9900", d(2024,11,18), ""),
        (20, 10200, "Walk-in",  "Nkosinathi Ndlovu",    "083 990 0011", d(2024,11,21), "Advised on battery condition"),
        (21, 8000,  "WhatsApp", "Priya Govender",       "074 001 1122", d(2024,11,23), ""),
        (22, 2900,  "Gumtree",  "Deon Kruger",          "082 112 2233", d(2024,11,25), ""),
        (23, 17800, "Walk-in",  "Mpho Ramokgopa",       "071 223 3344", d(2024,11,27), ""),
        (24, 7300,  "Facebook", "Jessica van der Berg", "083 334 4455", d(2024,11,29), ""),
        # Dec 2024
        (25, 22000, "Walk-in",  "Tshepiso Modise",      "076 445 5566", d(2024,12,4),  ""),
        (26, 25500, "Walk-in",  "Yusuf Adams",          "082 556 6677", d(2024,12,6),  "Christmas gift for daughter"),
        (27, 25800, "WhatsApp", "Anele Mthembu",        "079 667 7788", d(2024,12,8),  "Christmas gift"),
        (28, 22800, "Walk-in",  "Riaan Botha",          "073 778 8899", d(2024,12,10), ""),
        (29, 14300, "Facebook", "Nobuhle Khumalo",      "082 889 9900", d(2024,12,12), ""),
        (30, 12600, "Walk-in",  "Grant Williamson",     "071 990 0011", d(2024,12,14), ""),
        (31, 13800, "Walk-in",  "Zanele Mokoena",       "083 001 1122", d(2024,12,15), ""),
        (32, 5500,  "WhatsApp", "Imraan Cassim",        "074 112 2233", d(2024,12,16), ""),
        (33, 3400,  "Gumtree",  "Karabo Sithole",       "082 223 3344", d(2024,12,17), ""),
        (34, 9800,  "Walk-in",  "Christo Venter",       "071 334 4455", d(2024,12,18), ""),
        (35, 18200, "Facebook", "Lehlohonolo Mosia",    "083 445 5566", d(2024,12,19), ""),
        (36, 26500, "Walk-in",  "Aisha Mahomed",        "076 556 6677", d(2024,12,20), "Christmas present — paid in full"),
        (37, 9000,  "Walk-in",  "Stephan Fourie",       "082 667 7788", d(2024,12,21), ""),
        (38, 3900,  "WhatsApp", "Bongiwe Dlamini",      "079 778 8899", d(2024,12,22), ""),
        (39, 3400,  "Facebook", "Thabo Mthembu",        "073 889 9900", d(2024,12,23), ""),
        # Jan 2025
        (40, 32500, "Walk-in",  "Lungelo Nkosi",        "082 990 0011", d(2025,1,8),   "New year upgrade"),
        (41, 25000, "WhatsApp", "Palesa Molefe",        "071 001 1122", d(2025,1,10),  ""),
        (42, 12200, "Facebook", "Werner du Toit",       "083 112 2233", d(2025,1,13),  ""),
        (43, 6000,  "Walk-in",  "Sifiso Shabalala",     "074 223 3344", d(2025,1,16),  ""),
        (44, 4400,  "Gumtree",  "Fatima Osman",         "082 334 4455", d(2025,1,18),  ""),
        (45, 7600,  "Facebook", "Gareth Smit",          "071 445 5566", d(2025,1,22),  "Sold as-is — cracked back"),
        (46, 11200, "Walk-in",  "Kemi Adeyemi",         "083 556 6677", d(2025,1,24),  ""),
        (47, 6000,  "WhatsApp", "Nomthandazo Cele",     "076 667 7788", d(2025,1,27),  ""),
        # Feb 2025
        (48, 15200, "Walk-in",  "Siphamandla Zulu",     "082 778 8899", d(2025,2,5),   ""),
        (49, 3800,  "Facebook", "Anastasia Botha",      "079 889 9900", d(2025,2,7),   ""),
        (50, 10000, "WhatsApp", "Kabelo Phiri",         "073 990 0011", d(2025,2,11),  ""),
        (51, 4000,  "Gumtree",  "Hashim Docrat",        "082 001 1122", d(2025,2,13),  ""),
        (52, 10800, "Walk-in",  "Liezel Steenkamp",     "071 112 2233", d(2025,2,17),  "Valentine gift for wife"),
        (53, 25800, "WhatsApp", "Ndaba Mhlongo",        "083 223 3344", d(2025,2,24),  ""),
        # Mar 2025
        (56, 22800, "Walk-in",  "Refilwe Kgosana",      "074 334 4455", d(2025,3,9),   ""),
    ]

    for sale in sales_data:
        seed, sell, platform, buyer, phone, dt, notes = sale
        sid = stock_ids[seed]
        conn.execute(
            "INSERT INTO sales (stock_id,sell_price,platform,buyer_name,buyer_phone,sale_date,notes) VALUES (?,?,?,?,?,?,?)",
            (sid, sell, platform, buyer, phone, dt, notes)
        )
        conn.execute("UPDATE stock SET status='Sold' WHERE id=?", (sid,))
    conn.commit()

    # ── REPAIRS ───────────────────────────────────────────────────────────
    repairs_data = [
        # stock_seed, device_name, imei, issue, tech, cost, status, date_in, date_out, customer, cust_phone, notes
        # Oct 2024
        (None, "iPhone XS",        "352011100001111", "Cracked screen replacement",          "Mike", 950,  "Done",        d(2024,10,7),  d(2024,10,9),  "Thandeka Moyo",    "082 111 0001", "OEM screen used"),
        (None, "Samsung A12",      None,              "Battery replacement",                  "Mike", 350,  "Done",        d(2024,10,14), d(2024,10,15), "Susan Khumalo",    "083 222 0002", ""),
        (None, "iPhone 8",         "352011100002222", "Charging port repair",                 "Mike", 450,  "Done",        d(2024,10,21), d(2024,10,23), "Wandile Dube",     "076 333 0003", ""),
        # Nov 2024
        (None, "Huawei Y6",        None,              "Screen replacement",                   "Mike", 400,  "Done",        d(2024,11,4),  d(2024,11,6),  "Gerhard Mostert",  "082 444 0004", ""),
        (None, "iPhone 7",         "352011100003333", "Water damage — not repairable",        "Mike", 0,    "Cancelled",   d(2024,11,11), d(2024,11,12), "Mpho Nkosi",       "071 555 0005", "Advised unrepairable. No charge."),
        (None, "Samsung S10",      "352011100004444", "Back glass replacement",               "Mike", 600,  "Done",        d(2024,11,18), d(2024,11,20), "Ruan de Wet",      "083 666 0006", ""),
        (None, "iPhone XR",        "352011100005555", "Battery replacement",                  "Mike", 850,  "Done",        d(2024,11,25), d(2024,11,27), "Ntombi Shabalala", "074 777 0007", "Genuine Apple battery"),
        # Dec 2024
        (None, "Xiaomi Redmi 9",   None,              "Charging port + screen combo repair",  "Mike", 700,  "Done",        d(2024,12,3),  d(2024,12,5),  "Faizel Latief",    "082 888 0008", ""),
        (None, "iPhone 11",        "352011100006666", "Cracked screen replacement",           "Mike", 1100, "Done",        d(2024,12,9),  d(2024,12,11), "Bonolo Sithole",   "079 999 0009", "Aftermarket screen"),
        (None, "Samsung A51",      None,              "Liquid damage — motherboard cleaned",  "Mike", 800,  "Done",        d(2024,12,16), d(2024,12,19), "Helena van Zyl",   "073 000 0010", "Warned customer about future issues"),
        (None, "iPhone SE 2020",   "352011100007777", "Home button repair",                   "Mike", 500,  "Done",        d(2024,12,22), d(2024,12,24), "Kobus Pretorius",  "082 111 0011", "Christmas rush"),
        # Jan 2025
        (None, "Huawei P20 Pro",   "352011100008888", "Screen replacement",                   "Mike", 750,  "Done",        d(2025,1,8),   d(2025,1,10),  "Zintle Mbeki",     "071 222 0012", ""),
        (None, "iPhone 12",        "352011100009999", "Battery replacement",                  "Mike", 900,  "Done",        d(2025,1,14),  d(2025,1,16),  "Trevor Smit",      "083 333 0013", "Genuine Apple battery"),
        (None, "Samsung S21",      "352011100010000", "Cracked screen replacement",           "Mike", 1400, "Done",        d(2025,1,20),  d(2025,1,22),  "Amahle Dlamini",   "074 444 0014", ""),
        (None, "iPhone XS Max",    "352011100011111", "Charging port repair",                 "Mike", 650,  "Done",        d(2025,1,27),  d(2025,1,29),  "Christo Nel",      "082 555 0015", ""),
        # Feb 2025
        (None, "Oppo A74",         None,              "Screen replacement",                   "Mike", 550,  "Done",        d(2025,2,4),   d(2025,2,6),   "Lungile Nzama",    "071 666 0016", ""),
        (None, "iPhone 11 Pro",    "352011100012222", "Battery + screen replacement combo",   "Mike", 1650, "Done",        d(2025,2,10),  d(2025,2,13),  "Pieter Coetzer",   "083 777 0017", "Double job — good margin"),
        (None, "Samsung A52",      None,              "Charging port repair",                 "Mike", 450,  "Done",        d(2025,2,17),  d(2025,2,19),  "Brenda Kgomotso",  "074 888 0018", ""),
        (None, "iPhone 13",        "352011100013333", "Cracked screen replacement",           "Mike", 1200, "Done",        d(2025,2,24),  d(2025,2,26),  "Ryan Jacobs",      "082 999 0019", "OEM screen"),
        # Mar 2025
        (None, "Xiaomi Note 11",   None,              "Back glass replacement",               "Mike", 400,  "Done",        d(2025,3,3),   d(2025,3,5),   "Nokwanda Mthembu", "071 000 0020", ""),
        (None, "iPhone 12 Pro",    "352011100014444", "Battery replacement",                  "Mike", 950,  "In Progress", d(2025,3,8),   None,          "Sandile Mokoena",  "083 111 0021", "Battery on order from iRepair Wholesale"),
        (None, "Samsung S22",      "352011100015555", "Cracked screen replacement",           "Mike", 1500, "In Progress", d(2025,3,10),  None,          "Lara Venter",      "074 222 0022", "Screen arriving tomorrow"),
        (None, "iPhone 14",        "352011100016666", "Charging port not working",            "Mike", 750,  "Pending",     d(2025,3,11),  None,          "Kabelo Mosia",     "082 333 0023", "Awaiting assessment"),
        (None, "Huawei P30",       "352011100017777", "Screen replacement",                   "Mike", 800,  "Pending",     d(2025,3,12),  None,          "Yolandi Fourie",   "071 444 0024", "Dropped off this morning"),
    ]

    for r in repairs_data:
        stock_seed, device, rimei, issue, tech, cost, status, date_in, date_out, customer, cust_phone, notes = r
        stock_id = stock_ids.get(stock_seed) if stock_seed else None
        conn.execute(
            "INSERT INTO repairs (stock_id,device_name,imei,issue,technician,repair_cost,status,date_received,date_completed,customer_name,customer_phone,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (stock_id, device, rimei, issue, tech, cost, status, date_in, date_out, customer, cust_phone, notes)
        )
    conn.commit()

    # ── EXPENSES ──────────────────────────────────────────────────────────
    expenses_data = [
        # Oct 2024
        ("Rent",        "Shop rental — October 2024",                   4500, d(2024,10,1)),
        ("Electricity", "Electricity — October 2024",                   780,  d(2024,10,2)),
        ("Transport",   "Supplier pickup — TechSource Sandton",         320,  d(2024,10,3)),
        ("Transport",   "Supplier pickup — MobileWorld Rosebank",       180,  d(2024,10,5)),
        ("Marketing",   "Facebook Marketplace boost — October",         300,  d(2024,10,6)),
        ("Tools",       "Precision screwdriver set",                    420,  d(2024,10,8)),
        ("Other",       "Plastic bags and bubble wrap",                 95,   d(2024,10,10)),
        ("Transport",   "Courier — online sale delivery",               150,  d(2024,10,14)),
        ("Marketing",   "Gumtree featured listing — October",           199,  d(2024,10,15)),
        ("Other",       "Cleaning supplies for shop",                   85,   d(2024,10,20)),
        # Nov 2024
        ("Rent",        "Shop rental — November 2024",                  4500, d(2024,11,1)),
        ("Electricity", "Electricity — November 2024",                  820,  d(2024,11,2)),
        ("Transport",   "Supplier pickup — TechSource Sandton",         320,  d(2024,11,5)),
        ("Marketing",   "Facebook Marketplace boost — November",        300,  d(2024,11,6)),
        ("Tools",       "Screen replacement UV lamp",                   850,  d(2024,11,8)),
        ("Transport",   "Courier — 3 online sales",                     450,  d(2024,11,12)),
        ("Marketing",   "Gumtree featured listing — November",          199,  d(2024,11,15)),
        ("Tools",       "Screen protector stock (50 pack)",             380,  d(2024,11,18)),
        ("Other",       "Repair parts — assorted batteries",            650,  d(2024,11,20)),
        ("Other",       "Packaging and cellotape",                      120,  d(2024,11,25)),
        # Dec 2024
        ("Rent",        "Shop rental — December 2024",                  4500, d(2024,12,1)),
        ("Electricity", "Electricity — December 2024",                  950,  d(2024,12,2)),
        ("Transport",   "Supplier pickup — TechSource (Christmas stock)",480, d(2024,12,3)),
        ("Transport",   "Supplier pickup — MobileWorld (Christmas stock)",280,d(2024,12,3)),
        ("Marketing",   "Facebook ads — December Christmas campaign",   800,  d(2024,12,4)),
        ("Marketing",   "Gumtree featured listing — December",          199,  d(2024,12,5)),
        ("Marketing",   "OLX featured listing — December",              150,  d(2024,12,5)),
        ("Tools",       "Display stand and shelf units",                1200, d(2024,12,7)),
        ("Other",       "Gift wrapping paper and ribbon",               220,  d(2024,12,8)),
        ("Other",       "Extra packaging for Christmas orders",         180,  d(2024,12,10)),
        ("Transport",   "Courier — 5 online Christmas deliveries",      750,  d(2024,12,16)),
        ("Other",       "Screen protectors for Christmas bundles",      340,  d(2024,12,18)),
        # Jan 2025
        ("Rent",        "Shop rental — January 2025",                   4500, d(2025,1,1)),
        ("Electricity", "Electricity — January 2025",                   710,  d(2025,1,2)),
        ("Transport",   "Supplier pickup — TechSource Sandton",         320,  d(2025,1,6)),
        ("Transport",   "Supplier pickup — DropShip Direct delivery",   180,  d(2025,1,7)),
        ("Marketing",   "Facebook Marketplace boost — January",         300,  d(2025,1,8)),
        ("Tools",       "Replacement suction cups and spudgers",        280,  d(2025,1,10)),
        ("Other",       "Repair parts — iPhone batteries x5",           750,  d(2025,1,13)),
        ("Marketing",   "Gumtree featured listing — January",           199,  d(2025,1,15)),
        ("Transport",   "Courier — online sales",                       300,  d(2025,1,20)),
        ("Other",       "Phone cases and accessories for resale",       480,  d(2025,1,22)),
        # Feb 2025
        ("Rent",        "Shop rental — February 2025",                  4500, d(2025,2,1)),
        ("Electricity", "Electricity — February 2025",                  760,  d(2025,2,2)),
        ("Transport",   "Supplier pickup — MobileWorld Rosebank",       180,  d(2025,2,5)),
        ("Marketing",   "Facebook ads — Valentine's Day campaign",      500,  d(2025,2,7)),
        ("Marketing",   "Gumtree featured listing — February",          199,  d(2025,2,10)),
        ("Other",       "Repair parts — Samsung screens x2",            1100, d(2025,2,12)),
        ("Transport",   "Courier — online sales",                       250,  d(2025,2,17)),
        ("Tools",       "Heat gun for back glass repairs",              650,  d(2025,2,20)),
        ("Other",       "Assorted phone cases for resale",              620,  d(2025,2,24)),
        # Mar 2025
        ("Rent",        "Shop rental — March 2025",                     4500, d(2025,3,1)),
        ("Electricity", "Electricity — March 2025",                     790,  d(2025,3,2)),
        ("Transport",   "Supplier pickup — TechSource Sandton",         320,  d(2025,3,3)),
        ("Transport",   "Supplier pickup — MobileWorld (A55 stock)",    280,  d(2025,3,5)),
        ("Transport",   "Supplier pickup — DropShip Direct",            180,  d(2025,3,8)),
        ("Marketing",   "Facebook Marketplace boost — March",           300,  d(2025,3,9)),
        ("Marketing",   "Gumtree featured listing — March",             199,  d(2025,3,10)),
        ("Other",       "Repair parts — assorted charging ports",       480,  d(2025,3,11)),
        ("Tools",       "Anti-static wrist straps x3",                  180,  d(2025,3,12)),
    ]

    for e in expenses_data:
        cat, desc, amount, dt = e
        conn.execute("INSERT INTO expenses (category,description,amount,date) VALUES (?,?,?,?)",
                     (cat, desc, amount, dt))
    conn.commit()
    conn.close()

    print(f"Seed complete:")
    print(f"  {len(phones_data)} phones in stock history")
    print(f"  {len(sales_data)} sales transactions")
    print(f"  {len(repairs_data)} repair jobs (20 done, 2 in progress, 2 pending)")
    print(f"  {len(expenses_data)} expense records across 6 months")


if __name__ == "__main__":
    create_tables()
    seed_data()
    print("Database ready at data/stock.db")
