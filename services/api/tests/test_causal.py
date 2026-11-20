from app.simulation.causal import Mechanism, Mode, Status, simulate


def test_independent_pathway_survives() -> None:
    result = simulate(
        {"A", "B", "C"},
        [
            Mechanism("a_supports_c", ("A",), "C", Mode.ALL),
            Mechanism("b_supports_c", ("B",), "C", Mode.ALL),
        ],
        {"A"},
    )
    assert result.statuses["C"] is Status.STILL_SUPPORTED


def test_joint_requirements_fail() -> None:
    result = simulate(
        {"A", "B", "C"},
        [Mechanism("a_and_b_require_c", ("A", "B"), "C", Mode.ALL)],
        {"A"},
    )
    assert result.statuses["C"] is Status.DEPENDENCY_DISRUPTED


def test_chronology_does_not_propagate() -> None:
    result = simulate({"EARLY", "LATE"}, [], {"EARLY"})
    assert result.statuses["LATE"] is Status.UNCHANGED


def test_cycle_terminates_deterministically() -> None:
    mechanisms = [
        Mechanism("a_to_b", ("A",), "B", Mode.ALL),
        Mechanism("b_to_a", ("B",), "A", Mode.ALL),
    ]
    first = simulate({"A", "B"}, mechanisms, {"A"})
    second = simulate({"A", "B"}, mechanisms, {"A"})
    assert first == second
    assert first.statuses["B"] is Status.DEPENDENCY_DISRUPTED
