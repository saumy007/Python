def my_decorator(func):
    def wrapper():
        print("Decorator says hello 👋")
        return func()   # call the original function
    return wrapper


@my_decorator
def evening():
    print("Good Evening")
    def time():
        print("Time is 10:00 AM")
    return time

f = evening()
f()