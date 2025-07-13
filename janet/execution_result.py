from typing import Optional


class ExecutionResult:
    def __init__(self, success: bool, message: str, logs: Optional[list] = None, labels: Optional[dict] = None):
        self.success = success
        self.message = message
        self.logs = logs or []
        self.labels = labels or {}

    def __repr__(self):
        return f"<ExecutionResult success={self.success} message='{self.message}' logs={self.logs} labels={self.labels}>"
