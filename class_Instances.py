class employee:
    name = "first name"
    age = 0
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display_info(self):
        print(f"Name: {self.name}, Age: {self.age}")
        
    def shoes(self, shoe):
        self.shoe = shoe
        print(f"{self.name} wears size {self.shoe} shoes.")
        
e1 = employee("Alice", 30)
e1.display_info()

e1.name = "Bob"
e1.age = 25
e1.display_info()