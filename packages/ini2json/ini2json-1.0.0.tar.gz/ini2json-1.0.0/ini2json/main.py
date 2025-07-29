import sys
import json
import argparse
import configparser

EPILOG = "@readwithai 📖 https://readwithai.substack.com/p/habits ⚡️ machine-aided reading ✒️"

def ini2json():
    parser = argparse.ArgumentParser(
        description="Convert INI to JSON",
        epilog=EPILOG
    )
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r", encoding="utf-8"), default=sys.stdin)
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.optionxform = str  # preserve key case
    config.read_file(args.infile)

    result = {section: dict(config.items(section)) for section in config.sections()}
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


def json2ini():
    parser = argparse.ArgumentParser(
        description="Convert JSON to INI",
        epilog=EPILOG
    )
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r", encoding="utf-8"), default=sys.stdin)
    args = parser.parse_args()

    data = json.load(args.infile)
    config = configparser.ConfigParser()
    config.optionxform = str

    for section, values in data.items():
        config[section] = values

    config.write(sys.stdout)
