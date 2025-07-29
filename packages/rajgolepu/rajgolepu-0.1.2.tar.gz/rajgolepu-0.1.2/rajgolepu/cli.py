import argparse
from rajgolepu import (
    info, format_title_case, timer,
    reverse_string, count_vowels, help
)

def main():
    parser = argparse.ArgumentParser(
        description="rajgolepu CLI portfolio tool",
        epilog="""Examples:
  rajgolepu --info
  rajgolepu --format 'hello world'
  rajgolepu --reverse 'hello'
  rajgolepu --vowels 'encyclopedia'
  rajgolepu --time
  rajgolepu --help""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--info', action='store_true', help="Show portfolio information")
    parser.add_argument('--format', type=str, help="Format input text in Title Case")
    parser.add_argument('--reverse', type=str, help="Reverse a string")
    parser.add_argument('--vowels', type=str, help="Count vowels in a string")
    parser.add_argument('--time', action='store_true', help="Run a sample function with timer")
    parser.add_argument('--help', action='store_true', help="List all available functions")

    args = parser.parse_args()

    if args.info:
        info()
    elif args.format:
        print(format_title_case(args.format))
    elif args.reverse:
        print(reverse_string(args.reverse))
    elif args.vowels:
        print(f"Vowel count: {count_vowels(args.vowels)}")
    elif args.time:
        @timer
        def sample_function():
            sum(range(1000000))
        sample_function()
    elif args.help:
        help()
    else:
        parser.print_help()
