class Role:
    def __init__(self, id, name=None, description=None, metadata=None, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.metadata = metadata

    def add_identity(self, identity):
        # Simulate adding an identity to the role
        print(f"Added identity {identity.name} to role {self.name}")

    def remove_identity(self, identity):
        # Simulate removing an identity from the role
        print(f"Removed identity {identity.name} from role {self.name}")

    def get_identities(self):
        # Simulate getting all identities in the role
        print(f"Getting identities for role {self.name}")
        return []

    def has_identity(self, identity):
        # Simulate checking if the role has a specific identity
        print(f"Checking if role {self.name} has identity {identity.name}")
        return identity in self.get_identities()

    def __str__(self):
        return f"Role(name={self.name}, description={self.description}, metadata={self.metadata})"

    def __repr__(self):
        return f"Role(name={self.name}, description={self.description}, metadata={self.metadata})"
