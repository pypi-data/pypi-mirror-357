import re
import argparse

from spirepy import Study, Sample
from spirepy.cli import download, view


def maincall(input, action: str, target: str, output: str = None):
    if action == "view":
        view(input, target)
    else:
        download(input, target, output)


def main():
    parser = argparse.ArgumentParser(
        description="""
  _____ _____ _____ _____  ______             
 / ____|  __ \_   _|  __ \|  ____|            
| (___ | |__) || | | |__) | |__   _ __  _   _ 
 \___ \|  ___/ | | |  _  /|  __| | '_ \| | | |
 ____) | |    _| |_| | \ \| |____| |_) | |_| |
|_____/|_|   |_____|_|  \_\______| .__/ \__, |
                                 | |     __/ |
                                 |_|    |___/ 

Interact with the SPIRE[1] database.

[1] - Thomas S B Schmidt, Anthony Fullam, Pamela Ferretti, Askarbek Orakov,
Oleksandr M Maistrenko, Hans-Joachim Ruscheweyh, Ivica Letunic, Yiqian Duan,
Thea Van Rossum, Shinichi Sunagawa, Daniel R Mende, Robert D Finn, Michael Kuhn,
Luis Pedro Coelho, Peer Bork, SPIRE: a Searchable, Planetary-scale mIcrobiome
REsource, Nucleic Acids Research, Volume 52, Issue D1, 5 January 2024, Pages
D777–D783, https://doi.org/10.1093/nar/gkad943
""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--sample",
        dest="is_sample",
        action="store_true",
        help="The item you want to interact with is a sample",
    )
    parser.add_argument(
        "--study",
        dest="is_study",
        action="store_true",
        help="The item you want to interact with is a study",
    )
    subparsers = parser.add_subparsers(help="subcommand help", dest="action")
    # create the parser for the "view" command
    parser_view = subparsers.add_parser("view", help="view the data from an object")
    parser_view.add_argument(
        dest="target",
        choices=["metadata", "amr", "manifest", "eggnog", "mags"],
        action="store",
        help="target item to view",
    )
    parser_view.add_argument(
        "input", metavar="INPUT", nargs="+", help="Input (study or sample ID)", type=str
    )
    # create the parser for the "download" command
    parser_download = subparsers.add_parser(
        "download", help="download data from an item"
    )
    parser_download.add_argument(
        dest="target",
        choices=["mags", "proteins", "genecalls", "metadata"],
        action="store",
        help="target item to dowload",
    )
    parser_download.add_argument(
        "-o",
        "--output",
        dest="output",
        help="output folder; defaults to current folder",
        default="./",
    )
    parser_download.add_argument(
        "input", metavar="INPUT", nargs="+", help="Input (study or sample ID)", type=str
    )

    args = parser.parse_args()

    if args.is_sample:
        input = Sample(id=args.input[0])
        if args.action == "view":
            maincall(input, args.action, args.target)
        else:
            maincall(input, args.action, args.target, args.output)
    else:
        input = Study(name=args.input[0])
        if args.action == "view":
            maincall(input, args.action, args.target)
        else:
            maincall(input, args.action, args.target, args.output)


if __name__ == "__main__":
    main()
