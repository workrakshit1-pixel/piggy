# run.py
import random
import speech_recognition as sr
import pyttsx3
from sqlalchemy.orm import Session
from src import crud, Db, schemas
from word2number import w2n
import json

# ---------------- Voice Engine ---------------- #
engine = pyttsx3.init()
engine.setProperty("rate", 150)

def speak(text: str):
    print("Piggy:", text)
    engine.say(text)
    engine.runAndWait()

def listen() -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("Timeout: No speech detected.")
            speak("I didn’t hear anything. Can you say that again?")
            return ""  # return empty so main loop continues

    try:
        result = r.recognize_vosk(audio)
        data = json.loads(result)
        spoken_text = data.get("text", "").strip()
        print("You said:", spoken_text)
        return spoken_text.lower()
    except Exception as e:
        print("Error in listen():", e)
        return ""


# ---------------- Intent Detection ---------------- #
INTENTS = {
    "add expense": ["add", "record", "log", "new expense"],
    "list expenses": ["list", "show", "recent", "expenses"],
    "delete expense": ["delete", "remove", "erase", "drop"],
    "total": ["total", "sum", "overall", "how much"],
    "exit": ["exit", "quit", "stop", "goodbye"]
}

def detect_intent(spoken: str) -> str:
    for intent, keywords in INTENTS.items():
        for kw in keywords:
            if kw in spoken:
                return intent
    return ""

# ---------------- Fun Responses ---------------- #
JOKES = [
    "Remember, money saved is pizza earned!",
    "Tracking expenses: cheaper than therapy!",
    "I wish I had money… but I only have bytes.",
    "Your wallet just whispered: thank you!"
]

def random_joke():
    return random.choice(JOKES)

# ---------------- Main Assistant ---------------- #
def main():
    db: Session = Db.SessionLocal()
    manager = crud.ExpenseManager(db)

    speak("Hello! I am Piggy, your expense buddy. Ask me to add, list, delete, or total your expenses.")

    while True:
        command = listen()
        if not command.strip():
            continue

        intent = detect_intent(command)

        if intent == "add expense":
            try:
                speak("Got it! Let's add a new expense. How much did you spend?")
                amount_str = listen()
                try:
                    amount = w2n.word_to_num(amount_str)
                except ValueError:
                    amount = float(amount_str)

                speak("And what was it for?")
                description = listen()

                speak("Do you want to put it under a category, or just say skip?")
                category = listen()
                if "skip" in category:
                    category = None

                expense_in = schemas.ExpenseCreate(amount=amount, description=description, category=category)
                expense = manager.add_expense(expense_in)
                speak(f"Added {expense.amount} rupees for {expense.description}. {random_joke()}")
            except Exception as e:
                speak(f"Oops! Couldn’t add the expense: {str(e)}")

        elif intent == "list expenses":
            expenses = manager.get_expenses(limit=10)
            if not expenses:
                speak("No expenses found. Either you’re super frugal, or you forgot to log them!")
            else:
                speak("Here are your recent expenses:")
                for e in expenses:
                    cat_text = f" in {e.category}" if e.category else ""
                    speak(f"ID {e.id}: {e.amount} rupees for {e.description}{cat_text}")
                speak(random_joke())

        elif intent == "delete expense":
            try:
                speak("Sure. Tell me the expense ID you want me to delete.")
                exp_id_str = listen()
                try:
                    exp_id = w2n.word_to_num(exp_id_str)
                except ValueError:
                    exp_id = int(exp_id_str)

                if manager.delete_expense(exp_id):
                    speak(f"Expense {exp_id} deleted. One less worry in your wallet!")
                else:
                    speak(f"Expense {exp_id} doesn’t exist. Maybe it escaped already!")
            except Exception as e:
                speak(f"Failed to delete expense: {str(e)}")

        elif intent == "total":
            total = manager.total()
            speak(f"Your total expenses are {total} rupees. {random_joke()}")

        elif intent == "exit":
            speak("Goodbye! Don’t spend it all at once.")
            break
        elif intent == "thank you":
            speak("Not a problem! we are friends")
        else:
            speak("I can add, list, delete expenses or tell the total. Try one of those.")

    db.close()

if __name__ == "__main__":
    main()
