user_points = {}

def award_points(email, points):
    user_points[email] = user_points.get(email, 0) + points

def leaderboard():
    for u,p in sorted(user_points.items(), key=lambda x:x[1], reverse=True):
        print(f"{u}: {p} pts")
