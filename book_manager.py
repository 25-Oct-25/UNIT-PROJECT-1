# book_manager.py

from bookstore_data import books_db, save_data
from datetime import datetime

def list_all_books():
    """Displays a list of all books available in the store."""
    if not books_db:
        print("No books currently available in the store.")
        return

    print("\n--- Our Available Books ---")
    for title, data in books_db.items():
        avg_rating = calculate_average_rating(title)
        rating_str = f" (Rating: {avg_rating:.1f}/5)" if avg_rating is not None else ""
        print(f"- {title} by {data['author']} (Genre: {data.get('genre', 'N/A')}, Price: ${data['price']:.2f}, Quantity: {data['quantity']}){rating_str}")
    print("---------------------------")

def get_book_details(book_title):
    """Displays detailed information about a specific book."""
    book = books_db.get(book_title)
    if book:
        print(f"\n--- Book Details: {book_title} ---")
        print(f"  Author: {book['author']}")
        print(f"  Description: {book['description']}")
        print(f"  Genre: {book.get('genre', 'N/A')}")
        print(f"  Price: ${book['price']:.2f}")
        print(f"  Available Quantity: {book['quantity']}")
        print(f"  ISBN: {book['isbn']}")
        
        # Display ratings and reviews
        print("\n  --- Ratings and Reviews ---")
        if book['reviews']:
            total_rating = 0
            for review in book['reviews']:
                print(f"    - User: {review['username']}, Rating: {review['rating']}/5")
                print(f"      Comment: {review['comment']}")
                print(f"      Date: {review['date']}")
                total_rating += review['rating']
            avg_rating = total_rating / len(book['reviews'])
            print(f"  Average Rating: {avg_rating:.1f}/5")
        else:
            print("  No ratings or reviews for this book yet.")
        print("---------------------------------")
        return True
    else:
        print(f"Sorry, the book '{book_title}' was not found.")
        return False

def search_books(query):
    """Searches for books by title, author, or genre."""
    results = []
    query_lower = query.lower()
    for title, data in books_db.items():
        if query_lower in title.lower() or \
           query_lower in data['author'].lower() or \
           query_lower in data.get('genre', '').lower():
            results.append((title, data))
    
    if results:
        print(f"\n--- Search Results for '{query}' ---")
        for title, data in results:
            avg_rating = calculate_average_rating(title)
            rating_str = f" (Rating: {avg_rating:.1f}/5)" if avg_rating is not None else ""
            print(f"- {title} by {data['author']} (Genre: {data.get('genre', 'N/A')}, Price: ${data['price']:.2f}, Quantity: {data['quantity']}){rating_str}")
        print("----------------------------")
    else:
        print(f"No books found matching '{query}'.")
    return results

def get_book_price(book_title):
    """Gets the price of a specific book."""
    book = books_db.get(book_title)
    if book:
        return book['price']
    return None

def get_book_quantity(book_title):
    """Gets the available quantity of a specific book."""
    book = books_db.get(book_title)
    if book:
        return book['quantity']
    return None

def update_book_quantity(book_title, quantity_change):
    """Updates the available quantity of a specific book."""
    book = books_db.get(book_title)
    if book:
        if book['quantity'] + quantity_change < 0:
            return False # Not enough stock for this change
        book['quantity'] += quantity_change
        save_data() # Save changes
        return True
    return False

def add_book(title, author, description, price, quantity, isbn, genre="N/A"):
    """Adds a new book to the store."""
    if title in books_db:
        print(f"The book '{title}' already exists.")
        return False
    books_db[title] = {
        "author": author,
        "description": description,
        "price": price,
        "quantity": quantity,
        "isbn": isbn,
        "genre": genre,
        "reviews": []
    }
    save_data() # Save changes
    print(f"Book '{title}' added successfully.")
    return True

def remove_book(title):
    """Removes a book from the store."""
    if title in books_db:
        del books_db[title]
        save_data() # Save changes
        print(f"Book '{title}' removed successfully.")
        return True
    else:
        print(f"The book '{title}' was not found.")
        return False

def add_book_review(username, book_title, rating, comment):
    """Adds a rating and review for a book."""
    book = books_db.get(book_title)
    if not book:
        print(f"The book '{book_title}' does not exist.")
        return False
    
    # Check if the user has purchased this book
    from bookstore_data import users_db, orders_db
    user_data = users_db.get(username)
    if not user_data:
        print("Error: User does not exist.")
        return False

    has_purchased = False
    for order_id in user_data["purchase_history"]:
        order = orders_db.get(order_id)
        if order and book_title in order["items"]:
            has_purchased = True
            break
    
    if not has_purchased:
        print(f"Sorry, you can only review '{book_title}' if you have purchased it.")
        return False

    # Check if the user has already reviewed this book
    for review in book['reviews']:
        if review['username'] == username:
            print(f"You have already reviewed '{book_title}'. You can modify your previous review.")
            # Here, we could add logic to modify the review instead of preventing it
            return False

    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            print("Rating must be a number between 1 and 5.")
            return False
    except ValueError:
        print("Rating must be a number.")
        return False

    review_data = {
        "username": username,
        "rating": rating,
        "comment": comment,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    book['reviews'].append(review_data)
    save_data() # Save changes
    print(f"Your review for '{book_title}' has been added successfully!")
    return True

def calculate_average_rating(book_title):
    """Calculates the average rating for a specific book."""
    book = books_db.get(book_title)
    if book and book['reviews']:
        total_rating = sum(review['rating'] for review in book['reviews'])
        return total_rating / len(book['reviews'])
    return None # No ratings

def filter_books_by_genre(genre):
    """Filters and displays books by genre."""
    results = []
    genre_lower = genre.lower()
    for title, data in books_db.items():
        if data.get('genre', '').lower() == genre_lower:
            results.append((title, data))
    
    if results:
        print(f"\n--- Books in Genre '{genre}' ---")
        for title, data in results:
            avg_rating = calculate_average_rating(title)
            rating_str = f" (Rating: {avg_rating:.1f}/5)" if avg_rating is not None else ""
            print(f"- {title} by {data['author']} (Price: ${data['price']:.2f}, Quantity: {data['quantity']}){rating_str}")
        print("----------------------------")
    else:
        print(f"No books found in genre '{genre}'.")
    return results

def get_available_genres():
    """Returns a list of all unique genres available in the store."""
    genres = set()
    for book_data in books_db.values():
        if 'genre' in book_data:
            genres.add(book_data['genre'])
    return sorted(list(genres))