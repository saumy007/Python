class MyClass:
    def __init__(self, name):
        self._name = name   # underscore → “private” convention

    def get_name(self):      # getter
        return self._name

    def set_name(self, value):  # setter
        if isinstance(value, str):  # validation
            self._name = value
        else:
            print("Name must be a string!")

obj = MyClass("indirect access is working")
print(obj.get_name())   # call getter
obj.set_name("Direct access is working here")    # call setter
print(obj.get_name())
obj.set_name(123)       # validation kicks in
