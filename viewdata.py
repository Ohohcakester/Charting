import os
import traceback
import parameters as para

"""doc
viewdata.py
This is a somewhat standalone program used to query data from the files.



"""

dataPaths = {
    'original': 'data_/',
    '211111': 'data_211111/',
    '334111': 'data_334111/',
    '454111': 'data_454111/',
}


path = dataPaths['original']
data = None
headers = None

def error(*msgs):
    print('Error: ' + ''.join(map(str,msgs)))

def out(*msgs):
    print(''.join(map(str,msgs)))

def getCompany(substr):
    global path, data, headers
    if path == None:
        return error('No path specified')

    files = os.listdir(path)
    substr = substr.lower()
    substr = substr.replace(' ', '_')
    matches = list(filter(lambda name : substr in name.lower(), files))

    unload()
    if len(matches) == 0:
        return error('No matches found')
    elif len(matches) > 1:
        return out('Matches: ', ', '.join(map(str,matches)))
    else: #len(matches) == 1
        data, headers = para.readFile(path + matches[0])
        return out('Loaded ', matches[0])

def printHeaders():
    global headers
    out(headers)

def fixDatatypeCase(datatype):
    return datatype[0].upper() + datatype[1:].lower()


def viewData(datatype, index):
    global data
    datatype = fixDatatypeCase(datatype)
    index = int(index)
    if datatype not in data: return error('Unknown type')
    datalist = data[datatype]
    if index > len(datalist): return error('Index out of range. Length: ', len(datalist))

    out(datalist[index])

def find(datatype, value):
    global data
    datatype = fixDatatypeCase(datatype)
    if datatype not in data: return error('Unknown type')
    datalist = data[datatype]
    found = False
    for i in range(0,len(datalist)):
        if str(datalist[i]) == str(value):
            out('index ', i, ': ', datalist[i])
            found = True
    if not found:
        out('No matches found')


def unload():
    global data, headers
    data = None
    headers = None


def choosePath(pathName):
    global data, headers, dataPaths, path
    path = dataPaths[pathName]


commands = {
    'load': getCompany,
    'path': choosePath,
    'exit': quit,
    'quit': quit,
    'header': printHeaders,
    'view': viewData,
    'find': find,
}

def parse(cmd):
    global commands
    args = cmd.split()
    if len(args) < 1: return error('Parse error')
    cmd = args[0]
    args = args[1:]
    if cmd not in commands: return error('Command not found')

    commands[cmd](*args)



def main():
    s = input('>> ')
    while True:
        parse(s)
        try:
            s = input('>> ')
        except:
            s = None

if __name__ == '__main__':
    main()