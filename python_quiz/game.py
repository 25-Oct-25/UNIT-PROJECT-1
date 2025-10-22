from typing import List, Dict
import time
from .utils import now, seconds
from .messages import finalize_message
from .style import color_level_tag, colored, OK_CLR, WARN_CLR, TITLE_CLR
from .feedback import build_development_feedback


def ask_question_mcq(q_data: Dict[str, str]):
    """Ask an MCQ question (A/B/C/D) and return (False or correct, elapsed)."""
    start = time.time()

    # Show question and options
    print(colored(f"\n{q_data['q']}", TITLE_CLR))
    options = q_data.get("options", [])
    letters = ["A", "B", "C", "D"]

    for i, opt in enumerate(options):
        print(f"  {letters[i]}. {opt}")

    # Get player's answer
    ans = input(colored("Your choice (A/B/C/D): ", OK_CLR)).strip().upper()
    end = time.time()
    elapsed = end - start

    if ans not in letters:
        print(colored("Invalid choice! Counted as wrong.\n", WARN_CLR))
        return False, elapsed

    correct = q_data["answer"].strip().upper() == ans
    if correct:
        print(colored("✅ Correct!\n", OK_CLR))
    else:
        correct_ans = q_data["answer"]
        print(colored(f"❌ Wrong! Correct answer: {correct_ans}\n", WARN_CLR))

    return correct, elapsed


def run_round(player_name: str, questions: List[Dict[str, str]]):
    """
    Run a player's round with MCQ questions.
    Each question contains 'q', 'options', 'answer', 'level'.
    Returns: (score, avg_time, label, message, dev_plan)
    """
    total_qs = len(questions)
    correct = 0
    total_time = 0.0
    wrong_qs = []
    answered = 0

    print(colored(f"\n{player_name} — your turn! You have {total_qs} questions.\n", OK_CLR))

    # Readiness gate
    while True:
        ans = input(colored(f"{player_name}, are you ready for the challenge? (yes/no): ", OK_CLR)).strip().lower()
        if ans in ("yes", "y"):
            break
        if ans in ("no", "n"):
            print(colored("Why not? You’ve got this. Type 'start' to begin.", WARN_CLR))
            go = input(colored("Type exactly 'start': ", OK_CLR)).strip().lower()
            if go != "start":
                print(colored("No escape… you reached 'start'. Beginning now.", WARN_CLR))
            break
        print(colored("Please enter 'yes' or 'no'.", WARN_CLR))

    # Loop over questions
    for i, q in enumerate(questions, 1):
        lvl = q["level"].capitalize()
        lvl_clr = color_level_tag(lvl)
        print(colored(f"\n[{lvl}] Question {i}/{total_qs}", lvl_clr))
        is_correct, elapsed = ask_question_mcq(q)
        total_time += elapsed
        answered += 1
        if is_correct:
            correct += 1
        else:
            wrong_qs.append(q)

    # Calculate results
    total_q = max(answered, 1)
    score = round((correct / total_q) * 100, 2)
    avg_time = round(total_time / total_q, 3)

    if score >= 90:
        label = "Excellent"
    elif score >= 70:
        label = "Fast Thinker"
    else:
        label = "Needs Practice"

    message = finalize_message(score, avg_time)
    dev_plan = build_development_feedback(wrong_qs, avg_time, score)

    print(colored(f"\n{player_name}'s Results:", TITLE_CLR))
    print(colored(f"Score: {score}% | Average Time: {avg_time:.2f}s | Result: {label}", OK_CLR))
    print(colored("Message: ", OK_CLR) + message)
    print()
    print(dev_plan)
    print(colored(f"\nEnd of your turn, {player_name}.", OK_CLR))

    return score, avg_time, label, message, dev_plan
