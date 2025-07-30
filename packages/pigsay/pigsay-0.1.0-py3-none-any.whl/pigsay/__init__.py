import argparse

from .converter import PigConverter


def main():
    parser = argparse.ArgumentParser(description="猪曰")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enc_text_parser = subparsers.add_parser("encrypt")
    enc_text_parser.add_argument("text")

    dec_text_parser = subparsers.add_parser("decrypt")
    dec_text_parser.add_argument("cipher")

    enc_file_parser = subparsers.add_parser("encrypt-file")
    enc_file_parser.add_argument("input")
    enc_file_parser.add_argument("output")

    dec_file_parser = subparsers.add_parser("decrypt-file")
    dec_file_parser.add_argument("input")
    dec_file_parser.add_argument("output")

    args = parser.parse_args()

    try:
        converter = PigConverter()
        match args.command:
            case "encrypt":
                print(converter.encrypt_string(args.text))
            case "decrypt":
                print(converter.decrypt_string(args.cipher))
            case "encrypt-file":
                converter.encrypt_file(args.input, args.output)
            case "decrypt-file":
                converter.decrypt_file(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}")
