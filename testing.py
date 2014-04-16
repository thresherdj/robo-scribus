#!/usr/bin/env python

import sys, os, csv


# Import libs
import palaso.unicsv as csv
import operator
from itertools import *
#from pprint import *


def sanitise (row) :
    '''Clean up a raw row input dict here.
    To do this we will add a "row =" for each step'''

    row = dict((k,v.strip()) for k,v in row.viewitems())
    return row


def select (row) :
    '''Acceptance conditions for a row, tested after sanitise has run.'''

    return row['NameFirst'] != ''

###############################################################################
########################### Script Setup Parameters ###########################
###############################################################################

# File locations
# Data file and path (this must be a csv file in the MS Excel dialect)
dataFileName = '/home/dennis/Publishing/MSEAG/PhotoAlbum/2012/data/data-2012-final.csv'
#dataFileName = '/home/dennis/Publishing/MSEAG/PhotoAlbum/2012/data/test.csv'

# Immage folder path
imagedir = '/home/dennis/Publishing/MSEAG/PhotoAlbum/2012/images/4-gray-300'


def loadCSVData (csvFile) :
    '''Load up the CSV data and return a dictionary'''

    if os.path.isfile(csvFile) :
        records = list(csv.DictReader(open(csvFile,'r')))
        records = list(filter(select,
                imap(sanitise, records)))

        # Now sort starting with least significant to greatest
        records.sort(key=operator.itemgetter('NameFirst'))
        records.sort(key=operator.itemgetter('NameLast'))
        return records
    else :
        result = scribus.messageBox ('File not Found', 'Data file: [' + csvFile + '] not found!', scribus.BUTTON_OK)

records         = loadCSVData(dataFileName)

c = 0


while c < len(records) :

    print records[c]['NameLast'] + ': ' + records[c]['NameFirst'] + ' [' + records[c]['Assignment'] + ']'
    
    c+=1
    

