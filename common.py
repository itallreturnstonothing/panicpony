from datetime import datetime, timezone
import math
import argparse
from collections import namedtuple


api_key = "AIzaSyA-dlBUjVQeuc4a6ZN4RkNUYDFddrVLxrA"

consent_cookies = {"CONSENT": "YES+cb.20210622-13-p0.en+FX+677"}

# const
critical_datetime = datetime(year=2017, month=1, day=2, tzinfo=timezone.utc)
# january 2 just to be safe

HelpText = namedtuple("HelpText", "input output default_input")
CommonArgsParsed = namedtuple("CommonArgsParsed", "in_file out_file more_args")

def parse_date_format(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

# take an iterable and distribute it about evenly
# into some number of batches with at most batch_size items
def make_batches_of_size(big_list, batch_size):
    big_list = list(big_list) if not isinstance(big_list, list) else big_list
    num_batches = math.ceil(len(big_list) / batch_size)
    def unnecessary_recursion(remain, build):
        if not len(remain):
            # no more ids to distribute
            return build
        curr = remain.pop()
        front = build[1:]
        end = [build[0] + [curr]]
        return unnecessary_recursion(remain, front + end)

    kickstart = [big_list[i*(batch_size - 1):(i + 1)*(batch_size - 1)] for i in range(num_batches)]
    remain = big_list[num_batches*(batch_size - 1):]
    return unnecessary_recursion(remain, kickstart)

def print_or_not(message, end=None):
    if not quiet:
        if end:
            print(message, end)
        else:
            print(message)


def parse_args(helptext, add_options_callback):
    global api_key
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Optional API key to use. There is a default key.")

    parser.add_argument(
        "-i",
        "--input-file",
        help=helptext.input,
        metavar="file",
        default=helptext.default_input
    )
    parser.add_argument(
        "-o",
        "--machine-readable-output",
        help=helptext.output,
        metavar="file"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress stdout messages."
    )
    add_options_callback(parser)

    args = parser.parse_args()

    if args.key:
        api_key = args.key
    

    input_filename = args.input_file
    if args.quiet and not args.machine_readable_output:
        print("quiet + no output file. not doing anything.")
        exit()
    from common import api_key # why is this so dumb
    global quiet
    quiet = args.quiet or (args.machine_readable_output == "-")
    
    # try to set up the input file
    if input_filename == "-":
        import sys
        input_file = sys.stdin
    else:
        try:
            input_file = open(input_filename)
        except Exception as e:
            print(f"failed to open input file {input_filename}")
            print(e)
            exit()

    # try to set up the machine-readable output file if one has been specified
    if args.machine_readable_output:
        if args.machine_readable_output == "-":
            import sys
            output_file = sys.stdout
        else:
            try:
                output_file = open(args.machine_readable_output, "w")
            except Exception as e:
                print(f"failed to open output file {args.machine_readable_output}")
                print(e)
                input_file.close()
                exit()
    else:
        output_file = None



    return CommonArgsParsed(in_file=input_file, out_file=output_file, more_args=args)