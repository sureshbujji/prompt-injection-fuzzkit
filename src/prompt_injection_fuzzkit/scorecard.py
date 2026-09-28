"""Defense scorecard: aggregate fuzz results per attack class."""
from __future__ import annotations

from .payloads import ATTACK_CLASSES


def summarize(results: list[dict[str, object]]) -> dict[str, object]:
    """Aggregate results into per-class and overall defense stats."""
    per_class: dict[str, dict[str, object]] = {}
    for attack_class in ATTACK_CLASSES:
        class_results = [r for r in results if r["attack_class"] == attack_class]
        total = len(class_results)
        blocked = sum(1 for r in class_results if r["blocked"])
        bypassed = total - blocked
        per_class[attack_class] = {
            "total": total,
            "blocked": blocked,
            "bypassed": bypassed,
            "bypass_rate": (bypassed / total) if total else 0.0,
        }
    total = len(results)
    blocked = sum(1 for r in results if r["blocked"])
    return {
        "per_class": per_class,
        "total": total,
        "blocked": blocked,
        "bypassed": total - blocked,
        "bypass_rate": ((total - blocked) / total) if total else 0.0,
    }


def to_markdown(summary: dict[str, object]) -> str:
    """Render the scorecard as a Markdown table."""
    lines = [
        "# Defense Scorecard",
        "",
        "| Attack class | Cases | Blocked | Bypassed | Bypass rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    per_class = summary["per_class"]  # type: ignore[index]
    for attack_class in ATTACK_CLASSES:
        stats = per_class[attack_class]
        lines.append(
            f"| {attack_class} | {stats['total']} | {stats['blocked']} "
            f"| {stats['bypassed']} | {stats['bypass_rate']:.1%} |"
        )
    lines += [
        f"| **Overall** | **{summary['total']}** | **{summary['blocked']}** "
        f"| **{summary['bypassed']}** | **{summary['bypass_rate']:.1%}** |",
        "",
        "Lower bypass rate = stronger defense. "
        "Classes with high bypass rates are where the defense needs work.",
    ]
    return "\n".join(lines)


def print_scorecard(results: list[dict[str, object]]) -> None:
    """Print the scorecard plus a list of every bypassed case."""
    summary = summarize(results)
    print(to_markdown(summary))
    bypassed = [r for r in results if not r["blocked"]]
    if bypassed:
        print("\n## Bypassed cases (defense gaps)")
        for r in bypassed:
            print(f"- `{r['id']}` — {r['reason']}")
