#finally clause
try:
    list = [5,4,2,1]
    i = int(input("Enter the index: "))
    print(l[i])
except:
    print("Some error is here")
finally:
    print("This will show up Regardless of whatever")
