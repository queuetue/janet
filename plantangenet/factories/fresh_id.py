

import os
from ulid import ULID


class FreshIdFactory:
    def generate(self, references: dict, sample=False) -> dict:
        """
        Generate argument values based on the provided manifest.
        """
        result = {}
        for key, value in references.items():
            shellVar = value.get("shellVar")
            prefix = value.get("prefix", "VAR-")
            if sample:
                fallback = f"{prefix}{os.urandom(8).hex()}"
            else:
                fallback = f"{prefix}{ULID()}"
            if shellVar:
                result[key] = os.getenv(shellVar, fallback)
            else:
                result[key] = fallback
        return result
