class Identity:
    def __init__(self, id, name=None, roles=None, description=None, metadata=None, **kwargs):
        self.id = id
        self.name = name
        self.roles = roles
        self.description = description
        self.metadata = metadata

    def add_role(self, role):
        # Simulate adding a role to the identity
        print(f"Added role {role.name} to identity {self.name}")

    def remove_role(self, role):
        # Simulate removing a role from the identity
        print(f"Removed role {role.name} from identity {self.name}")

    def get_roles(self):
        # Simulate getting all roles for the identity
        print(f"Getting roles for identity {self.name}")
        return []

    def has_role(self, role):
        # Simulate checking if the identity has a specific role
        print(f"Checking if identity {self.name} has role {role.name}")
        return role in self.get_roles()

    def __str__(self):
        return f"Identity(id={self.id}, name={self.name})"

    def __repr__(self):
        return f"Identity(id={self.id}, name={self.name})"
