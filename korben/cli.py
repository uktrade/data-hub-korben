# TODO: Use click to formalise, add generic opts etc
import sys
from . import sync, etl

MODULES = {
    'sync': sync,
    'etl': etl,
}


def print_modules():
    for module_name in sorted(MODULES):
        print("  {0}".format(module_name))


def main():
    try:
        module = MODULES[sys.argv[1]]
    except IndexError:
        print('Must pass a command, available commands are:')
        print_modules()
        return exit(1)
    except KeyError:
        print("`{0}` is not a command try one of the following:".format(
            sys.argv[1]
        ))
        print_modules()
        return exit(1)
    commands = list(sorted(getattr(module, 'COMMANDS', {}).keys()))
    if commands:
        try:
            func = module.COMMANDS[sys.argv[2]]
        except IndexError as exc:  # no command requested
            try:
                func = module.main  # module itself offers CLI
            except AttributeError:
                print(("Must pass a subcommand, available subcommands for {0} "
                       "are:").format(sys.argv[1]))
                for command in commands:
                    print("  {0}".format(command))
                return exit(1)
        except KeyError:
            print("`{0}` is not a subcommand, available subcommands are:".format(
                sys.argv[2]
            ))
            for command in commands:
                print("  {0}".format(command))
            return exit(1)
    else:
        try:
            func = module.main  # module itself offers CLI
        except AttributeError:
            print(
                "Module {0} doesn’t offer a CLI".format(module.__name__)
            )
            return exit(1)

    return func(*sys.argv[3:])
