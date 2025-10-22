# 🐍 Project Name: Python Challenge

---

## ⚙️ Requirements
Before running the project, make sure you have the following installed:
- Python 3.10 or higher
- Required libraries listed in requirements.txt

---

## ▶️ How to Run
1. Create a virtual environment  
   `python -m venv venv`
2. Activate the virtual environment  
   - On Windows (PowerShell): `venv\Scripts\activate`  
   - On Mac/Linux: `source venv/bin/activate`
3. Install all required libraries  
   `pip install -r requirements.txt`
4. Run the program  
   `python -m python_quiz.cli`
5. Follow the on-screen menus to play the quiz.

---

## 📖 Overview
**Python Challenge** is an interactive quiz game that runs entirely in the command line (CLI).  
It challenges players to test their Python knowledge, logic, and reaction speed in a fun and competitive way.

The game supports multiple players and uses AI to generate dynamic Python questions.  
If an internet connection or API key is not available, the game automatically switches to a **local question bank** (offline mode), ensuring it always runs smoothly.

Each round includes five color-coded questions across three difficulty levels — Easy 🟢, Medium 🟡, and Hard 🔴.  
After every round, each player receives a **personalized motivational message** and a **short development plan** based on their score and average response time.

All session results are saved automatically in **JSON** and **CSV** formats for tracking progress over time,  
and players can also generate a **PDF report** summarizing scores, rankings, and feedback at the end of each session.

---

## 👥 User Stories
As a Player, I can:
- Enter my name and play against others in **Single-level (turn-based)** mode — each player completes their round separately.  
- Answer 5 Python questions: 🟢2 Easy, 🟡2 Medium, and 🔴1 Hard.
- See my score, average time, and ranking.
- Receive a motivational message and personal development plan.
- Generate a PDF report after finishing.

As a Returning Player, I can:
- View the all-time leaderboard from previous sessions.
- Search for my previous results by name.
- Add, update, or delete players before starting.

---

## 🧩 Usage
When you run the program, the main menu appears:
1. Start Game  
2. Show All Players  
3. Player Info  
4. Exit  

- select `1` to start a new game session.  
- select `2` to display the all-time leaderboard of players.  
- select `3` to search for a specific player’s past performance.  
- select `4` to exit the program.  

After choosing Start Game, another menu appears before starting the round:
1. Add Player  
2. Update Player  
3. Delete Player  
4. No Change  

- select `1` to add a new player.  
- select `2` to rename a player.  
- select `3` to remove a player.  
- select `4` to continue and start the challenge.  

During the game, answer each question by typing A, B, C, or D.  
At the end, your score, average time, and feedback will be displayed.  
You will also be asked if you want to generate a PDF report or start another round.

---

## 👩‍💻 Developed by
**Maha Saud**  
*Tuwaiq Academy – Python Web Development Bootcamp.*
