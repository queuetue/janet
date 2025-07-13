import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from meatball import preprocess_yaml_string

from .helpers import save_render_json, load_pickle_state, save_pickle_state
from .plan_transformer import PlanTransformer
from .plan_renderer import PlanRenderer
from .phase_executor import PhaseExecutor
from .phase_resource import PhaseResource
from .version import __version__


class JanetCLI:
    """Main Janet CLI class for plan operations."""

    def __init__(self, args: Optional[Dict[str, Any]] = None):
        """Initialize the JanetCLI with the given arguments.

        Args:
            args (Optional[Dict[str, Any]]): Command-line arguments as a dictionary.
        """
        self.args = args or {}
        self.parser = argparse.ArgumentParser(
            description="Janet CLI for plan operations"
        )
        self.subparsers = self.parser.add_subparsers(dest="command")

        # Define the 'render' command
        render_parser = self.subparsers.add_parser(
            "render", help="Render a plan")
        render_parser.add_argument(
            "-d", "--directory", type=str, default=None, help="Directory containing the plan file (default: current directory)"
        )
        render_parser.add_argument(
            "-f", "--file", type=str, default=None, help="Plan file name (default: plan.yaml)"
        )
        render_parser.add_argument(
            "--output", type=str, help="The output file for the rendered plan"
        )

        # Define the 'validate' command
        validate_parser = self.subparsers.add_parser(
            "validate", help="Validate a plan against the schema"
        )
        validate_parser.add_argument(
            "-d", "--directory", type=str, default=None, help="Directory containing the plan file (default: current directory)"
        )
        validate_parser.add_argument(
            "-f", "--file", type=str, default=None, help="Plan file name (default: plan.yaml)"
        )

        # Define the 'execute' command
        execute_parser = self.subparsers.add_parser(
            "execute", help="Execute a plan"
        )
        execute_parser.add_argument(
            "-d", "--directory", type=str, default=None, help="Directory containing the plan file (default: current directory)"
        )
        execute_parser.add_argument(
            "-f", "--file", type=str, default=None, help="Plan file name (default: plan.yaml)"
        )
        execute_parser.add_argument(
            "--timeout", type=float, default=None, help="Timeout in seconds for plan execution"
        )

    def resolve_plan_path(self):
        """Resolve the plan file path based on CLI options (-d, -f).

        Returns:
            str: The resolved plan file path.
        """
        plan_file = self.args.get("file") or self.args.get("plan")
        plan_dir = self.args.get("directory")
        if plan_dir:
            if not plan_file:
                plan_file = "plan.yaml"
            plan_path = os.path.join(plan_dir, plan_file)
        else:
            plan_path = plan_file
        if not plan_path or not os.path.isfile(plan_path):
            print(f"Error: Plan file not found: {plan_path}")
            sys.exit(1)
        return plan_path

    def run(self):
        """Run the CLI application."""
        args = self.parser.parse_args()
        self.args = vars(args)  # Convert Namespace to dictionary

        command = args.command
        if command == "render":
            self.render_plan()
        elif command == "validate":
            self.validate_plan()
        elif command == "execute":
            self.execute_plan()
        else:
            self.parser.print_help()

    def render_plan(self):
        """Render a plan using the PlanRenderer with optional Meatball macro expansion."""
        plan_path = self.resolve_plan_path()
        output_path = self.args.get("output")

        # Load and preprocess the plan
        plan = self.load_and_preprocess_plan(plan_path)

        # Render the plan
        renderer = PlanRenderer(plan)
        rendered_plan = renderer.render()

        # Save the rendered plan to the output file or print it
        if output_path:
            with open(output_path, "w") as output_file:
                yaml.dump(rendered_plan, output_file)
            print(f"Rendered plan saved to {output_path}")
        else:
            print("Rendered plan:")
            print(yaml.dump(rendered_plan))

    def load_and_preprocess_plan(self, plan_path):
        """Load and preprocess a plan file with optional Meatball macro expansion.

        Args:
            plan_path (str): Path to the plan file

        Returns:
            dict: The processed plan data
        """
        # Load the raw YAML content
        with open(plan_path, "r") as plan_file:
            raw_yaml_content = plan_file.read()

        # Apply Meatball macro expansion if available
        if preprocess_yaml_string:
            try:
                # Create context for macro expansion
                context = {
                    'plan_dir': os.path.dirname(plan_path),
                    'plan_file': os.path.basename(plan_path)
                }
                expanded_yaml_content = preprocess_yaml_string(
                    raw_yaml_content, context)
                return expanded_yaml_content
            except Exception as e:
                print(f"Warning: Meatball macro expansion failed: {e}")
                print("Falling back to standard YAML loading...")
                return yaml.safe_load(raw_yaml_content)
        else:
            print("Meatball not available, using standard YAML loading...")
            return yaml.safe_load(raw_yaml_content)

    def validate_plan(self):
        """Validate a plan against the JSON schema."""
        plan_path = self.resolve_plan_path()

        # Load and preprocess the plan
        plan = self.load_and_preprocess_plan(plan_path)

        # Validate the plan
        try:
            validate(instance=plan, schema=self.get_plan_schema())
            print("Plan is valid.")
        except ValidationError as e:
            print(f"Plan is invalid: {e.message}")

    def execute_plan(self, timeout: float = 0):
        """Execute a plan: instantiate all resources and keep running until killed or timeout."""
        plan_path = self.resolve_plan_path()

        # Load and preprocess the plan
        plan = self.load_and_preprocess_plan(plan_path)

        executor = PhaseExecutor()
        phases = plan.get("phases", [])
        resources = []
        for phase in phases:
            phase_spec = phase.get("spec", {})
            phase_resource = PhaseResource(phase_spec)
            resources.append(phase_resource)
            metadata = phase.get("metadata", {})
            name = metadata.get("name")
            display_name = metadata.get("annotations", {}).get("displayName")
            label = name or display_name or phase_resource.id or "Unknown"
            result = executor.execute(phase_resource)
            print(f"Phase {label} execution result: {result}")
        print("Instantiated resources:")
        for r, phase in zip(resources, phases):
            metadata = phase.get("metadata", {})
            name = metadata.get("name")
            display_name = metadata.get("annotations", {}).get("displayName")
            label = name or display_name or getattr(r, 'id', None) or "Unknown"
            print(f"- {label}: {r}")
        print("System running. Press Ctrl-C to exit.")
        import time
        start = time.time()
        try:
            while True:
                if timeout > 0 and (time.time() - start) > timeout:
                    print("\nSystem timed out.")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nSystem terminated.")

    def get_plan_schema(self):
        """Get the JSON schema for plan validation.

        Returns:
            dict: The JSON schema as a dictionary.
        """
        # TODO: Define and return the JSON schema for plan validation
        return {}
