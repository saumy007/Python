claim = "pluto is the planet"
print(claim.lower())
print(claim.index('u'))
'''Going between strings and lists: .split() and .join()
str.split() turns a string into a list of smaller strings, breaking on whitespace by default. This is super useful for taking you from one big string to a list of words.'''
words = claim.split()
print(words)
'''
to split other than white spaces we have to use it like this
'''
datestr = '1956-04-08'
year, month, day = datestr.split('-')
print(year, month, day)
'''
to join we have to use '/'.join
'''

print('/'.join([month, day, year]))
'''
we can concantinate strings in python as well 
'''

con = str(words)+  " " + claim + 'this is new'
print(con)
"{}, you'll always be the {}th planet to me.".format(planet, position)




