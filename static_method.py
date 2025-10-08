#static method can be used to ship with the class and make it accessible without using self keyword
class Math():
    def __init__(self, num):
        #num = self.num
        self.num = num
        
        
    def add_to_num(self, n):
        self.num = self.num + n
        return self.num
        
    @staticmethod
    def add(x, y):
        return x + y
    
m = Math(10)
print(m.add_to_num(20))

print(m.add(5,10))
    
    