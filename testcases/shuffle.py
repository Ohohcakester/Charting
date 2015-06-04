

li = []
s = input()
while s != None:
    li.append(s)
    try:
        s = input()
    except:
        s = None
   
import random
random.shuffle(li)
for s in li[0:10]:
    print(s)