"""Tests for the seed payload catalog."""
from prompt_injection_fuzzkit.payloads import ATTACK_CLASSES, BASE_PAYLOADS


def test_every_attack_class_has_seeds():
    assert set(BASE_PAYLOADS) == set(ATTACK_CLASSES)
    for attack_class, seeds in BASE_PAYLOADS.items():
        assert seeds, attack_class
        for seed in seeds:
            assert isinstance(seed, str) and seed.strip(), attack_class


def test_multi_turn_seed_is_a_turn_sequence():
    turns = BASE_PAYLOADS["multi_turn_escalation"]
    assert len(turns) == 2
    assert all(isinstance(t, str) for t in turns)
