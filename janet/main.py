#!/usr/bin/env python3
"""
Plan CLI Tool - A kubectl-style command-line interface for managing Plantangenet plans.

Usage:
    plan validate [-d DIRECTORY] [-f FILE]
    plan apply [-d DIRECTORY] [-f FILE]
    plan delete [-d DIRECTORY] [-f FILE]
    plan render [-d DIRECTORY] [-f FILE] [--show]
    plan plan [-d DIRECTORY] [-f FILE]
"""
from .cli import JanetCLI


def main():
    """CLI entry point."""
    cli = JanetCLI()
    exit(cli.run())


if __name__ == "__main__":
    main()
