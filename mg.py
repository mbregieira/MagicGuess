#!/usr/bin/env python3

import argparse
from magicguess.cli import main_cli
from magicguess.banner import get_banner
from magicguess.utils import clear_screen

def print_help():
    print("""
MagicGuess - Human Pattern Password/PIN Generator
---------------------------------------------

Usage:
    mg                   Launch with banner and interactive menu
    mg -q                Quiet mode (no banner)
    mg -h / --help       Show help message

Description:
    MagicGuess is an advanced wordlist and PIN generator based on real-world
    human password patterns commonly found during forensic investigations.
    The tool collects contextual information (suspect name, birth date,
    relatives, pets, relevant keywords, etc.) and generates plausible
    password combinations, including transformations, T9/PIN mappings,
    and pattern-based mutations.

Useful for:
    • Digital Forensics
    • Penetration Testing
    • Red Teaming
    • Password Profiling
""")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-q", action="store_true", help="Quiet mode (no banner)")
    parser.add_argument("-h", "--help", "--h", action="store_true")
    args = parser.parse_args()
    
    clear_screen()

    if args.help:
        print_help()
        return

    if not args.q:
        print(get_banner())

    
    main_cli()


if __name__ == "__main__":
    main()
