"""
Canonical payload contract constants.
Every connector must produce a payload that conforms to this shape.
"""

SOURCE_CATEGORIES = {"work_tracking", "code_collaboration", "service_context"}
SOURCE_MODES = {"live", "scenario", "user_provided"}
PRODUCTS = {"jira", "github", "gitlab", "manual"}

# Minimum required keys in the top-level payload
REQUIRED_PAYLOAD_KEYS = {"tasks"}

# Allowed task statuses
TASK_STATUSES = {"open", "in_progress", "done", "blocked"}
ACTIVE_TASK_STATUSES = {"open", "in_progress"}

# Allowed priority values (None is also valid — its absence is a signal)
TASK_PRIORITIES = {"critical", "high", "medium", "low"}

# Allowed PR statuses
PR_STATUSES = {"open", "merged", "closed"}

# Allowed service criticality levels
SERVICE_CRITICALITY = {"p0", "p1", "p2"}

# History event types
HISTORY_EVENTS = {"status_change", "owner_change", "team_transfer", "comment", "label_change"}
