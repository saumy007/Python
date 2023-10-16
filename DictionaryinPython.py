#Dictionary is unordered pair 
#In Python Sets are ordered Pair
ep1 ={122:25,102: 55, 505:23}
ep2 ={210:25,226: 26, 527: 69, 45: "Saumy is here"}
ep2.update(ep1)
print(ep2)
print(ep1)
ep1.pop(122)
print(ep1)