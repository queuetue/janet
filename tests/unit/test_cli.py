import pytest
from janet.cli import JanetCLI


class DummyPhaseExecutor:
    def __init__(self):
        pass

    def execute(self, phase_resource=None):
        return True


class DummyPlanRenderer:
    def __init__(self, plan):
        self.plan = plan

    def render(self):
        return {'dummy': 'rendered'}


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    monkeypatch.setattr('janet.cli.PhaseExecutor', DummyPhaseExecutor)
    monkeypatch.setattr('janet.cli.PlanRenderer', DummyPlanRenderer)


def test_validate_plan(monkeypatch, tmp_path):
    # Create a dummy plan file
    plan_file = tmp_path / "plan.yaml"
    plan_file.write_text("foo: bar\n")

    cli = JanetCLI({'plan': str(plan_file)})
    cli.get_plan_schema = lambda: {'type': 'object'}  # Accept any dict
    cli.args = {'plan': str(plan_file)}
    # Should print 'Plan is valid.'
    cli.validate_plan()


def test_render_plan(monkeypatch, tmp_path):
    plan_file = tmp_path / "plan.yaml"
    plan_file.write_text("foo: bar\n")
    cli = JanetCLI({'plan': str(plan_file)})
    cli.args = {'plan': str(plan_file)}
    cli.render_plan()


def test_execute_plan(monkeypatch, tmp_path):
    # Create a plan file in the new format
    plan_file = tmp_path / "plan.yaml"
    plan_file.write_text("""
phases:
  - metadata:
      name: preflight
      labels:
        phase: preflight
      annotations:
        displayName: "Preflight Checks"
    spec:
      description: Deploy base infra like Redis/NATS.
      selector:
        matchLabels:
          phase: preflight
      onFailure:
        action: raise
        spec:
          message: 
            - "Preflight checks failed, please check the logs."
          notify:
            email: oncall@team.com
            slack: "#ops-alerts"
  - metadata:
      name: initialization
      labels:
        phase: initialization
      annotations:
        displayName: "Initialization"
    spec:
      description: Generate IDs, slugs, and other initial data.
      selector:
        matchLabels:
          phase: initialization
      waitFor:
        phases:
          - preflight
        timeout: 300ms        
      retry:
        maxAttempts: 5
      onFailure:
        action: continue
        spec:
          message: 
            - "Initialization failed, please check the logs."
            - "We will continue with defaults."
          labels:
            initialization: defaults
      onSuccess:
        spec:
          message: 
            - "Initialization completed successfully."
          notify:
            email: oncall@team.com
  - metadata:
      name: setup
      labels:
        phase: setup
      annotations:
        displayName: "Setup"
    spec:
      description: Set up game board and initial state.
      selector:
        matchLabels:
          phase: setup
      waitFor: 
        phases: [initialization]
      retry:
        maxAttempts: "10"
  - metadata:
      name: lazy
      labels:
        phase: lazy
      annotations:
        displayName: "Lazy Deployment"
    spec:
      description: Deploy squads and other resources as needed.
      selector:
        matchLabels:
          phase: lazy
      instanceMode: onUse
""")
    cli = JanetCLI({'plan': str(plan_file)})
    cli.args = {'plan': str(plan_file)}
    cli.execute_plan(timeout=1)
