## ✈ Travel Assistant CLI System

A full-featured Python project that runs entirely in the terminal, offering an interactive travel management experience for both flights and hotels — complete with secure login, password recovery via email, and modern visuals using the Rich library.

⸻

🧩 Core Features

🔐 Authentication System
	•	Create new accounts with input validation.
	•	Log in using either username or email.
	•	Password recovery via email only.
	•	The first registered user becomes the Admin automatically.
	•	All passwords are encrypted using SHA-256.

⸻

✈ Flights Module
	•	Search for flights using city names or airport codes.
	•	Select departure and return dates.
	•	Filter results by:
	•	💰 Price
	•	🛫 Airline
	•	⏱ Duration
	•	Display results in beautiful, colorized Rich tables.
	•	Option to confirm bookings directly within the CLI.

⸻

🏨 Hotels Module
	•	Realistic hotel data from Saudi and international cities.
	•	Search hotels by city and date range.
	•	Filter results by price category:
	•	💰 Cheap
	•	💼 Medium
	•	💎 Expensive
	•	Choose preferred currency (SAR / USD / EUR).
	•	View hotels in an elegant Rich table showing:
	•	Hotel name
	•	Category (Cheap / Medium / Expensive)
	•	Rating and star level ⭐
	•	Price per night with currency
	•	Check-in and check-out dates
	•	Ability to confirm and view bookings later.

⸻

📧 Password Reset
	•	When users forget their password, they enter their registered email.
	•	The system sends an email containing a unique reset link.
	•	Clicking the link opens a page to enter a new password.
	•	Each reset token can only be used once for added security.

⸻

🧾 Data Management
	•	All data stored locally inside the data/ directory.
	•	Files are auto-created if missing.
	•	Uses JSON for easy readability and updates.
	•	Data files include:
	•	users.json — User credentials
	•	bookings.json — Flight and hotel bookings
	•	reset_links.json — Password reset tokens

⸻

⚙ Folder Structure

travel_assistant/
│
├── main.py                     # Main entry point
├── modules/
│   ├── auth.py                 # Authentication and password recovery
│   ├── flights.py              # Flight management
│   ├── hotels.py               # Hotel management
│   └── amadeus_api.py          # Amadeus API integration (optional)
│
├── data/
│   ├── users.json              # Registered users
│   ├── bookings.json           # Booking records
│   └── reset_links.json        # Password reset tokens
│
├── .env                        # Contains secure email credentials
└── README.md                   # Project documentation


⸻

🧠 Technologies Used
	•	Python 3.10+
	•	Rich — For colorful tables and styled text
	•	smtplib — For sending emails
	•	dotenv — For managing environment variables
	•	hashlib — For password hashing
	•	JSON — For local data storage

⸻

🔒 Security
	•	All passwords hashed using SHA-256.
	•	Each password reset token is unique and one-time-use.
	•	No plaintext passwords stored anywhere.
	•	Secure Gmail SMTP integration for email operations.

