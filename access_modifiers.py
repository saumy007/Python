#access modifiers in python

class Employee:
    def __init__(self):
        self.name = "John"
        
a = Employee()
print(a.name) #public access modifier

# print(a._Employee__name) #can be accessed indirectly but not recommended
# print(a.__name) #private access modifier

print(dir(a)) #to see all attributes of the class
print("===============================")
print(a.__dir__()) #to see all attributes of the class
