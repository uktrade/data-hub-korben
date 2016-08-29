import sys
from . import sync

COMMANDS = {
    'sync': sync,
}

def main():
    try:
        module = COMMANDS[sys.argv[1]]
    except IndexError:
        print('Must pass a command, available commands are:')
        for command in sorted(COMMANDS.keys()):
            print("  {0}".format(command))
        exit(1)
    try:
        func = getattr(module, sys.argv[2])
    except (AttributeError, IndexError):
        try:
            getattr(module, 'main')(*sys.argv[3:])
        except AttributeError:
            subcommands = sorted(getattr(module, 'COMMANDS', {}).keys())
            if not subcommands:
                print(
                    "Module {0} doesn’t offer a CLI".format(module.__name__)
                )
                exit(1)
            print('Must pass a subcommand, available commands are:')
            for command in subcommands:
                print("  {0}".format(command))
            exit(1)
