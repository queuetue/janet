import yaml
from meatball import preprocess_yaml


def test_meatball_macro_expansion():
    # Load your example YAML file as raw string
    with open("examples/tictactoe/statements.yaml") as f:
        yaml_content = f.read()

    # Example context for macro expansion
    context = {
        "session": {
            "PLANTANGENET": "/home/ciuser/"
        }
    }

    # Expand macros in the YAML string
    expanded_docs = preprocess_yaml(yaml_content, context)

    # Print expanded results for manual inspection
    if isinstance(expanded_docs, list):
        for doc in expanded_docs:
            print(yaml.dump(doc, sort_keys=False))
    else:
        print(yaml.dump(expanded_docs, sort_keys=False))

    # Example assertion (customize as needed)
    # assert expanded_docs[0]['spec']['policyBinding'] == 'ttt'
