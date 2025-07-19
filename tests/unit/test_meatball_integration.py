import yaml
from meatball import preprocess_yaml


def test_meatball_macro_expansion():
    # Load your example YAML file as a string
    with open("examples/tictactoe/statements.yaml") as f:
        yaml_str = f.read()

    # Example context for macro expansion
    context = {
        "session": {
            "PLANTANGENET": "/home/ciuser/"
        }
    }

    # Expand macros in the YAML string
    from meatball import preprocess_yaml_string
    expanded = preprocess_yaml_string(yaml_str, context)

    # Print expanded result for manual inspection
    print(yaml.dump(expanded, sort_keys=False))
