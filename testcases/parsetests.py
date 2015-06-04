
companyName = None
groupIndexes = []

def parse(s):
    global companyName, groupIndexes
    colon = s.find(':')
    if companyName == None:
        companyName = s
        return
    
    if colon == -1:
        print(companyName + ' ' + ','.join(groupIndexes))
        companyName = s
        groupIndexes = []
    else:
        index = s[:colon]
        groupIndexes.append(index)
        
        


s = input()
while s != None:
    parse(s)
    try:
        s = input()
    except:
        s = None