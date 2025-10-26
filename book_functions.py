import json
import os
import time

BOOK_FILE = "books.json"
USER_FILE = "users.json"
ADMIN_FILE = "admin_profit.json"

# ---------- JSON ----------
def load_json(file_path, default):
    if not os.path.exists(file_path):
        return default
    with open(file_path, "r") as f:
        return json.load(f)

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# ---------- BOOK FUNCTIONS ----------
def load_books():
    return load_json(BOOK_FILE, [])

def save_books(books):
    save_json(BOOK_FILE, books)

def add_book(title, author, price, category, district, seller):
    books = load_books()
    new_book = {
        "id": int(time.time() * 1000),
        "title": title,
        "author": author,
        "price": price,
        "category": category,
        "district": district,
        "seller": seller,
        "sold": False
    }
    books.append(new_book)
    save_books(books)

def edit_book(book_id, title, author, price, category, district):
    books = load_books()
    for b in books:
        if b["id"] == book_id:
            b.update({
                "title": title,
                "author": author,
                "price": price,
                "category": category,
                "district": district
            })
            break
    save_books(books)

def delete_book(book_id):
    books = [b for b in load_books() if b["id"] != book_id]
    save_books(books)

def search_books(keyword="", category="", district=""):
    books = load_books()
    results = []
    for b in books:
        # skip sold books
        if b.get("sold", False):
            continue
        if (keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()) and \
           (category.lower() in b["category"].lower() if category else True) and \
           (district.lower() in b["district"].lower() if district else True):
            results.append(b)
    return results

# ---------- USER FUNCTIONS ----------
def load_users():
    return load_json(USER_FILE, {})

def save_users(users):
    save_json(USER_FILE, users)

def register_user(username, password, role):
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": password, "role": role}
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return users[username]
    return None

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)

# ---------- ADMIN PROFIT ----------
def load_admin_profit():
    return load_json(ADMIN_FILE, {"total_profit": 0.0, "transactions": []})

def save_admin_profit(data):
    save_json(ADMIN_FILE, data)

def add_commission(price, book_title, seller, rate=0.10):
    profit_data = load_admin_profit()
    commission = round(price * rate, 2)
    profit_data["total_profit"] += commission
    profit_data["transactions"].append({
        "book": book_title,
        "seller": seller,
        "commission": commission
    })
    save_admin_profit(profit_data)
    return commission
