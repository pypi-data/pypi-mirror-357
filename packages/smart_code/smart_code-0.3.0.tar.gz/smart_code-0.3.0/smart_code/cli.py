import argparse
from .analyzer import analyze_file
from .suggestor import format_suggestions

def main():
    parser = argparse.ArgumentParser(prog='smart-code')
    parser.add_argument('paths', nargs='+', help='file paths to analyze')
    args = parser.parse_args()
    for path in args.paths:
        sug = analyze_file(path)
        out = format_suggestions(sug)
        if out:
            print(out)
        else:
            print(f"No suggestions for {path}")

if __name__ == '__main__':
    main()
