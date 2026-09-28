"""Tests for the defense scorecard."""
from prompt_injection_fuzzkit.payloads import ATTACK_CLASSES
from prompt_injection_fuzzkit.scorecard import summarize, to_markdown


def sample_results():
    return [
        {"id": "a/identity/0", "attack_class": "direct_override", "mutator": "identity",
         "blocked": True, "reason": "blocklist hit"},
        {"id": "a/homoglyph/0", "attack_class": "direct_override", "mutator": "homoglyph",
         "blocked": False, "reason": "no defense triggered"},
        {"id": "b/identity/0", "attack_class": "prompt_leak", "mutator": "identity",
         "blocked": True, "reason": "blocklist hit"},
    ]


def test_summarize_counts_per_class():
    s = summarize(sample_results())
    assert s["per_class"]["direct_override"]["total"] == 2
    assert s["per_class"]["direct_override"]["blocked"] == 1
    assert s["per_class"]["direct_override"]["bypassed"] == 1
    assert s["per_class"]["direct_override"]["bypass_rate"] == 0.5


def test_summarize_overall():
    s = summarize(sample_results())
    assert s["total"] == 3
    assert s["blocked"] == 2
    assert s["bypassed"] == 1
    assert s["bypass_rate"] == 1 / 3


def test_summarize_includes_every_attack_class():
    s = summarize(sample_results())
    assert set(s["per_class"]) == set(ATTACK_CLASSES)
    # classes with no cases report zeros, not errors
    assert s["per_class"]["role_confusion"]["total"] == 0
    assert s["per_class"]["role_confusion"]["bypass_rate"] == 0.0


def test_markdown_renders_table():
    md = to_markdown(summarize(sample_results()))
    assert "| Attack class |" in md
    for attack_class in ATTACK_CLASSES:
        assert attack_class in md
    assert "Overall" in md
    assert "50.0%" in md  # direct_override bypass rate
