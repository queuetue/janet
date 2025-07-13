# Janet

Janet is a command-line tool for managing and automating YAML-based "plans". It provides a simple interface for rendering, validating, and executing plans, making it easy to build and operate declarative workflows.

## Features
- **Render**: Load and render a plan file, optionally saving the output.
- **Validate**: Check a plan file against a JSON schema to ensure correctness.
- **Execute**: Run the plan using a phase-based executor.
- **Macro Expansion**: Uses [Meatball](https://github.com/queuetue/meatball) for safe, pluggable macro expansion and preprocessing of YAML plans.

## Meatball Integration
Janet leverages the [Meatball](https://github.com/queuetue/meatball) library to preprocess and expand macros in YAML plans. This enables:
- Safe, auditable macro expansion in YAML files
- Support for inline, s-expression, list, and block macros
- Pluggable engines for custom templating (Python, JavaScript, Go templates, etc.)
- Pipeline processing for staged transformations

### Macro Expansion Context
When Janet processes a plan file, it provides the following context variables for macro expansion:
- `plan_dir`: The directory containing the plan file
- `plan_file`: The name of the plan file

### Example Plan with Macros
```yaml
phases:
  - metadata:
      name: preflight
      annotations:
        displayName: "Preflight Checks"
      labels:
        phase: preflight
    spec:
      description: py:"Deploy base infra in {plan_dir}."
      selector:
        matchLabels:
          phase: js:"${plan_file}_preflight"
      onFailure:
        spec:
          message:
            - go:"Preflight checks failed for {{ .plan_file }}"
```

### Macro Forms Supported
Janet supports all Meatball macro forms:

1. **Inline macros**: `py:"Hello {name}"`, `js:"${variable}/path"`
2. **S-expression macros**: `expr:'(concat foo /bar.js)'`
3. **List macros**: `[js, "${variable}/path"]`
4. **Block macros**: `{engine: py, template: "Hello {name}"}`

### Macro Expansion Process
1. Janet loads the raw YAML file
2. If Meatball is available, macro expansion is applied with plan context
3. The expanded YAML is then processed by Janet's rendering pipeline
4. If Meatball is not available, Janet falls back to standard YAML loading

## Usage
```
janet [render|validate|execute] [-d DIR] [-f FILE] [--output OUTPUT]
```

### Commands
- `render`: Render a plan and optionally save the output.
- `validate`: Validate a plan against the schema.
- `execute`: Execute a plan.

## Flexible Plan Selection
Janet supports flexible plan file selection using the `-d` (directory) and `-f` (file) options:

- `-d <directory>`: Specify the directory containing the plan file (defaults to current directory).
- `-f <file>`: Specify the plan file name (defaults to `plan.yaml`).

**Default Behavior:**
If you specify only the `-d` option, Janet will automatically look for `plan.yaml` in that directory. This makes it easy to run commands on standard plan files without specifying the filename each time.

**Examples:**
```
# Render the default plan.yaml in the examples/tictactoe directory
janet render -d examples/tictactoe

# Validate the default plan.yaml in a directory
janet validate -d examples/tictactoe

# Execute the default plan.yaml in a directory
janet execute -d examples/tictactoe
```

If you want to use a different filename, add the `-f` option:
```
janet render -d examples/tictactoe -f custom_plan.yaml
```

You can also use `--output` with `render` to save the rendered plan.

## Example
```
janet render plan.yaml --output rendered.yaml
janet validate plan.yaml
janet execute plan.yaml
```

## Example Output
When you run Janet with the `render` command, you will see the rendered plan as a list of phase objects:

```
$ janet render -d examples/tictactoe
Rendered plan:
- !!python/object:janet.phase_resource.PhaseResource
  id: preflight
  kind: Phase
  spec:
    description: Deploy base infra like Redis/NATS.
    ...
- !!python/object:janet.phase_resource.PhaseResource
  id: initialization
  kind: Phase
  spec:
    description: Generate IDs, slugs, and other initial data.
    ...
- !!python/object:janet.phase_resource.PhaseResource
  id: setup
  kind: Phase
  spec:
    description: Set up game board and initial state.
    ...
```

Each phase is rendered as a Python object with its configuration. You can use `--output` to save this to a file.

## Installation
Clone the repo and install in editable mode:
```
pip install -e .
```

## Requirements
- Python 3.8+
- PyYAML
- jsonschema
- meatball

## License
MIT
