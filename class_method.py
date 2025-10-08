#class methods are used to change the class variables used because first variable in a method call is always an object
'''
In Python, a class method is a method that belongs to the class rather than an instance of the class. To define it, you use the @classmethod decorator.

Key points about @classmethod:

It takes the class (cls) as the first argument instead of the instance (self).

It can access or modify class-level state, but not instance-specific data.

It’s often used as factory methods — alternative ways to create objects.


'''

class Student:
    school_name = "OpenAI Academy"
    age = 25
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    @classmethod
    def change_school(cls, new_name, age):
        cls.school_name = new_name
        cls.age = age
        

# Normal method call via object
s1 = Student("Alice", 20)
print(s1.school_name, s1.age)  # OpenAI Academy

# Call class method via class
Student.change_school("DeepMind Institute", 35)
print(Student.school_name,Student.age)  # DeepMind Institute