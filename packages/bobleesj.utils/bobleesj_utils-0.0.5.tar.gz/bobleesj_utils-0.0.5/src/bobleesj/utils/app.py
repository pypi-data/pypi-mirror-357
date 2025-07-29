from argparse import ArgumentParser

from bobleesj.utils.cli import test
from bobleesj.utils.cli.create import gif, issues
from bobleesj.utils.cli.delete import branch


def setup_test_subcommands(subparsers):
    """
    Examples
    --------
    >>> bob test package
    >>> bob test release
    """
    test_parser = subparsers.add_parser(
        "test", help="Test the package with a new conda environment."
    )
    test_subparsers = test_parser.add_subparsers(
        dest="subcommand", required=True
    )
    test_commands = {
        "package": ("Test the single package.", test.build_pytest),
        "release": (
            "Test the release condition for the package.",
            test.build_check_release,
        ),
    }
    for name, (help_text, handler) in test_commands.items():
        subparser = test_subparsers.add_parser(name, help=help_text)
        subparser.set_defaults(func=handler)


def setup_create_subcommands(subparsers):
    """
    Examples
    --------
    >>> bob create issues
    >>> bob create gif -p <path-to-the-video-file>
    """
    create_parser = subparsers.add_parser(
        "create", help="Create new issues, PRs, etc."
    )
    create_subparsers = create_parser.add_subparsers(
        dest="subcommand", required=True
    )
    create_commands = {
        "issues": ("Create issues.", issues.create),
        "gif": ("Create a GIF from a video file.", gif.create),
    }
    for name, (help_text, handler) in create_commands.items():
        subparser = create_subparsers.add_parser(name, help=help_text)
        if name == "gif":
            subparser.add_argument(
                "-p", "--path", required=True, help="Path to the video file"
            )
        subparser.set_defaults(func=handler)


def setup_delete_subcommands(subparsers):
    """
    Examples
    --------
    >>> bob delete local-branches
    """
    delete_parser = subparsers.add_parser(
        "delete", help="Operations for deleting files, branches, etc."
    )
    delete_subparsers = delete_parser.add_subparsers(
        dest="subcommand", required=True
    )
    delete_commands = {
        "local-branches": (
            "Delete all local branches.",
            branch.delete_local,
        ),
    }
    for name, (help_text, handler) in delete_commands.items():
        subparser = delete_subparsers.add_parser(name, help=help_text)
        subparser.set_defaults(func=handler)


def main():
    parser = ArgumentParser(
        description="Save time managing software packages."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_test_subcommands(subparsers)
    setup_delete_subcommands(subparsers)
    setup_create_subcommands(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    """
    Examples:
    ---------
    >>> bob test package
    >>> bob test release
    >>> bob create issues
    >>> bob delete local-branches

    Not implemented:
    >>> bob test packages
    >>> bob delete local-branch
    >>> bob create issues
    """
    main()
