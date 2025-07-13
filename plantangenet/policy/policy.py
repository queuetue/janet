class Policy:
    def __init__(self, id, name=None, description=None, metadata=None, spec=None, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata
        self.spec = spec

    def add_role(self, role):
        # Simulate adding a role to the policy
        print(f"Added role {role.name} to policy {self.name}")

    def remove_role(self, role):
        # Simulate removing a role from the policy
        print(f"Removed role {role.name} from policy {self.name}")

    def add_statement(self, statement):
        # Simulate adding a statement to the policy
        print(f"Added statement {statement.name} to policy {self.name}")

    def remove_statement(self, statement):
        # Simulate removing a statement from the policy
        print(f"Removed statement {statement.name} from policy {self.name}")

    def get_statements(self):
        # Simulate getting all statements in the policy
        print(f"Getting statements for policy {self.name}")
        return []

    def get_roles(self):
        # Simulate getting all roles in the policy
        print(f"Getting roles for policy {self.name}")
        return []

    def has_role(self, role):
        # Simulate checking if the policy has a specific role
        print(f"Checking if policy {self.name} has role {role.name}")
        return role in self.get_roles()

    def __str__(self):
        return f"Policy(id={self.id}, name={self.name}, description={self.description})"

    def __repr__(self):
        return f"Policy(id={self.id}, name={self.name}, description={self.description})"
