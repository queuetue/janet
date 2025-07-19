# Janet

**Janet** is a command-line tool for authoring, expanding, validating, and submitting declarative YAML-based *plans*. It serves as a frontend for workflow execution systems — rendering plans from source files and sending them to compatible runtimes for dry-run, apply, or inspection.

Janet focuses on transformation and communication — helping humans write plans and systems understand them.

---

## Features

* **Macro Expansion**: Leverages [Meatball](https://github.com/queuetue/meatball) for safe, auditable macro expansion inside YAML plans.
* **Validation**: Confirms plan structure against a JSON Schema, ensuring well-formed output.
* **Render**: Converts macro-enhanced YAML into a fully interpolated JSON plan.
* **Submit**: Sends rendered plans to a running plan executor (like [Planter](https://github.com/queuetue/planter)) over HTTP.
* **Status Check** *(planned)*: Queries remote execution state and differences.

---

## Intended Flow

1. Author a macro-enhanced YAML plan file.
2. Use Janet to expand, validate, and render it.
3. Submit the rendered plan to a running executor.
4. Use Janet to view diffs, logs, or current status.

---

## Macro Expansion

Janet integrates deeply with [Meatball](https://github.com/queuetue/meatball), a macro processing engine for YAML/JSON pipelines. This enables:

* Inline string expansion (`py:"Hello {plan_file}"`)
* S-expression and list macros
* Embedded block templates
* Support for templating in Python, JavaScript, Go templates, and more

### Context Provided to Macros

When expanding, Janet passes:

* `plan_dir`: The directory containing the plan
* `plan_file`: The plan’s filename (e.g. `plan.yaml`)

### Example

```yaml
phases:
  - metadata:
      name: preflight
    spec:
      description: py:"Deploy infra from {plan_file}"
      selector:
        matchLabels:
          phase: js:"${plan_file}_preflight"
```

---

## Usage

```bash
janet [render|validate|submit] [-d DIR] [-f FILE] [--output FILE]
```

### Commands

* `render`: Expand and convert a YAML plan into JSON.
* `validate`: Ensure rendered plans match the expected schema.
* `submit`: Send the rendered plan to a remote executor via HTTP.

---

## Examples

```bash
# Expand and validate a plan
janet render -d examples/tictactoe --output rendered.json
janet validate -f rendered.json

# Submit to a running server
janet submit --endpoint http://localhost:3030 --file rendered.json
```

Or in a one-liner:

```bash
janet render -d myplan | janet submit --endpoint http://planter.local:3030
```

---

## File Selection

By default, Janet looks for `plan.yaml` in the current or specified directory. Use `-f` to specify an alternate filename.

```bash
# Use examples/tictactoe/plan.yaml
janet render -d examples/tictactoe

# Use a custom file
janet render -f custom.yaml
```

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone https://github.com/queuetue/janet
cd janet
pip install -e .
```

---

## Requirements

* Python 3.8+
* `PyYAML`
* `jsonschema`
* [`meatball`](https://github.com/queuetue/meatball)

---

## Compatibility

Janet emits plans in a well-defined JSON format that can be consumed by any compliant runtime. It is currently tested against [Planter](https://github.com/queuetue/planter), but is not limited to any single backend.

---

Immediate TODO:
[X] remove execution system (provided by planter server, see PROTOCOL.md)
[X] fix errors that prevent current examples from running
[ ] remove state system (or move to local testing only - see PROTOCOL.md)
[ ] interface to planter for storage (see PROTOCOL.md)

---
## License

MIT © 2025 [Queuetue, LLC](https://queuetue.com)
