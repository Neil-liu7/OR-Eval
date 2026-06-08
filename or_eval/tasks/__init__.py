"""Task registry — YAML-driven benchmark definitions.

Adding a new OR benchmark requires only a YAML file in tasks/configs/.
No core code changes needed.
"""
from or_eval.tasks.registry import (
    TaskConfig,
    get_task,
    list_tasks,
    load_task_problems,
    register_task,
)
