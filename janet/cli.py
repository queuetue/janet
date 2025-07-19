import argparse
import json
import os
import sys
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from jsonschema import validate, ValidationError
from meatball import preprocess_yaml_string

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
        render_parser.add_argument(
            "--format", type=str, choices=["json", "yaml"], default="json", 
            help="Output format (default: json for PMP compatibility)"
        )

        # Define the 'submit' command
        submit_parser = self.subparsers.add_parser(
            "submit", help="Submit a rendered plan to a PMP server"
        )
        submit_parser.add_argument(
            "-d", "--directory", type=str, default=None, help="Directory containing the plan file (default: current directory)"
        )
        submit_parser.add_argument(
            "-f", "--file", type=str, default=None, help="Plan file name (default: plan.yaml) or rendered JSON file"
        )
        submit_parser.add_argument(
            "--endpoint", type=str, default="http://localhost:3030", 
            help="PMP server endpoint (default: http://localhost:3030)"
        )
        submit_parser.add_argument(
            "--dry-run", action="store_true", 
            help="Perform a dry run submission"
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
        elif command == "submit":
            self.submit_plan()
        else:
            self.parser.print_help()

    def render_plan(self):
        """Render a plan using the PlanRenderer with optional Meatball macro expansion."""
        plan_path = self.resolve_plan_path()
        output_path = self.args.get("output")
        output_format = self.args.get("format", "json")

        # Load and preprocess the plan
        plan = self.load_and_preprocess_plan(plan_path)

        # Render the plan
        renderer = PlanRenderer(plan)
        rendered_plan = renderer.render()

        # Save the rendered plan to the output file or print it
        if output_path:
            with open(output_path, "w") as output_file:
                if output_format == "json":
                    json.dump(rendered_plan, output_file, indent=2)
                else:
                    yaml.dump(rendered_plan, output_file)
            print(f"Rendered plan saved to {output_path}")
        else:
            print("Rendered plan:")
            if output_format == "json":
                print(json.dumps(rendered_plan, indent=2))
            else:
                print(yaml.dump(rendered_plan))

    def submit_plan(self):
        """Submit a rendered plan to a PMP server."""
        plan_path = self.resolve_plan_path()
        endpoint = self.args.get("endpoint", "http://localhost:3030")
        dry_run = self.args.get("dry_run", False)

        # Check if the file is already rendered JSON or needs rendering
        if plan_path.endswith('.json'):
            # Load pre-rendered JSON
            with open(plan_path, "r") as f:
                rendered_plan = json.load(f)
        else:
            # Load and render YAML plan
            plan = self.load_and_preprocess_plan(plan_path)
            renderer = PlanRenderer(plan)
            rendered_plan = renderer.render()

        # Submit to PMP server
        url = f"{endpoint}/plan"
        headers = {
            "Content-Type": "application/vnd.phase-manifest+json"
        }

        try:
            print(f"Submitting plan to {url}...")
            if dry_run:
                print("DRY RUN - Plan that would be submitted:")
                print(json.dumps(rendered_plan, indent=2))
                return

            response = requests.post(url, json=rendered_plan, headers=headers)
            
            if response.status_code == 200:
                print("Plan submitted successfully!")
                if response.text:
                    print("Server response:", response.text)
            elif response.status_code == 400:
                print("Bad Request: Invalid manifest")
                print("Response:", response.text)
            elif response.status_code == 409:
                print("Conflict: Already executing or conflicting manifest")
                print("Response:", response.text)
            else:
                print(f"Unexpected response: {response.status_code}")
                print("Response:", response.text)
                
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to PMP server at {endpoint}")
            print("Make sure the server is running and accessible.")
        except Exception as e:
            print(f"Error submitting plan: {e}")

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


    def get_plan_schema(self):
        """Get the JSON schema for plan validation.

        Returns:
            dict: The JSON schema as a dictionary.
        """
        # TODO: Define and return the JSON schema for plan validation
        return {}
