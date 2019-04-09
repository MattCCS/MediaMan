
import sys


SHORT_DESCRIPTION = """\
MediaMan is a simple but robust file archiving tool.

Pass the help flag (-h or --help) for more info."""


def parse_args():
    parse_args_empty()
    parse_args_action_only()


def parse_args_empty():
    if len(sys.argv) < 2:
        print(SHORT_DESCRIPTION)
        exit()


def parse_args_action_only():
    pass


if __name__ == '__main__':
    print(parse_args())
