#array code
import array

a1=array.array('i',[1,2,3,4,5,4,5,6,3,6,7,8])
a1.append(6)
a1.remove(6)
a1.remove(6)  
n=len(a1)
for i in range(n):
    print(a1[i], end=' ,')


