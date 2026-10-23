"""CLI: python -m pii_redact [FILE]  (reads stdin when FILE is omitted)."""
import sys

from .redact import redact_text


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    sys.stdout.write(redact_text(text))


if __name__ == "__main__":
    main()
