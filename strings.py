#strings 
a = '''
Hi I am Saumy Sharma
and this 
is multiline 
wording 
u can also use \n for this 
okay let me try \n this should be in new line

'''
print(a)

name = "Saumy!!!!!!!!!!!!"
print(name[0])
print(name[1])
print(name[2])
print(name[3])

print("lets use a for loop here")
for character in name:
    print(character)
#String slicing in python
print(name[0:-3])#this is len of fruit minus 3
'''
strings are  immutable

'''
print(name.upper())
print(name.lower())
print(name.rstrip("!"))
print(name.replace("!", "@"))
#capitalize
name1 = "this is capiutalize method"
print(name1.capitalize())
print(len(name1))
print(name1.center())



