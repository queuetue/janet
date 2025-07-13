from setuptools import setup, find_packages

setup(
    name="janet",
    version="1.0.0",
    description="Janet CLI and library for plan management (Plantangenet)",
    author="Scott Russell (Queuetue)",
    author_email="scott@queuetue.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "jsonschema"
    ],
    entry_points={
        "console_scripts": [
            "janet=janet.main:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.8",
)
