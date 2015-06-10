
# returns a dictionary of testcases {fileName : groupIndexList)
def readTests():
    d = {}
    #f = open('testcases/truncated.txt')
    #f = open('testcases/formatted.txt')
    f = open('testcases/dtf_formatted.txt')
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
