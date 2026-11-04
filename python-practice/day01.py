# Day 01: Word Counting Practice

def count_words(text):
    words = text.split()
    return len(words)


document = """
Artificial Intelligence is changing the world.
Python is useful for AI development.
"""

total_words = count_words(document)

print("Total Words:", total_words)