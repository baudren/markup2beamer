"""
.. module:: parser_m2b.py
    :synopsis: Definition of the command line options
.. moduleauthor:: Benjamin Audren <benj_audren@yahoo.fr>

"""
import argparse


def create_parser():
    """
    Definition of the parser command line options
    """
    parser = argparse.ArgumentParser(
        description='Mardown to Beamer converter')

    parser.add_argument('input')
    parser.add_argument(
        '-o', metavar='output pdf', type=str, dest='pdf', default=None)

    parser.add_argument(
        '-v', metavar='verbosity', dest='verbose',
        action='store_const', const=True, default=False)

    return parser


def parse():
    """
    Handle simple cases
    """

    parser = create_parser()

    # Recover all command line arguments in the args dictionnary
    args = parser.parse_args()

    # Create a default output if none specified
    if args.pdf is None:
        args.pdf = args.input.replace('.md', '.pdf')

    return args
