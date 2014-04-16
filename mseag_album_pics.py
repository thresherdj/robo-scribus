#!/usr/bin/env python

"""
This script will read the captions.csv file designed for this process and look
for the photo album pictures and process them for the photo album.  It is
designed to run from within Scribus.  A lot of work still needs to be done with
dialogs and error reporting.

This script not only relys on Scribus but also needs ImageMagick's convert
utility and the pngnq utility too.  The pngnq utility handles the reduction of
the PNG files.  These two utilies are external and are called by the python
script to do their work.

AUTHOR: Dennis Drescher version: 2011.03.22

LICENSE: This program is free software; you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by the Free 
Software Foundation; either version 2 of the License, or (at your option) any 
later version.
"""

# FIXME: Another process needs to be added which will rename the files to a
# consitent name. That name should be inserted into the data file so the new
# name will map to the original name.

# FIXME: This should be turned into a lib and run along side the Scribus
# photo album script and each photo can be processed as needed by the script
# rather than doing all the processes at once. Also, once the photo was created,
# it would not need to do it on the next pass.

# Import libs
import sys, os, csv, codecs, shutil
import palaso.unicsv as csv
import operator


totalErrors = 0

# Set write protect to true to prevent re-processing of pictures
writeProtect = True

projHome = '/home/dennis/Publishing/MSEAG/PhotoAlbum/2012'

# Set the data file name (this must be a csv file in the MS Excel dialect)
dataFileName = os.path.join(projHome, 'data/data-2012-final.csv')
#dataFileName = os.path.join(projHome, 'data/test.csv')

# Make a dict of folders
folders = {
            'startingDir' : os.path.join(projHome, 'images/ready'),
            'procOneDir' : os.path.join(projHome, 'images/1-jpg-resize'),
            'procTwoDir' : os.path.join(projHome, 'images/2-shade-300'),
            'procThreeDir' : os.path.join(projHome, 'images/3-shade-72'),
            'procFourDir' : os.path.join(projHome, 'images/4-gray-300'),
            'procFiveDir' : os.path.join(projHome, 'images/5-gray-border-300'),
            'procSixDir' : os.path.join(projHome, 'images/6-color-border-300'),
            'procSevenDir' : os.path.join(projHome, 'images/7-gray-border-72'),
            'procEightDir' : os.path.join(projHome, 'images/8-color-border-72')
            }

# Create the folders
for f in folders.keys() : 
    if not os.path.isdir(folders[f]) :
        os.makedirs(folders[f])


# Define any necessary funtions here
def runCommand (command, output) :
    '''This will run a common sytem command and report any errors.  It will
    not overwrite exsiting files.'''

    error = 0
    if not os.path.isfile(output) :
        error = os.system(command)
        if error > 0 :
            # Output any error to log file
            recordError('Error found: ' + str(error))


def recordError (event) :
    '''Record an error report line to the error log object.  To reset the log
    file we will send it an empty event.'''

    global totalErrors
    log = 'errors.log'
    totalErrors +=1
    
    # Check for old log file
    if event == '' :
        if os.path.isfile(log) :
            os.remove(log)
            totalErrors -=1

    if os.path.isfile(log) :
        errorWriteObject = codecs.open(log, "a", encoding='utf_8')
    else :
        errorWriteObject = codecs.open(log, "w", encoding='utf_8')

    event = str(totalErrors) + ': ' + event
    errorWriteObject.write(event + '\n')
    errorWriteObject.close()


def crushPhoto (inFile, outFile) :
    '''This funtion will use pngnq to suck the fluff out of a PNG file.  This
    will fail if there is more than on '.' used in the file name.'''

    if os.path.isfile(inFile) :

        error = os.system('pngnq -f -e -tmp.png ' + inFile)
        if error > 0 :
            recordError('pngnq failed with: ' + str(error))

        tempFile = inFile.split('.')[0] + '-tmp.' + inFile.split('.')[1]
        if os.path.isfile(tempFile) :
            shutil.copy(tempFile, outFile)
            os.remove(tempFile)

    else :
        recordError('pngnq failed, file not found: ' + os.path.split(inFile)[1])


####################################################################################
################################# Main Process #####################################
####################################################################################


# Reset log
recordError('')

# Load up all the file and record information.
# Use CSV reader to build list of record dicts
if os.path.isfile(dataFileName) :
    records = list(csv.DictReader(open(dataFileName,'r')))
    # Now sort starting with least significant to greatest
    records.sort(key=operator.itemgetter('NameFirst'))
    records.sort(key=operator.itemgetter('NameLast'))
    totalRecs = len(records)
else :
    recordError('CSV Data not found: ' + dataFileName)

totalRecs = len(records)

# Start the main process here.  There are several things going on but we want to
# stay record-based as far as the count goes.
recCount = 1

