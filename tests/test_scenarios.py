import os
import unittest

from connectors.scenario_connector import ScenarioConnector
from engine.detector import detect_patterns
from engine.interpreter import interpret
from engine.output import assemble

SCENARIOS_DIR = os.path.join(os.path.dirname(__file__), "..", "scenarios")


def run_scenario(filename: str) -> dict:
    path = os.path.join(SCENARIOS_DIR, filename)
    connector = ScenarioConnector(path)
    payload = connector.load()
    results = detect_patterns(payload)
    findings = [interpret(r) for r in results]
    return {
        "payload": payload,
        "results": results,
        "findings": findings,
        "output": assemble(findings, payload),
    }


class TestOrphanWorkScenario(unittest.TestCase):

    def setUp(self):
        self.data = run_scenario("orphan_work_strong.json")

    def test_orphan_work_detected(self):
        patterns = [r.pattern for r in self.data["results"]]
        self.assertIn("orphan_work", patterns)

    def test_orphan_finding_has_evidence(self):
        orphan = next(f for f in self.data["findings"] if f.pattern == "orphan_work")
        self.assertTrue(len(orphan.evidence) > 0)

    def test_orphan_finding_has_improvements(self):
        orphan = next(f for f in self.data["findings"] if f.pattern == "orphan_work")
        self.assertTrue(len(orphan.suggested_improvements) > 0)

    def test_output_has_required_keys(self):
        output = self.data["output"]
        self.assertIn("generated_at", output)
        self.assertIn("input_summary", output)
        self.assertIn("findings", output)

    def test_input_summary_counts_are_correct(self):
        summary = self.data["output"]["input_summary"]
        payload = self.data["payload"]
        self.assertEqual(summary["task_count"], len(payload["tasks"]))
        self.assertEqual(summary["pr_count"], len(payload["pull_requests"]))


class TestUndefinedOutcomeScenario(unittest.TestCase):

    def setUp(self):
        self.data = run_scenario("undefined_outcome_strong.json")

    def test_undefined_outcome_detected(self):
        patterns = [r.pattern for r in self.data["results"]]
        self.assertIn("undefined_outcome", patterns)

    def test_done_tasks_are_excluded(self):
        outcome = next(
            r for r in self.data["results"] if r.pattern == "undefined_outcome"
        )
        # T-206 is done — must not appear in matched_ids
        self.assertNotIn("T-206", outcome.matched_ids)

    def test_interpretation_is_non_empty(self):
        outcome = next(f for f in self.data["findings"] if f.pattern == "undefined_outcome")
        self.assertTrue(len(outcome.interpretation) > 0)


class TestMixedCaseScenario(unittest.TestCase):

    def setUp(self):
        self.data = run_scenario("mixed_case.json")

    def test_at_least_two_patterns_detected(self):
        self.assertGreaterEqual(len(self.data["results"]), 2)

    def test_all_findings_have_non_empty_issue(self):
        for finding in self.data["findings"]:
            self.assertTrue(len(finding.issue) > 0, f"Empty issue in {finding.pattern}")

    def test_all_findings_have_improvements(self):
        for finding in self.data["findings"]:
            self.assertTrue(
                len(finding.suggested_improvements) > 0,
                f"No improvements for {finding.pattern}"
            )

    def test_output_is_serializable(self):
        import json
        output = self.data["output"]
        # Should not raise
        serialized = json.dumps(output)
        self.assertIsInstance(serialized, str)

    def test_findings_list_matches_result_count(self):
        self.assertEqual(
            len(self.data["results"]),
            len(self.data["findings"])
        )


class TestFalsePositiveGuard(unittest.TestCase):

    def setUp(self):
        self.data = run_scenario("false_positive_guard.json")

    def test_false_positive_guard_detects_no_patterns(self):
        self.assertEqual(
            len(self.data["results"]), 0,
            f"Expected 0 patterns but got: {[r.pattern for r in self.data['results']]}"
        )

    def test_findings_list_is_empty(self):
        self.assertEqual(self.data["output"]["findings"], [])

    def test_output_is_valid_json(self):
        import json
        serialized = json.dumps(self.data["output"])
        self.assertIsInstance(serialized, str)

    def test_input_summary_counts_are_correct(self):
        summary = self.data["output"]["input_summary"]
        payload = self.data["payload"]
        self.assertEqual(summary["task_count"], len(payload["tasks"]))
        self.assertEqual(summary["pr_count"], len(payload["pull_requests"]))
        self.assertEqual(summary["service_count"], len(payload["services"]))


class TestCirculatingWorkSuppression(unittest.TestCase):
    """Suppression layer: circulating_work must not fire when orphan_work is HIGH on same entity."""

    def test_strong_orphan_present_circulating_suppressed(self):
        data = run_scenario("circulating_work_strong.json")
        patterns = [r.pattern for r in data["results"]]
        self.assertIn("orphan_work", patterns)
        self.assertNotIn("circulating_work", patterns)

    def test_overlap_orphan_and_untracked_present_circulating_suppressed(self):
        data = run_scenario("circulating_work_overlap.json")
        patterns = [r.pattern for r in data["results"]]
        self.assertIn("orphan_work", patterns)
        self.assertIn("untracked_work_dies", patterns)
        self.assertNotIn("circulating_work", patterns)

    def test_weak_no_patterns_detected(self):
        data = run_scenario("circulating_work_weak.json")
        self.assertEqual(data["results"], [])


if __name__ == "__main__":
    unittest.main()
