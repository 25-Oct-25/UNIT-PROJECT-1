# bookstore_data.py

import json
import os

DATA_FILE = "bookstore_data.json"

# Default data if no file exists
default_books_db = {
    "The Lord of the Rings": {
        "author": "J.R.R. Tolkien",
        "description": "Epic fantasy novel.",
        "price": 25.00,
        "quantity": 10,
        "isbn": "978-0618260274",
        "genre": "Fantasy",
        "reviews": [] # {username, rating, comment, date}
    },
    "Pride and Prejudice": {
        "author": "Jane Austen",
        "description": "Romantic novel of manners.",
        "price": 15.50,
        "quantity": 15,
        "isbn": "978-0141439518",
        "genre": "Romance",
        "reviews": []
    },
    "1984": {
        "author": "George Orwell",
        "description": "Dystopian social science fiction novel.",
        "price": 12.00,
        "quantity": 8,
        "isbn": "978-0451524935",
        "genre": "Dystopian",
        "reviews": []
    },
    "To Kill a Mockingbird": {
        "author": "Harper Lee",
        "description": "Classic of modern American literature.",
        "price": 18.75,
        "quantity": 12,
        "isbn": "978-0446310789",
        "genre": "Classic",
        "reviews": []
    },
    "The Great Gatsby": {
        "author": "F. Scott Fitzgerald",
        "description": "Novel illustrating the Jazz Age.",
        "price": 14.00,
        "quantity": 7,
        "isbn": "978-0743273565",
        "genre": "Classic",
        "reviews": []
    }
}

default_users_db = {
    "customer1": {
        "password": "password123",
        "email": "customer1@example.com", # Added email field
        "address": {},
        "purchase_history": [],
        "cart": {}
    },
    "admin": {
        "password": "adminpassword",
        "email": "admin@example.com",
        "is_admin": True
    }
}

default_orders_db = {}

books_db = {}
users_db = {}
orders_db = {}
low_stock_threshold = 5 # Low stock alert threshold

def load_data():
    """Loads bookstore data from a JSON file."""
    global books_db, users_db, orders_db
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            books_db.update(data.get('books', {}))
            users_db.update(data.get('users', {}))
            orders_db.update(data.get('orders', {}))
    else:
        # If no file, use default data
        books_db.update(default_books_db)
        users_db.update(default_users_db)
        orders_db.update(default_orders_db)
        save_data() # Save default data for the first time

def save_data():
    """Saves bookstore data to a JSON file."""
    data = {
        'books': books_db,
        'users': users_db,
        'orders': orders_db
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Load data on module import
load_data()