# Process each picture seperatly
for r in records :

    # Begin the process (if the parent file is there)
    startImage = os.path.join(folders['startingDir'], r['Photo'])
    if os.path.isfile(startImage) :

        print 'Processing file #' + str(recCount) + ' of ' + str(len(records)) + ' records'
        
        # Step 1: Resize to common height (400px)
        if os.path.isfile(startImage) :
            endImage = os.path.join(folders['procOneDir'], r['Photo'])
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -resize x400 ' + endImage, endImage)
        else :
            recordError('Step 1, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'])

        # Step 2: Add a drop shadow (shade) to 300 dpi version.
        startImage = os.path.join(folders['procOneDir'], r['Photo'])
        # For the rest of the processes we need .png output. It is assumed
        # the original input file is in a .jpg format but we need to do
        # a little name fixing to complish this.
        currentImage = r['Photo'].replace('.jpg', '.png')
        if os.path.isfile(startImage) :
            endImage = os.path.join(folders['procTwoDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                # This will put a nice white border around it with a shadow as well (works with both .jpg and .png)
                runCommand('convert ' + startImage + ' -bordercolor white -border 13 \( +clone -background black -shadow 80x3+2+2 \) +swap -background white -layers merge +repage ' + endImage, endImage)
                # This will put just a shadow along the bottom and right side
#                runCommand('convert ' + startImage + ' \( +clone -background black -shadow 60x2+8+8 \) ' + '+swap -background none -mosaic ' + endImage, endImage)
        else :
            recordError('Step 2, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 3: This time we will use the pngnq utility to crush the
        # life out of the 300 dpi shadowed version.  This version can be
        # used for an electronic display.
        startImage = os.path.join(folders['procTwoDir'], currentImage)
        if os.path.isfile(startImage) :
            endImage = os.path.join(folders['procThreeDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                crushPhoto(startImage, endImage)
        else :
            recordError('Step 3, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 4: Using "convert" change the pics to gray color space,
        # set density to 300x300.
        startImage = os.path.join(folders['procTwoDir'], currentImage)
        if os.path.isfile(startImage) :
            endImage = os.path.join(folders['procFourDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -colorspace gray -density 300x300 ' + endImage, endImage)
        else :
            recordError('Step 4, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 5: Add a variable size border around the final that will
        # make the size of the image consistent with all the others.
        # The border is transparent so it can be used in a variety of
        # applications.
        startImage = os.path.join(folders['procFourDir'], currentImage)
        if os.path.isfile(startImage) :
            midImage = os.path.join(folders['procFiveDir'], 'temp.png')
            endImage = os.path.join(folders['procFiveDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -bordercolor transparent -border 100x20 -gravity center ' + midImage, endImage)
                runCommand('convert ' + midImage + ' -resize 800x600^ -background transparent -gravity center -extent 800x600 ' + endImage, endImage)
                # Do a little clean up if needed
                if os.path.isfile(midImage) :
                    os.remove(midImage)
        else :
            recordError('Step 5, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 6: Just like in step 5, add a variable size border, only
        # this time, do it to the color version.
        startImage = os.path.join(folders['procTwoDir'], currentImage)
        if os.path.isfile(startImage) :
            midImage = os.path.join(folders['procSixDir'], 'temp.png')
            endImage = os.path.join(folders['procSixDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -bordercolor transparent -border 100x0 -gravity center ' + midImage, endImage)
                runCommand('convert ' + midImage + ' -resize 800x600^ -background transparent -gravity center -extent 800x600 ' + endImage, endImage)
                # Do a little clean up if needed
                if os.path.isfile(midImage) :
                    os.remove(midImage)
        else :
            recordError('Step 6, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 7: Just like in step 6, add a variable size border, only
        # this time, do it to the gray version at 72 dpi.
        startImage = os.path.join(folders['procThreeDir'], currentImage)
        if os.path.isfile(startImage) :
            tmpOne = os.path.join(folders['procSevenDir'], 'temp1.png')
            tmpTwo = os.path.join(folders['procSevenDir'], 'temp2.png')
            tmpThree = os.path.join(folders['procSevenDir'], 'temp3.png')
            endImage = os.path.join(folders['procSevenDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -bordercolor transparent -border 100x0 -gravity center ' + tmpOne, endImage)
                runCommand('convert ' + tmpOne + ' -resize 800x600^ -background transparent -gravity center -extent 800x600 ' + tmpTwo, endImage)
                runCommand('convert ' + tmpTwo + ' -colorspace gray ' + tmpThree, endImage)
                crushPhoto(tmpThree, endImage)
                # Do a little clean up if needed
                if os.path.isfile(tmpOne) :
                    os.remove(tmpOne)
                if os.path.isfile(tmpTwo) :
                    os.remove(tmpTwo)
                if os.path.isfile(tmpThree) :
                    os.remove(tmpThree)
        else :
            recordError('Step 7, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

        # Step 8: Just like in step 6, add a variable size border, only
        # this time, do it to the color version at 72 dpi.
        startImage = os.path.join(folders['procThreeDir'], currentImage)
        if os.path.isfile(startImage) :
            tmpOne = os.path.join(folders['procEightDir'], 'temp1.png')
            endImage = os.path.join(folders['procEightDir'], currentImage)
            if not os.path.isfile(endImage) or not writeProtect :
                runCommand('convert ' + startImage + ' -bordercolor transparent -border 100x0 -gravity center ' + tmpOne, endImage)
                runCommand('convert ' + tmpOne + ' -resize 800x600^ -background transparent -gravity center -extent 800x600 ' + endImage, endImage)
                # Do a little clean up if needed
                if os.path.isfile(tmpOne) :
                    os.remove(tmpOne)
        else :
            recordError('Step 8, Rec: ' + str(recCount) + ' File not found: ' + r['Photo'].replace('.jpg', '.png'))

    else :
        print 'Error processing record #' + str(recCount) + '(file not found: ' + r['Photo'] + ')'
        recordError('Rec: ' + str(recCount) + ' File not found: ' + r['Photo'])

    # End the record file processing here
    recCount +=1



