class Squad:
    def __init__(self, id, name=None, session_id=None, class_name=None, max_members=None, metadata=None, spec=None, **kwargs):
        self.id = id
        self.name = name
        self.session_id = session_id
        self.class_name = class_name
        self.max_members = max_members
        self.metadata = metadata
        self.spec = spec

    def __str__(self):
        return f"Squad(id={self.id}, name={self.name}, session_id={self.session_id}, class_name={self.class_name}, max_members={self.max_members})"

    def __repr__(self):
        return f"Squad(id={self.id}, name={self.name}, session_id={self.session_id}, class_name={self.class_name}, max_members={self.max_members})"

    def add_member(self, member):
        # Simulate adding a member to the squad
        print(f"Added member {member.name} to squad {self.name}")

    def remove_member(self, member):
        # Simulate removing a member from the squad
        print(f"Removed member {member.name} from squad {self.name}")

    def get_members(self):
        # Simulate getting all members in the squad
        print(f"Getting members for squad {self.name}")
        return []

    def has_member(self, member):
        # Simulate checking if the squad has a specific member
        print(f"Checking if squad {self.name} has member {member.name}")
        return member in self.get_members()
