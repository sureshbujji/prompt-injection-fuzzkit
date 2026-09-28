"""Fuzz runner: builds the attack-case matrix and executes it."""
from __future__ import annotations

from .mutators import MUTATORS
from .payloads import BASE_PAYLOADS
from .target import defended_chat


def build_cases() -> list[dict[str, object]]:
    """Build every (attack class x seed x mutator) case.

    The multi-turn class replays its seed as a turn sequence instead of
    being mutated.
    """
    cases: list[dict[str, object]] = []
    for attack_class, seeds in BASE_PAYLOADS.items():
        if attack_class == "multi_turn_escalation":
            cases.append(
                {
                    "id": f"{attack_class}/split_turns",
                    "attack_class": attack_class,
                    "mutator": "split_turns",
                    "turns": list(seeds),
                }
            )
            continue
        for i, seed in enumerate(seeds):
            for name, mutate in MUTATORS.items():
                cases.append(
                    {
                        "id": f"{attack_class}/{name}/{i}",
                        "attack_class": attack_class,
                        "mutator": name,
                        "turns": [mutate(seed)],
                    }
                )
    return cases


def run_case(case: dict[str, object]) -> dict[str, object]:
    """Replay a case's turns against the target; stop on first block."""
    messages: list[dict[str, str]] = []
    result: dict[str, object] = {"blocked": False, "reason": "no turns", "response": ""}
    for turn in case["turns"]:  # type: ignore[union-attr]
        messages.append({"role": "user", "content": turn})
        result = defended_chat(messages)
        messages.append({"role": "assistant", "content": str(result["response"])})
        if result["blocked"]:
            break
    return {
        "id": case["id"],
        "attack_class": case["attack_class"],
        "mutator": case["mutator"],
        "blocked": result["blocked"],
        "reason": result["reason"],
    }


def run_all() -> list[dict[str, object]]:
    """Execute the full case matrix and return the results."""
    return [run_case(case) for case in build_cases()]
