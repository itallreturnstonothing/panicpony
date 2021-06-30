from datetime import datetime, timezone
import math
import argparse

api_key = "AIzaSyA-dlBUjVQeuc4a6ZN4RkNUYDFddrVLxrA"

consent_cookies = {"CONSENT": "YES+cb.20210622-13-p0.en+FX+677"}

# const
critical_datetime = datetime(year=2017, month=1, day=2, tzinfo=timezone.utc)
# january 2 just to be safe

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

def print_or_not(message):
    global quiet
    if not quiet:
        print(message)

def set_quiet(set_to):
    global quiet
    quiet = set_to

def parse_args(add_options_callback):
    global api_key
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Optional API key to use. There is a default key.")
    add_options_callback(parser)

    args = parser.parse_args()

    if args.key:
        api_key = args.key
    
    return args