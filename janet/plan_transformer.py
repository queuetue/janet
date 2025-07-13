from .phase_executor import PhaseExecutor


class PlanTransformer:
    def __init__(self, rendered_plan, stored_state, environment_state):
        self.desired_resources = rendered_plan
        self.stored_state = stored_state
        self.environment_state = environment_state

    def diff_against_state(self):
        """
        What would change vs last applied?
        This is for operator plan approval.
        """
        return self._compute_diff(self.desired_resources, self.stored_state)

    def diff_against_environment(self):
        """
        What drift exists in the real world?
        For apply to fix.
        """
        return self._compute_diff(self.stored_state, self.environment_state)

    def _compute_diff(self, desired, current):
        # Classic 3-way diff algorithm
        adds = []
        updates = []
        deletes = []

        current_lookup = {(r.kind, r.id): r for r in current}
        desired_lookup = {(r.kind, r.id): r for r in desired}

        # Additions and updates
        for key, desired_r in desired_lookup.items():
            if key not in current_lookup:
                adds.append(desired_r)
            else:
                current_r = current_lookup[key]
                if desired_r.spec != current_r.spec:
                    updates.append((current_r, desired_r))

        # Deletions
        for key, current_r in current_lookup.items():
            if key not in desired_lookup:
                deletes.append(current_r)

        return {"add": adds, "update": updates, "delete": deletes}

    def apply(self, dry_run=False):
        """
        Actually perform the plan.
        """
        plan = self.diff_against_state()

        # Always show execution logs, even for dry-run
        self._execute_plan(plan, dry_run=dry_run)
        return plan

    def _execute_plan(self, plan, dry_run=False):
        executor = PhaseExecutor()
        for r in plan["add"]:
            result = executor.execute(r)
            print(f"Creating: {r}")
            for log in result.logs:
                print(f"    {log}")
        for c, d in plan["update"]:
            result = executor.execute(d)
            print(f"Updating: {c.id}")
            for log in result.logs:
                print(f"    {log}")
        for r in plan["delete"]:
            print(f"Deleting: {r}")
        if dry_run:
            print("(dry-run: no changes made)")
