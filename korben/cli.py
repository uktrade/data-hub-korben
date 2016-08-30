import sys
from . import sync, odata_psql

COMMANDS = {
    'sync': sync,
    'odata-psql': odata_psql,
}


def print_commands():
    for command in sorted(COMMANDS):
        print("  {0}".format(command))


def main():
    try:
        module = COMMANDS[sys.argv[1]]
    except IndexError:
        print('Must pass a command, available commands are:')
        print_commands()
        exit(1)
    except KeyError:
        print("`{0}` is not a command, available commands are:".format(
            sys.argv[1]
        ))
        print_commands()
        exit(1)
    try:
        func = getattr(module, sys.argv[2]).main
    except (AttributeError, IndexError) as exc:
        import ipdb;ipdb.set_trace()
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
    func(*sys.argv[3:])
