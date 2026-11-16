import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from model import Protocol, transition, kinetic_proxy, original_score, equal_work_retention


class ModelChecks(unittest.TestCase):
    def test_schedule_has_no_final_rest(self):
        self.assertEqual(Protocol("example", 4, 6, 3).elapsed, 33)
        self.assertEqual(Protocol("single", 1, 8, 99).elapsed, 8)
        self.assertEqual(Protocol("volume", 4, 8, 2).work_total, 32)

    def test_analytic_area_against_independent_midpoint_integration(self):
        initial, target, tau, duration = .35, .88, 60, 240
        end, integral = transition(initial, target, duration, tau)
        steps = 20000
        dt = duration / steps
        numeric = sum(target + (initial - target) * math.exp(-((i + .5) * dt) / tau)
                      for i in range(steps)) * dt
        self.assertAlmostEqual(integral, numeric, places=6)
        self.assertTrue(initial < end < target)

    def test_zero_duration_and_equilibrium(self):
        self.assertEqual(transition(.35, .88, 0, 60), (.35, 0))
        self.assertEqual(transition(.5, .5, 120, 30), (.5, 60))

    def test_zero_rest_equals_continuous_work(self):
        split = kinetic_proxy(Protocol("split", 4, 6, 0))
        continuous = kinetic_proxy(Protocol("continuous", 1, 24, 0))
        self.assertAlmostEqual(split["integral_q_min"], continuous["integral_q_min"], places=12)

    def test_kinetics_stays_within_response_bounds(self):
        for tau in (30, 60, 90):
            result = kinetic_proxy(Protocol("bounded", 4, 6, 2), tau)
            self.assertTrue(.35 < result["mean_q_work"] < .88)

    def test_original_score_has_no_interior_rest_optimum(self):
        for work in (3, 4, 6, 8):
            self.assertGreater(original_score(work, 4), original_score(work, 3))
        choices = [(original_score(w, r), w, r) for w in (3, 4, 6, 8) for r in (1.5, 2, 3, 4)]
        self.assertEqual(max(choices)[1:], (8, 4))

    def test_break_even_and_rank_reversal(self):
        self.assertEqual(equal_work_retention(32, 30), .9375)
        self.assertGreater(32 * .95, 30)
        self.assertLess(32 * .90, 30)

    def test_reject_invalid_inputs(self):
        for n, work, rest in [(0, 6, 2), (True, 6, 2), (2.5, 6, 2), (4, 0, 2), (4, 6, -1), (4, float('nan'), 2)]:
            with self.assertRaises(ValueError):
                Protocol("invalid", n, work, rest)
        with self.assertRaises(ValueError):
            transition(.35, .88, 240, 0)
        with self.assertRaises(ValueError):
            kinetic_proxy(Protocol("invalid target", 4, 6, 2), work_target=2)


if __name__ == "__main__":
    unittest.main()
