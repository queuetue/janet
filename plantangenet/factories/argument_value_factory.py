
import os


class ArgumentValueFactory:
    def generate(self, references: dict, sample=False) -> dict:
        """
        Generate argument values based on the provided manifest.
        """
        result = {}
        for key, value in references.items():
            shellVar = value.get("shellVar")
            if sample:
                fallback = os.urandom(16).hex()
            else:
                fallback = None
            if shellVar:
                result[key] = os.getenv(
                    shellVar, value.get("default", fallback))
            else:
                result[key] = value.get("default", fallback)
        return result
