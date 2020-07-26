# Demonstration of a program that uses command line arguments
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("numbers", nargs="*", help="List of numbers to add.")
parser.add_argument("--to_int", help="Converts the sum to integer", action="store_true")


total = 0
args = parser.parse_args()

for number in args.numbers:
    total += float(number)

if int(total) == total and args.to_int:
    total = int(total)

print("The sum is", total)
