#MAP
def cube(x):
    
    return x*x*x

print(cube(2))

l = [1,2,4,6,7]

newl = list(map(cube,l))
print(newl)

#FILTER

def filter_function(a):
    return a>4

newlnewl = list(filter(filter_function,l))
print(newlnewl)

#REDUCE
#requires import called reduce

from functools import reduce

def mysum(x,y):
    return(x+y)

numbers =[1,2,3,4,5]
sum = reduce(mysum,numbers)

print(sum)




