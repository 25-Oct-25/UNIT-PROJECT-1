# 🎮 Time Arcade

**Time Arcade** is a command-line game hub where players can log in, play mini games, earn points, and unlock achievements.  
It includes both **user** and **admin** modes.

---

## 🧩 Features
- 👤 **User system** with login and registration  
- 🔐 **Admin dashboard** to view, edit, and manage users  
- 🕹️ **Mini games included:**
  - **Time Traveler** – explore historical events by entering a date  
  - **Escape Room** – solve puzzles before time runs out  
- 🏆 **Achievements** and score tracking  
- 💾 Data saved automatically in `data/users.json`  
- ⚠️ Error logging for debugging in `logs/error.log`

---

## 🚀 How to Run

1. Make sure you have **Python 3.8+** installed.  
2. Install required dependencies:
   ```bash
   pip install bcrypt
3. Run the admin setup once to create the first admin:
   ```bash
   python admin_setup.py
4. Start the game:
   ```bash
   python main.py

## 🧠 Game Modes

**👑 Admin**
- View users
- Edit or delete users
- Add achievements manually
- Play games and earn points
- Unlock achievements automatically
  
**👥 User**
- Register or log in
- Play games and earn points
- Unlock achievements automatically

## 📁 Project Structure
    ```bash
      TimeArcade/
      │
      ├── main.py                # Main program entry point
      ├── admin_setup.py         # Creates the first admin account
      │
      ├── data/
      │   └── users.json         # Stores user and admin data
      │
      ├── games/
      │   ├── time_traveler.py   # Historical time-travel game
      │   └── escape_room.py     # Puzzle-solving game
      │
      ├── users/
      │   ├── user.py            # User model and password handling
      │   └── admin.py           # Admin dashboard and tools
      │
      └── utils/
          ├── helpers.py         # Common helper functions
          ├── colors.py          # Color codes for CLI
          ├── art_assets.py      # ASCII art and logos

## 🧾 Notes

- Passwords are stored securely using bcrypt hashing.
- Admin username is reserved ("admin").
- All data is saved locally — no external servers required.
