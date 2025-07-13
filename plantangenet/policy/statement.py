class Statement:
    def __init__(self, id, name=None, action=None, effect=None, condition=None, metadata=None, **kwargs):
        self.id = id
        self.name = name
        self.action = action
        self.effect = effect
        self.condition = condition
        self.metadata = metadata

    def __str__(self):
        return f"Statement(id={self.id}, name={self.name}, action={self.action}, effect={self.effect})"

    def __repr__(self):
        return f"Statement(id={self.id}, name={self.name}, action={self.action}, effect={self.effect})"

    def evaluate(self, context):
        # Simulate evaluating the statement against a context
        print(
            f"Evaluating statement {self.name} with action {self.action} and effect {self.effect}")
        if self.condition:
            print(f"Conditions: {self.condition}")
        return self.effect == "allow"
