import unittest

from engine.rules import (
    detect_orphan_work,
    detect_undefined_outcome,
    detect_priority_translation_failure,
    detect_untracked_work_dies,
    detect_circulating_work,
)


def task(**kwargs) -> dict:
    """Minimal valid active task with overrideable fields."""
    defaults = {
        "id": "T-1",
        "title": "Test task",
        "status": "open",
        "priority": "medium",
        "owner": "alice",
        "team": "team-a",
        "service": None,
        "done_criteria": "Criteria defined",
        "success_metric": "Metric defined",
        "age_days": 1,
        "in_report": True,
        "labels": [],
        "history": [],
    }
    defaults.update(kwargs)
    return defaults


def payload(tasks=None, prs=None, services=None) -> dict:
    return {
        "tasks": tasks or [],
        "pull_requests": prs or [],
        "services": services or [],
    }


# ---------------------------------------------------------------------------
# detect_orphan_work
# ---------------------------------------------------------------------------

class TestOrphanWork(unittest.TestCase):

    def test_task_with_no_owner_and_no_team_is_detected(self):
        p = payload([task(owner=None, team=None)])
        result = detect_orphan_work(p)
        self.assertIsNotNone(result)
        self.assertEqual(result.pattern, "orphan_work")
        self.assertIn("T-1", result.matched_ids)

    def test_task_with_owner_assigned_not_detected(self):
        p = payload([task(owner="alice", team="team-a")])
        result = detect_orphan_work(p)
        self.assertIsNone(result)

    def test_done_task_with_no_owner_not_detected(self):
        p = payload([task(owner=None, team=None, status="done")])
        result = detect_orphan_work(p)
        self.assertIsNone(result)

    def test_service_with_no_owner_team_is_detected(self):
        svc = {"id": "svc-1", "name": "Svc", "owner_team": None, "criticality": "p1"}
        t = task(owner="alice", team="team-a", service="svc-1")
        p = payload([t], services=[svc])
        result = detect_orphan_work(p)
        self.assertIsNotNone(result)
        self.assertIn("T-1", result.matched_ids)

    def test_two_ownership_changes_triggers_signal(self):
        history = [
            {"event": "owner_change", "from": "alice", "to": "bob", "days_ago": 5},
            {"event": "team_transfer", "from": "team-a", "to": None, "days_ago": 3},
        ]
        p = payload([task(owner="bob", team=None, history=history)])
        result = detect_orphan_work(p)
        self.assertIsNotNone(result)

    def test_open_pr_with_no_reviewers_detected(self):
        pr = {"id": "PR-1", "title": "Fix", "author": "bob", "reviewers": [], "status": "open", "age_days": 2}
        p = payload(prs=[pr])
        result = detect_orphan_work(p)
        self.assertIsNotNone(result)
        self.assertIn("PR-1", result.matched_ids)

    def test_open_pr_with_reviewers_not_detected(self):
        pr = {"id": "PR-1", "title": "Fix", "author": "bob", "reviewers": ["carol"], "status": "open", "age_days": 2}
        p = payload(prs=[pr])
        result = detect_orphan_work(p)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# detect_undefined_outcome
# ---------------------------------------------------------------------------

class TestUndefinedOutcome(unittest.TestCase):

    def test_active_task_missing_both_fields_detected(self):
        p = payload([task(done_criteria=None, success_metric=None)])
        result = detect_undefined_outcome(p)
        self.assertIsNotNone(result)
        self.assertIn("T-1", result.matched_ids)

    def test_active_task_missing_one_field_detected(self):
        p = payload([task(done_criteria="defined", success_metric=None)])
        result = detect_undefined_outcome(p)
        self.assertIsNotNone(result)

    def test_active_task_with_both_fields_not_detected(self):
        p = payload([task(done_criteria="Done when X", success_metric="Error rate < 1%")])
        result = detect_undefined_outcome(p)
        self.assertIsNone(result)

    def test_done_task_excluded(self):
        p = payload([task(status="done", done_criteria=None, success_metric=None)])
        result = detect_undefined_outcome(p)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# detect_priority_translation_failure
# ---------------------------------------------------------------------------

