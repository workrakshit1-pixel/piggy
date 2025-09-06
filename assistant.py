# src/piggy/assistant.py
import re
from typing import Tuple, Optional, List
from . import crud, schemas, models
import os
from src import crud, schemas, models



def _format_money(amount: float) -> str:
    return f"{amount:.2f}"

def _simple_reply_template(action: str, success: bool, data: Optional[List[models.Expense]] = None) -> Tuple[str, bool, Optional[List[models.Expense]]]:
    # Return a short humorous reply
    if action == "add":
        if success:
            return ("Done — Piggy accepted the coin 🐷💰. Want to throw another?", True, None)
        else:
            return ("Whoops — Piggy refused the coin. Try again?", False, None)
    if action == "delete":
        if success:
            return ("Trash! The expense is gone. Piggy cleaned it out. 🧹", True, None)
        else:
            return ("I couldn't find that expense. Maybe it hid under the couch?", False, None)
    if action == "list":
        if data and len(data) > 0:
            return ("Here's what Piggy found — lookin' good (and spendy):", True, data)
        else:
            return ("No expenses found. Piggy is hungry though.", True, [])
    if action == "total":
        return (f"All together, that's ₹{_format_money(data) if data is not None else '0.00'} — Piggy's getting heavy!", True, None)
    return ("Sorry, I didn't understand that. Try: add, delete, list, total, help.", False, None)

def parse_and_handle(message: str, manager: crud.ExpenseManager) -> Tuple[str, bool, Optional[List[models.Expense]]]:
    """
    Parse message using regex and call CRUD functions accordingly.
    Supports:
      - add 12.5 for lunch
      - add 200 grocery
      - delete 5    (expense id)
      - delete description: lunch
      - list
      - total
      - help
    Returns: (reply, success, optional payload)
    """
    text = message.strip().lower()

    # ADD intent: "add 12.50 for lunch" OR "add 200 grocery"
    add_match = re.match(r"^(add|deposit)\s+([0-9]+(?:\.[0-9]+)?)\s*(?:for|as|on)?\s*(.*)$", text)
    if add_match:
        amount = float(add_match.group(2))
        description = add_match.group(3).strip() or "misc"
        expense_in = schemas.ExpenseCreate(amount=amount, description=description)
        try:
            expense = manager.add_expense(expense_in)
            reply, success, payload = _simple_reply_template("add", True, None)
            # Optionally mention created id
            reply = f"{reply} (id={expense.id}, {expense.description} — {expense.amount:.2f})"
            return (reply, True, None)
        except Exception as e:
            return (f"Error saving expense: {e}", False, None)

    # DELETE by id: "delete 5"
    del_id_match = re.match(r"^(delete|remove)\s+([0-9]+)$", text)
    if del_id_match:
        expense_id = int(del_id_match.group(2))
        ok = manager.delete_expense(expense_id)
        reply, success, _ = _simple_reply_template("delete", ok)
        return (reply, success, None)

    # DELETE by description: "delete lunch" or "delete description: lunch"
    del_desc_match = re.match(r"^(delete|remove)\s+(?:description:)?\s*(.+)$", text)
    if del_desc_match:
        desc = del_desc_match.group(2).strip()
        # Find first matching expense with that description
        all_exp = manager.get_expenses(limit=1000)  # small scale
        target = None
        for e in all_exp:
            if desc in e.description.lower():
                target = e
                break
        if target:
            ok = manager.delete_expense(target.id)
            reply, success, _ = _simple_reply_template("delete", ok)
            if ok:
                reply = f"{reply} (deleted id={target.id}, {target.description} — {target.amount:.2f})"
            return (reply, success, None)
        else:
            return ("Couldn't find an expense with that description.", False, None)

    # LIST intent
    if text.startswith("list") or text in ("show", "expenses", "what did i spend"):
        items = manager.get_expenses(limit=100)
        reply, success, payload = _simple_reply_template("list", True, items)
        return (reply, success, items)

    # TOTAL intent
    if text.startswith("total") or text in ("balance", "how much", "how much did i spend"):
        t = manager.total()
        reply, success, _ = _simple_reply_template("total", True, t)
        return (reply, True, None)

    # HELP
    if text in ("help", "what can you do", "commands"):
        help_text = (
            "I'm Piggy 🐷. I can:\n"
            "- add <amount> [description]  e.g. 'add 12.5 lunch'\n"
            "- delete <id>                 e.g. 'delete 3'\n"
            "- delete <description>        e.g. 'delete lunch'\n"
            "- list                        show recent expenses\n"
            "- total                       show total spent\n"
        )
        return (help_text, True, None)

    return ("Sorry, I didn't get that. Try 'help' for commands.", False, None)
