#!/usr/bin/env python3

import time

from .helpers import parse_timeout
from .phase_resource import PhaseResource
from .execution_result import ExecutionResult


class PhaseExecutor:
    def execute(self, phase: PhaseResource) -> ExecutionResult:
        logs = []
        result_message = f"Executing phase {phase.name or phase.id}"
        logs.append(result_message)

        # Handle waitFor timeout
        wait_for = phase.spec.get("waitFor", {})
        timeout_str = wait_for.get("timeout")
        timeout_value = parse_timeout(timeout_str)
        if timeout_value > 0:
            logs.append(f"Sleeping for timeout: {timeout_value} seconds")
            time.sleep(timeout_value)

        # Handle retry
        retry_config = phase.spec.get("retry", {})
        max_attempts = int(retry_config.get("maxAttempts", 1))

        attempt = 0
        success = False
        while attempt < max_attempts:
            attempt += 1
            logs.append(f"Attempt {attempt} of {max_attempts}")

            # Simulated execution outcome (always succeeds for now)
            success = True
            if success:
                logs.append("Phase execution succeeded")
                break
            else:
                logs.append("Phase execution failed")

        # Choose handler based on success
        handler = phase.spec.get(
            "onSuccess") if success else phase.spec.get("onFailure")
        handler_spec = handler.get("spec", {}) if handler else {}

        # Collect handler messages and notifications
        messages = handler_spec.get("message", [])
        notify = handler_spec.get("notify", {})
        labels = handler_spec.get("labels", {})

        logs.extend(messages)
        if notify:
            logs.append(f"Notify targets: {notify}")

        return ExecutionResult(
            success=success,
            message=result_message,
            logs=logs,
            labels=labels
        )
