class PhaseResource:
    def __init__(self, spec):
        self.kind = spec.get("kind", "Phase")
        self.id = spec.get("id") or spec.get("name")
        self.spec = spec
        self.phase = spec.get("phase")
        self.name = spec.get("name")
        self.metadata = spec.get("metadata", {})

    def __repr__(self):
        return f"<PhaseResource kind={self.kind} id={self.id} phase={self.phase} name={self.name} spec={self.spec}>"
