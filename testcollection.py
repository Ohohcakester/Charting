
# The default test collection to use if chooseCollection is not specified.
defaultCollection = 'trun'

# The possible choices of test collections.
# In the format key => value
# Where key refers to the handle name of the collection (to be used when choosing collections)
# And value refers to the path where the collection text file resides.
testCollectionChoices = {
    'trun': 'testcases/fyh_truncated.txt',
    'fyh': 'testcases/fyh_formatted.txt',
    'dtf': 'testcases/dtf_formatted.txt',
    'rand1': 'testcases/rand1_formatted.txt',
    'rand2': 'testcases/rand2_formatted.txt',
    'rand3': 'testcases/rand3_formatted.txt', # small testcase
}

# returns a dictionary of testcases {fileName : groupIndexList)
def readTests(chooseCollection = None):
    global defaultCollection, testCollectionChoices
    
    if chooseCollection == None: chooseCollection = defaultCollection
    testFileName = testCollectionChoices[chooseCollection]

    d = {}
    f = open(testFileName)
    for line in f:
        args = line.split(' ', 1)
        name = args[0]
        indexes = list(map(int, args[1].split(',')))
        d[name] = indexes
    f.close()
    return d
    

# Run this script to count the number of test cases in a test collection.
if __name__ == '__main__':
    d = readTests()
    print(d)

    total = sum(map(len, d.values()))
    print(str(total) + ' tests found')
