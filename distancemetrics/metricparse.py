
def parse(s):
    return s.split(' ', 1)[0]

def format(s):
    name = s.split('Distance', 1)[0]

    return '\t\'' + name + '\': similarity.tsdist(\'' + s + '\'),'

s = input()
while s != None:
    print(format(parse(s)))
    try:
        s = input()
    except:
        s = None