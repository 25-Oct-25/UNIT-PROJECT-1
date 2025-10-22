from typing import List, Tuple

def rank_session(results: List[Tuple[str, float, float, str, str, str]]):
    """
    results items: (name, score, avg_time, label, message, dev_plan)
    Sort by highest score, then lowest avg_time.
    Return: (table_text, winners_list, is_tie, sorted_rows)
    """
    sorted_rows = sorted(results, key=lambda r: (-r[1], r[2]))
    lines = [
        "Rank | Name         | Score  | Avg Time | Result",
        "------------------------------------------------"
    ]
    for i, (name, score, avg, label, _msg, _plan) in enumerate(sorted_rows, 1):
        lines.append(f"{i:<4}| {name:<12} | {score:>6.1f}% | {avg:.2f}s   | {label}")
    table = "\n".join(lines)

    if not sorted_rows:
        return table, [], False, sorted_rows

    # Determine winners: same top score group; break tie by fastest time; if still equal -> multiple winners
    top_score = sorted_rows[0][1]
    top_group = [r for r in sorted_rows if r[1] == top_score]
    min_time = min(r[2] for r in top_group)
    winners = [r[0] for r in top_group if r[2] == min_time]
    is_tie = len(winners) > 1
    return table, winners, is_tie, sorted_rows
