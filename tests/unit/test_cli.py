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
