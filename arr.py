#array code
import array

a1=array.array('i',[1,2,3,4,5])
n=len(a1)
for i in range(n):
    print(a1[i], end=' ,')