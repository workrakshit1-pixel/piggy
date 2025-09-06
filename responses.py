import random

def get_response(text):
    jokes = [
        "Piggy approves 🐷",
        "Oink! That’s recorded.",
        "Money, money, money 🤑",
        "Piggy says: budget wisely!"
    ]
    return f"{text} {random.choice(jokes)}"
