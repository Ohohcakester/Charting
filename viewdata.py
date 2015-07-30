import os
import parameters as para

dataPaths = {
    'original': 'data_/',
    '211111': 'data_211111/',
    '334111': 'data_334111/',
    '454111': 'data_454111/',
}


path = dataPaths['original']
data = None
headers = None


""" REGION: USER COMMANDS - START """
# In this region, we define the commands a user can make.

def getCompany(substr):
    global data, headers
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
        return out('Multiple Matches Found: \n', '\n'.join(map(lambda s : '  '+str(s),matches)))
    else: #len(matches) == 1
        data, headers = para.readFile(path + matches[0])
        return out('Loaded data, headers from ', matches[0])


def printHeaders():
    out('Parameters:\n', headers)


def viewData(parameter, index):
    parameter = fixDatatypeCase(parameter)
    index = int(index)
    if parameter not in data: return error('Unknown parameter')
    datalist = data[parameter]
    if index > len(datalist): return error('Index out of range. Length: ', len(datalist))

    out(datalist[index])


def find(parameter, value):
    parameter = fixDatatypeCase(parameter)
    if parameter not in data: return error('Unknown parameter')
    datalist = data[parameter]
    found = False
    for i in range(0,len(datalist)):
        if str(datalist[i]) == str(value):
            out('index ', i, ': ', datalist[i])
            found = True
    if not found:
        out('No matches found')


def choosePath(pathName):
    if pathName not in dataPaths:
        return errorLong('Invalid path name "' + pathName + '".',
                         'Valid path names:',
                         *map(lambda s : "  '"+s+"'", dataPaths.keys()))
    path = dataPaths[pathName]


def printHelp():
    def format(key, value):
        return '  ' + str(key) + ' : ' + str(value[1])

    manual = [format(key,value) for key, value in commands.items()]

    outLong('Command List:', *manual)

def manual(command):
    if command not in commands:
        out('There is no such command: ', command)
    out(command, ' : ', commands[command][1])

""" REGION: USER COMMANDS - END """

""" REGION: HELPER FUNCTIONS - START """

def fixDatatypeCase(parameter):
    return parameter[0].upper() + parameter[1:].lower()


def unload():
    global data, headers
    data = None
    headers = None

""" REGION: HELPER FUNCTIONS - END """



""" REGION: CONTROL FUNCTIONS - START """

def error(*msgs):
    print('Error: ' + ''.join(map(str,msgs)))

def errorLong(*msgs):
    print('Error: ' + '\n'.join(map(str, msgs)))

def out(*msgs):
    print(''.join(map(str,msgs)))

def outLong(*msgs):
    print('\n'.join(map(str,msgs)))

""" REGION: CONTROL FUNCTIONS - END """

# Define the commands here. (keyword => function)
commands = {
    'help': (printHelp, 'Prints the list of commands'),
    'load': (getCompany, 'Load data, headers from a file (company)'),
    'path': (choosePath, 'Choose the directory to load from'),
    'quit': (quit, 'Exits the program'),
    'parameters': (printHeaders, 'Prints a list of usable parameters'),
    'view': (viewData, 'Display the data of a parameter at a specific index'),
    'find': (find, 'Look for indexes where the parameter matches an input'),
    'man': (manual, 'Gives a short description of a command'),
}

# Used by main() to parse a user's input.
def parse(cmd):
    args = cmd.split()
    if len(args) < 1: return error('Parse error')
    cmd = args[0]
    args = args[1:]
    if cmd not in commands: return error('Command not found')

    try:
        commands[cmd][0](*args)
    except TypeError as e:
        error('Wrong Arguments\n', e)


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