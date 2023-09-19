#functions 
#program to find g mean
def mean(a,b):
    mean = a+b/(a+b)
    print("The average is ",mean)

d = 100
f = 100
mean(d,f)

def mean2(*numbers):
    #print tuples
    sum = 0
    for i in numbers:
        sum = sum + i
    print("Average is given here",sum)

mean2(20,30)

