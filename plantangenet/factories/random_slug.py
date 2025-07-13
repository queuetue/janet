import os
from coolname import generate_slug


class RandomSlugFactory:
    def generate(self, references: dict, sample=False) -> dict:
        """
        Generate argument values based on the provided manifest.
        """
        result = {}
        for key, value in references.items():
            shellVar = value.get("shellVar")
            chunks = value.get("chunks", 2)
            fallback = generate_slug(chunks)
            if shellVar:
                result[key] = os.getenv(
                    shellVar, fallback)
            else:
                result[key] = fallback
        return result
