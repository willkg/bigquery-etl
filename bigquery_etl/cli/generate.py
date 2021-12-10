import click
from pathlib import Path
import importlib.util
from inspect import getmembers
import sys


SQL_GENERATORS_DIR = "sql_generators"
GENERATE_COMMAND = "generate"
ROOT = Path(__file__).parent.parent.parent


def generate_group():
    """Create the CLI group for the generate command."""
    commands = []
    generator_path = ROOT / SQL_GENERATORS_DIR

    for path in generator_path.iterdir():
        if path.is_dir():
            # get Python modules for generators
            spec = importlib.util.spec_from_file_location(
                path.name, (path / "__init__.py").absolute()
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # find the `generate` click command in the module
            members = getmembers(module)
            generate_cmd = [cmd[1] for cmd in members if cmd[0] == GENERATE_COMMAND]
            if len(generate_cmd) > 0:
                if isinstance(generate_cmd[0], click.Command):
                    # rename command to name of query generator
                    cmd = generate_cmd[0]
                    cmd.name = path.name
                    commands.append(cmd)

    # add commands for generating queries to `generate` click group
    return click.Group(
        name="generate", commands=commands, help="Commands for generating SQL queries."
    )


# expose click command group
generate = generate_group()
