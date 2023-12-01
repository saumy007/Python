#we use try keyword in python to do exception handling
a = input("enter the number ")
print("multiplication table of folowing")

try:
    for i in range(1,11):
        print(f"{int(a)}X{i} = {int(a)*(i)}")
except Exception as e:
    print("sorry bro cannot work")

print("sthis is working")
    