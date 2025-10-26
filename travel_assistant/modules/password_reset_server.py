# modules/password_reset_server.py
from flask import Flask, request, render_template_string
import hashlib
import json
import os

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
RESET_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reset_links.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Password Reset</title>
  </head>
  <body>
    <h2>Reset Password for {{email}}</h2>
    <form method="post">
      <label>New Password (min 6 characters):</label><br>
      <input type="password" name="password" minlength="6" required>
      <br><br>
      <button type="submit">Reset Password</button>
    </form>
  </body>
</html>
"""

@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    email = request.args.get("email")
    token = request.args.get("token")

    if not email or not token:
        return "❌ Invalid or missing parameters."

    if not os.path.exists(RESET_FILE):
        return "❌ Reset token file not found."

    with open(RESET_FILE, "r", encoding="utf-8") as f:
        tokens = json.load(f)

    stored_email = tokens.get(token)
    if not stored_email or stored_email.lower() != email.lower():
        return "❌ Invalid or expired reset link."

    users = _load_users()

    if request.method == "POST":
        new_password = request.form["password"].strip()
        if len(new_password) < 6:
            return "⚠ Password too short."

        for u in users:
            if u["email"].lower() == email.lower():
                u["password"] = hash_password(new_password)
                _save_users(users)
                # delete token after use
                del tokens[token]
                with open(RESET_FILE, "w", encoding="utf-8") as f:
                    json.dump(tokens, f, indent=4)
                return "✅ Password reset successfully! You can now log in."

    return render_template_string(PAGE, email=email)

if __name__ == "__main__":
    print("🚀 Starting Flask password reset server...")
    app.run(debug=True)