a = int(input("Enter the Value between 5 and 9"))
if(a<5 or a>9):
    raise ValueError("the value if out of bounds and should be between 9 and 5")