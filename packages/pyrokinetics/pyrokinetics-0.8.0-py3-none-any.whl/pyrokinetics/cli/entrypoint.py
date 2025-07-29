from argparse import ArgumentParser
from textwrap import dedent

from .convert import add_arguments as convert_add_arguments
from .convert import description as convert_description
from .convert import main as convert_main
from .generate import add_arguments as generate_add_arguments
from .generate import description as generate_description
from .generate import main as generate_main


def entrypoint() -> None:
    """
    The entrypoint for the Command Line Interface (CLI). Uses ``argparse`` to handle
    command line arguments, and makes use of subparsers to delegate tasks across
    multiple functions.
    """

    # Set up ArgumentParser and subparsers
    parser = ArgumentParser(
        prog="Pyrokinetics",
        description="A tool to run and analyse gyrokinetics simulations.",
    )
    subparsers = parser.add_subparsers(
        description=dedent(
            """\
            Please provide one of the following subcommands as a positional argument.
            For information on how each subcommand works, try providing '--help' after
            the subcommand.
            """
        ),
        dest="subcommand",
    )

    # Add a subparser for each subcommand. These should provide a short description
    # string, and two functions:
    # - add_arguments(parser): Add arguments to their own subparser. Takes the subparser
    #   as its only argument.
    # - main(args): Run the subroutine. Takes an argparse Namespace object as the only
    #   argument, and must unpack the Namespace itself.
    # The parser should then set it's default 'main' arg to the corresponding main
    # function, and the add_arguments function should set up the required arguments.
    convert_parser = subparsers.add_parser("convert", help=convert_description)
    convert_parser.set_defaults(main=convert_main)
    convert_add_arguments(convert_parser)

    generate_parser = subparsers.add_parser("generate", help=generate_description)
    generate_parser.set_defaults(main=generate_main)
    generate_add_arguments(generate_parser)

    args = parser.parse_args()

    # If user provided no subcommand, print help text
    if args.subcommand is None:
        parser.print_help()
        parser.exit()

    args.main(args)
