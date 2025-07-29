import os
import sys
from pathlib import Path
import yaml
import subprocess
import argparse

class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def color_text(text, color):
    return f"{color}{text}{Colors.ENDC}"

def get_home_path():
    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")
    if not home:
        raise RuntimeError('Your environment does not contain "HOME" or "USERPROFILE" variables')
    return Path(home)

def get_bitflags_dir():
    home_dir = get_home_path()
    home_bitflags = home_dir / ".bitmark"
    if home_bitflags.exists():
        return home_bitflags
    else:
        cwd_bitflags = Path.cwd() / ".bitmark"
        cwd_bitflags.mkdir(exist_ok=True)
        return cwd_bitflags

class FlagsInfo:
    def __init__(self, db):
        self.flags_db = db

    def get_name(self, value):
        for name, val in self.flags_db:
            if val == value:
                return name
        return None

def get_flags_info(type_name):
    db_path = get_bitflags_dir() / f"{type_name}.yml"
    if not db_path.exists():
        raise RuntimeError(f"File does not exist: {db_path}")

    with open(db_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    result = []
    if isinstance(data, dict):
        for name, val in data.items():
            if isinstance(val, str):
                flag_val = int(val, 16)
            else:
                flag_val = int(val)
            result.append((name, flag_val))
    return FlagsInfo(result)

def open_bitflags_dir():
    path = get_bitflags_dir()
    if sys.platform == "win32":
        subprocess.run(["explorer", str(path)])
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)])
    else:
        subprocess.run(["xdg-open", str(path)])

def create_yaml(type_name, flags):
    db_path = get_bitflags_dir() / f"{type_name}.yml"
    if db_path.exists():
        print(color_text(f"File {db_path} already exists! Aborting.", Colors.FAIL))
        return

    data = {}
    for flag in flags:
        if '=' not in flag:
            print(color_text(f"Invalid flag format '{flag}'. Use NAME=VALUE", Colors.FAIL))
            return
        name, val_str = flag.split('=', 1)
        name = name.strip()
        val_str = val_str.strip()
        try:
            if val_str.lower().startswith("0x"):
                val = int(val_str, 16)
            else:
                val = int(val_str)
        except ValueError:
            print(color_text(f"Invalid value '{val_str}' for flag '{name}'", Colors.FAIL))
            return
        data[name] = f"0x{val:X}"

    with open(db_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    print(color_text(f"Created new flags file: {db_path}", Colors.OKGREEN))

def parse_flags(hex_number, type_name=None):
    try:
        flags = int(hex_number, 16)
    except ValueError:
        print(color_text("Invalid hex number", Colors.FAIL))
        sys.exit(1)

    flags_info = None
    if type_name:
        try:
            flags_info = get_flags_info(type_name)
        except RuntimeError as e:
            print(color_text(str(e), Colors.FAIL))
            sys.exit(1)

    result_parts = []
    for i in range(64):
        if flags & (1 << i):
            flag_value = 1 << i
            if flags_info:
                name = flags_info.get_name(flag_value)
                if name:
                    print(f"bit {i}: {color_text(f'[{name}]', Colors.OKGREEN)} 0x{flag_value:X}")
                    result_parts.append(name)
                else:
                    print(f"bit {i}: 0x{flag_value:X}")
                    result_parts.append(f"0x{flag_value:X}")
            else:
                print(f"bit {i}: 0x{flag_value:X}")
                result_parts.append(f"0x{flag_value:X}")

    print()
    print(" | ".join(result_parts))

def list_types():
    dir_path = get_bitflags_dir()
    for file_path in dir_path.iterdir():
        if file_path.suffix == ".yml":
            print(file_path.stem)

def main():
    # If first arg is a known command, use argparse normally
    # else treat it as 'parse' shortcut
    commands = {'parse', 'create', 'types', 'db', '-h', '--help'}
    argv = sys.argv[1:]
    if not argv:
        print(color_text("No arguments provided. Use '-h' for usage.", Colors.WARNING))
        sys.exit(1)

    if argv[0] not in commands:
        # Insert 'parse' as the first argument
        argv.insert(0, 'parse')

    parser = argparse.ArgumentParser(description="Bitflags utility")
    subparsers = parser.add_subparsers(dest='command', required=True)

    parse_parser = subparsers.add_parser('parse', help='Parse hex flags')
    parse_parser.add_argument('hex_number', help='Hexadecimal number to parse')
    parse_parser.add_argument('type_name', nargs='?', help='Optional type name for flag names')

    create_parser = subparsers.add_parser('create', help='Create new flags YAML file')
    create_parser.add_argument('type_name', help='Type name for the new YAML file')
    create_parser.add_argument('flags', nargs='+', help='Flags in NAME=VALUE format')

    subparsers.add_parser('types', help='List available types')
    subparsers.add_parser('db', help='Open bitflags directory')

    args = parser.parse_args(argv)

    if args.command == 'parse':
        parse_flags(args.hex_number, args.type_name)
    elif args.command == 'create':
        create_yaml(args.type_name, args.flags)
    elif args.command == 'types':
        list_types()
    elif args.command == 'db':
        open_bitflags_dir()