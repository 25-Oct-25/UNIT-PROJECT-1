# transport.py
import random

class TransportMode:
    def __init__(self, name, base_time, cost, comfort):
        self.name = name
        self.base_time = base_time
        self.cost = cost
        self.comfort = comfort

    def calculate_time(self, traffic_multiplier=1, weather_multiplier=1):
        return self.base_time * traffic_multiplier * weather_multiplier

class TransportSystem:
    def __init__(self):
        self.modes = [
            TransportMode("Car", 20, 12, "High"),
            TransportMode("Metro", 30, 7, "Medium"),
            TransportMode("Bus", 45, 5, "Low"),
        ]

    def get_best_commute(self, preference="speed", weather="clear"):
        traffic_level = random.choice(["Low", "Moderate", "Heavy"])
        weather_multiplier_map = {"clear":1.0,"sandstorm":1.5,"hot":1.1}
        t_mult_map = {"Low":1.0,"Moderate":1.3,"Heavy":1.8}
        t_mult = t_mult_map[traffic_level]
        w_mult = weather_multiplier_map.get(weather.lower(), 1.0)

        best_score = -1
        best_candidate = None
        candidates = []

        for m in self.modes:
            est_time = m.calculate_time(t_mult, w_mult)
            if preference=="speed":
                score = 100/est_time
            elif preference=="cost":
                score = 50/m.cost
            elif preference=="comfort":
                score = {"Low":10,"Medium":20,"High":30}[m.comfort]
            else:
                score = 100/est_time

            candidate = {
                "mode": m.name,
                "time_min": round(est_time),
                "cost_sar": m.cost,
                "comfort": m.comfort,
                "score": round(score)
            }
            candidates.append(candidate)
            if score>best_score:
                best_score = score
                best_candidate = candidate

        points = max(0, int(best_score))
        return best_candidate, candidates, points, traffic_level
