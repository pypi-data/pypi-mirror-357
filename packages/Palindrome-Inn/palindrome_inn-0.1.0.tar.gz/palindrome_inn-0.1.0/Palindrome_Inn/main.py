import time
import argparse
import logging

def sleeping(fun):
    def wrapper(*args, **kwargs):
        time.sleep(1)
        val = fun(*args, **kwargs)
        return val
    return wrapper

@sleeping
def ispalindrome(word):
    return word == word[::-1]

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", required=True, help="Input file")
parser.add_argument("-o", "--output", required=True, help="Output file")
args = parser.parse_args()

if args.input is None or args.output is None:
    logging.error(logging.ERROR, "Please enter valid file names.")


try:
    with open(args.input, "r") as input_f:
        lines = input_f.readlines()
        for line in lines:
            if ispalindrome(line[:-1]):
                with open(args.output, "a+") as output_f:
                    output_f.write(line)
except FileNotFoundError:
    logging.error(logging.ERROR, "File is not found")


