#factorial function in python
#factorial(7) = 7*6*5*4*3*2*1
#factorial(6) = 6*5*4*3*2*1
#factorial(5) = 5*4*3*2*1

def factorial(n):
    if(n == 1 or n == 0):
        return 1
    else:
        return n * factorial(n-1)

print (factorial(3))
print (factorial(4))
print (factorial(5))