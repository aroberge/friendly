# Demonstration of a program that uses command line arguments
import sys

total = 0

for arg in sys.argv[1:]:
    total += float(arg)

if int(total) == total:
    total = int(total)

print("The sum is", total)