class TestPriorityTranslationFailure(unittest.TestCase):

    def test_active_task_with_no_priority_not_detected(self):
        # missing priority alone is a data quality issue, not a pattern
        p = payload([task(priority=None, labels=[])])
        result = detect_priority_translation_failure(p)
        self.assertIsNone(result)

    def test_urgency_label_with_low_priority_detected(self):
        p = payload([task(priority="low", labels=["critical"])])
        result = detect_priority_translation_failure(p)
        self.assertIsNotNone(result)

    def test_urgency_label_with_high_priority_not_detected(self):
        p = payload([task(priority="critical", labels=["critical"])])
        result = detect_priority_translation_failure(p)
        self.assertIsNone(result)

    def test_task_with_priority_and_no_urgency_label_not_detected(self):
        p = payload([task(priority="medium", labels=["backend"])])
        result = detect_priority_translation_failure(p)
        self.assertIsNone(result)

    def test_priority_spread_across_service_detected(self):
        tasks = [
            task(id="T-1", service="svc", priority="critical"),
            task(id="T-2", service="svc", priority="high"),
            task(id="T-3", service="svc", priority="low"),
        ]
        p = payload(tasks)
        result = detect_priority_translation_failure(p)
        self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# detect_untracked_work_dies
# ---------------------------------------------------------------------------

class TestUntrackedWorkDies(unittest.TestCase):

    def test_task_not_in_report_detected(self):
        p = payload([task(in_report=False)])
        result = detect_untracked_work_dies(p)
        self.assertIsNotNone(result)
        self.assertIn("T-1", result.matched_ids)

    def test_task_in_report_not_detected_on_report_check(self):
        p = payload([task(in_report=True, success_metric="defined", service="svc")])
        result = detect_untracked_work_dies(p)
        self.assertIsNone(result)

    def test_old_task_with_no_metric_and_no_service_detected(self):
        p = payload([task(success_metric=None, service=None, age_days=10, in_report=True)])
        result = detect_untracked_work_dies(p)
        self.assertIsNotNone(result)

    def test_young_task_with_no_metric_and_no_service_not_detected(self):
        p = payload([task(success_metric=None, service=None, age_days=3, in_report=True)])
        result = detect_untracked_work_dies(p)
        self.assertIsNone(result)

    def test_done_task_excluded(self):
        p = payload([task(status="done", in_report=False)])
        result = detect_untracked_work_dies(p)
        self.assertIsNone(result)


# ---------------------------------------------------------------------------
# detect_circulating_work
# ---------------------------------------------------------------------------

class TestCirculatingWork(unittest.TestCase):

    def _status_change(self, from_s, to_s, days_ago):
        return {"event": "status_change", "from": from_s, "to": to_s, "days_ago": days_ago}

    def test_three_status_changes_detected(self):
        history = [
            self._status_change("open", "in_progress", 10),
            self._status_change("in_progress", "blocked", 7),
            self._status_change("blocked", "in_progress", 4),
        ]
        p = payload([task(history=history)])
        result = detect_circulating_work(p)
        self.assertIsNotNone(result)
        self.assertIn("T-1", result.matched_ids)

    def test_status_bounce_detected(self):
        history = [
            self._status_change("open", "in_progress", 8),
            self._status_change("in_progress", "open", 5),
        ]
        p = payload([task(history=history)])
        result = detect_circulating_work(p)
        self.assertIsNotNone(result)

    def test_old_task_with_multiple_status_changes_detected(self):
        history = [
            self._status_change("open", "in_progress", 12),
            self._status_change("in_progress", "blocked", 8),
        ]
        p = payload([task(age_days=20, history=history)])
        result = detect_circulating_work(p)
        self.assertIsNotNone(result)

    def test_old_task_with_single_status_change_not_detected(self):
        # age + 1 status change is normal progression, not circulating
        history = [self._status_change("open", "in_progress", 12)]
        p = payload([task(age_days=20, history=history)])
        result = detect_circulating_work(p)
        self.assertIsNone(result)

    def test_new_task_with_no_history_not_detected(self):
        p = payload([task(age_days=2, history=[])])
        result = detect_circulating_work(p)
        self.assertIsNone(result)

    def test_done_task_excluded(self):
        history = [
            self._status_change("open", "in_progress", 5),
            self._status_change("in_progress", "blocked", 3),
            self._status_change("blocked", "in_progress", 1),
        ]
        p = payload([task(status="done", history=history)])
        result = detect_circulating_work(p)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
