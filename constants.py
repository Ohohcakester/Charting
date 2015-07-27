""" This file stores all the constants that are used by the scripts. """

# The size of the groups to use for analysis.
# Note: When you modify this, please modify ma as well.
# groupSize = 75 is 3.5 months. ma should be larger than this number.
groupSize = 75


# ma: months ahead
# When running a test on an algorithm, we try to predict the values of a group a few months ahead.
# This number should be larger than the number of months in groupSize (so that you aren't predicting values you already know)
# Note that there is one group per month.
ma = 4