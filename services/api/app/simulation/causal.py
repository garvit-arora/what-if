from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    UNCHANGED = "unchanged"
    DIRECTLY_INTERVENED = "directly_intervened"
    DEPENDENCY_DISRUPTED = "dependency_disrupted"
    STILL_SUPPORTED = "still_supported_by_another_pathway"
    INDETERMINATE = "indeterminate"


class Mode(StrEnum):
    ALL = "ALL"
    ANY = "ANY"


@dataclass(frozen=True)
class Mechanism:
    id: str
    inputs: tuple[str, ...]
    output: str
    mode: Mode
    certainty: str = "documented"


@dataclass(frozen=True)
class TraceStep:
    mechanism_id: str
    output: str
    supported: bool
    reason: str


@dataclass(frozen=True)
class SimulationResult:
    statuses: dict[str, Status]
    trace: tuple[TraceStep, ...]


def simulate(
    event_ids: set[str], mechanisms: list[Mechanism], removed: set[str]
) -> SimulationResult:
    """Evaluate grouped support to a bounded fixed point.

    An output with no mechanism is a baseline fact. If multiple mechanisms target
    one output, they are alternative pathways. `PRECEDED`/chronology edges are not
    accepted by this function and therefore cannot propagate invalidity.
    """
    unknown = removed - event_ids
    if unknown:
        raise ValueError(f"unknown intervention ids: {sorted(unknown)}")

    ordered = sorted(mechanisms, key=lambda item: item.id)
    active = event_ids - removed
    ever_disrupted: set[str] = set()
    trace: list[TraceStep] = []
    limit = max(1, len(event_ids) * max(1, len(ordered)) + 1)

    by_output: dict[str, list[Mechanism]] = {}
    for mechanism in ordered:
        if mechanism.output not in event_ids or set(mechanism.inputs) - event_ids:
            raise ValueError(f"mechanism {mechanism.id} references an unknown event")
        by_output.setdefault(mechanism.output, []).append(mechanism)

    for _ in range(limit):
        changed = False
        for output in sorted(by_output):
            if output in removed:
                continue
            evaluations: list[tuple[Mechanism, bool]] = []
            for mechanism in by_output[output]:
                inputs = [item in active for item in mechanism.inputs]
                supported = all(inputs) if mechanism.mode is Mode.ALL else any(inputs)
                evaluations.append((mechanism, supported))
            output_supported = any(value for _, value in evaluations)
            if output_supported and output not in active:
                active.add(output)
                changed = True
            elif not output_supported and output in active:
                active.remove(output)
                ever_disrupted.add(output)
                changed = True
        if not changed:
            break
    else:
        raise RuntimeError("causal evaluation did not converge within its safety bound")

    statuses = {event_id: Status.UNCHANGED for event_id in sorted(event_ids)}
    for event_id in removed:
        statuses[event_id] = Status.DIRECTLY_INTERVENED
    for output, output_mechanisms in sorted(by_output.items()):
        evaluations = []
        for mechanism in output_mechanisms:
            inputs = [item in active for item in mechanism.inputs]
            supported = all(inputs) if mechanism.mode is Mode.ALL else any(inputs)
            evaluations.append(supported)
            trace.append(TraceStep(
                mechanism.id,
                output,
                supported,
                f"{mechanism.mode}: active inputs {sum(inputs)}/{len(inputs)}",
            ))
        if output not in active:
            statuses[output] = (Status.DEPENDENCY_DISRUPTED if all(m.certainty == "documented" for m in output_mechanisms) else Status.INDETERMINATE)
        elif output in ever_disrupted or (not all(evaluations) and any(evaluations)):
            statuses[output] = Status.STILL_SUPPORTED

    return SimulationResult(statuses, tuple(trace))

