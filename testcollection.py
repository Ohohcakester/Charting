
# returns a dictionary of testcases {fileName : groupIndexList)
def readTests():
    d = {}

    choice = 'dtf'
    testFileName = {
        'trun': 'testcases/fyh_truncated.txt',
        'fyh': 'testcases/fyh_formatted.txt',
        'dtf': 'testcases/dtf_formatted.txt',
        'rand1': 'testcases/rand1_formatted.txt',
        'rand2': 'testcases/rand2_formatted.txt',
        'rand3': 'testcases/rand3_formatted.txt', # small testcase
    }[choice]

    f = open(testFileName)
    for line in f:
        args = line.split(' ', 1)
        name = args[0]
        indexes = list(map(int, args[1].split(',')))
        d[name] = indexes
    f.close()
    return d
    

if __name__ == '__main__':
    d = readTests()
    print(d)

    total = sum(map(len, d.values()))
    print(str(total) + ' tests found')
