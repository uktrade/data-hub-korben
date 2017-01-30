from . import webserver, poll


def main():
    webserver.start()


COMMANDS = {'poll': poll.main}
