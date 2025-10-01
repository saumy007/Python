class Person:
    def __init__(self,n,o):
        print("hey this is saumy")
        self.name = n
        self.occ = o
    def info(self):
        print(f"{self.name} is a {self.occ}")





a = Person("saumy","I am here")
a.info()
