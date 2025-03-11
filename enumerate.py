# Example of using enumerate() in Python

# Simple list of fruits
fruits = ['apple', 'banana', 'orange', 'grape']

# Basic enumerate usage
print("Basic enumeration:")
for index, fruit in enumerate(fruits):
    print(f"Index {index}: {fruit}")

# Enumerate with custom start index
print("\nEnumerate with start index = 1:")
for index, fruit in enumerate(fruits, start=1):
    print(f"Index {index}: {fruit}")

# Using enumerate in a list comprehension
indexed_fruits = list(enumerate(fruits))
print("\nEnumerate in a list:", indexed_fruits)