class Person:
    name = "Saumy"
    occupation = "developer"
    networth = 10
    def info(self):
        print(f"{self.name} is a {self.occupation}")


a = Person()
b = Person()

a.name = "Sam"
a.occupation = "Person"


print(a)