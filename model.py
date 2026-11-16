"""Exact scheduling and hypothetical kinetics; no adaptation prediction."""
from dataclasses import dataclass
from math import exp, isfinite


def positive(value, name):
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


@dataclass(frozen=True)
class Protocol:
    name: str
    repetitions: int
    work_min: float
    rest_min: float

    def __post_init__(self):
        if isinstance(self.repetitions, bool) or not isinstance(self.repetitions, int) or self.repetitions < 1:
            raise ValueError("repetitions must be a positive integer")
        positive(self.work_min, "work_min")
        if not isfinite(self.rest_min) or self.rest_min < 0:
            raise ValueError("rest_min must be finite and nonnegative")

    @property
    def work_total(self):
        return self.repetitions * self.work_min

    @property
    def rest_total(self):
        return (self.repetitions - 1) * self.rest_min

    @property
    def elapsed(self):
        return self.work_total + self.rest_total

    @property
    def density(self):
        return self.work_total / self.elapsed


PROTOCOLS = (
    Protocol("6x4 / 1", 6, 4, 1), Protocol("4x6 / 2", 4, 6, 2),
    Protocol("3x8 / 3", 3, 8, 3), Protocol("2x12 / 3", 2, 12, 3),
    Protocol("4x6 / 3", 4, 6, 3), Protocol("5x6 / 2", 5, 6, 2),
    Protocol("4x8 / 2", 4, 8, 2), Protocol("continuous 32", 1, 32, 0),
)


def transition(initial, target, duration_s, tau_s):
    """Analytic solution and integral of dq/dt=(target-q)/tau, in seconds."""
    positive(tau_s, "tau_s")
    if not all(isfinite(x) for x in (initial, target, duration_s)) or duration_s < 0:
        raise ValueError("arguments must be finite; duration nonnegative")
    decay = exp(-duration_s / tau_s)
    final = target + (initial - target) * decay
    integral = target * duration_s + (initial - target) * tau_s * (1 - decay)
    return final, integral


def kinetic_proxy(protocol, tau_s=60.0, work_target=0.88, rest_target=0.35, initial=0.35):
    """Work-only response integral and mean; q is arbitrary and dimensionless.

    0.88 is NOT a fraction of FTP, CP, heart rate or measured VO2max.
    Targets and time constants are assumptions, never hormone-derived.
    """
    if not all(isfinite(x) and 0 <= x <= 1 for x in (work_target, rest_target, initial)):
        raise ValueError("targets and initial must lie in [0, 1]")
    state, integral = initial, 0.0
    for repetition in range(protocol.repetitions):
        state, area = transition(state, work_target, 60 * protocol.work_min, tau_s)
        integral += area
        if repetition < protocol.repetitions - 1:
            state, _ = transition(state, rest_target, 60 * protocol.rest_min, tau_s)
    area_min = integral / 60
    return {"integral_q_min": area_min, "mean_q_work": area_min / protocol.work_total}


def original_score(work_min, rest_min, intensity=0.88):
    """Reconstruction of the starting analysis's unvalidated per-bout score."""
    positive(work_min, "work_min")
    if not isfinite(rest_min) or rest_min < 0:
        raise ValueError("rest_min must be finite and nonnegative")
    efficiency = exp(-.05 * max(work_min - 3, 0))
    fatigue = max(0, .15 * work_min - .25 * (1 - exp(-.4 * rest_min)))
    return work_min * intensity * efficiency - fatigue


def equal_work_retention(long_work, short_work, short_quality=1.0):
    """Break-even work-weighted quality; not an adaptation equation."""
    positive(long_work, "long_work")
    positive(short_work, "short_work")
    if not isfinite(short_quality) or not 0 <= short_quality <= 1:
        raise ValueError("short_quality must lie in [0, 1]")
    return short_work * short_quality / long_work
