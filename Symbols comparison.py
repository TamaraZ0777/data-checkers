# Ask user for input
text1 = input("Enter Text1: ")
text2 = input("Enter Text2: ")

# Find the longer length
max_length = max(len(text1), len(text2))

print("\nDifferences found:\n")

difference_found = False

# Compare character by character
for i in range(max_length):

    # Get character or placeholder if text is shorter
    char1 = text1[i] if i < len(text1) else "(no character)"
    char2 = text2[i] if i < len(text2) else "(no character)"

    # Compare characters
    if char1 != char2:
        difference_found = True
        print(f"Position {i}:")
        print(f"  Text1 -> {char1}")
        print(f"  Text2 -> {char2}")
        print()

# If no differences
if not difference_found:
    print("The texts are identical.")