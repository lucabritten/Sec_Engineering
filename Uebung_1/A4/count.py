import math


print("Testing entropy of german words: ")
with open("wortliste-ger.txt") as words:
    lines  = sum(1 for lines in words)
    entropy = math.log2(lines)
    print(f"Total number of lines: {lines}")
    print(f"According entropy german words: {entropy}")

print("\n==============")
with open("wordlist-en.txt") as words:
    lines  = sum(1 for lines in words)
    entropy = math.log2(lines)
    print(f"Total number of lines: {lines}")
    print(f"According entropy english words: {entropy}")
