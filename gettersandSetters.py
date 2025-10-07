class MyClass:
    def __init__(self, name):
        self._name = name
        
        
    def show(self): # method
        print(f"Name: {self._name}")
        
        
    @property # getter function
    def ten_value(self ): 
        return self._name * 10
    
    
    @ten_value.setter
    def ten_value(self,new_name):
        self._name = new_name - 10

obj = MyClass(5)
obj.show()
obj.ten_value = 100
print(obj.ten_value)
obj.show()
obj.ten_value = 50
print(obj.ten_value)


