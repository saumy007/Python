import re

# Example text
text = "Hello, my email is john.doe@example.com."

# Define a pattern for matching email addresses
pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Use re.search() to find the pattern in the text
match = re.search(pattern, text)

if match:
    print("Found email:", match.group())
else:
    print("Email not found.")
