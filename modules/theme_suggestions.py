import random

def suggest_theme(keyword):
    themes = ["Neon Night", "Vintage Chic", "Minimalist", "Tropical Sunset", "Futuristic"]
    return random.choice(themes) + f" ({keyword})"
