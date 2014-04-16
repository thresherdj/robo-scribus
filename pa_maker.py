#!/usr/bin/env python

'''
__version__ = '0.1.r004'
__date__    = '28 February 2014'
__author__  = 'Dennis Drescher <dennis_drescher@sil.org>'
__credits__ = \

Original ideas for this script came from the scribalbum_letter.py script by 
Gregory Pittman, version: 2008.07.23.

#############################################

LICENSE:

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
'''

###############################################################################
######################### Description/Documentation ###########################
###############################################################################

# This is a Scribus script that will insert data for a photo album into a 
# document that it creates. It will also process and insert the photos as well.
# This script is based on three row per page layout.


###############################################################################
############################# Initialize Module ###############################
###############################################################################

# Import Python modules
import sys, os, csv, subprocess, re

# Set up the lib environment
sys.path.insert(0, os.path.join(os.getcwd(), 'lib'))




# Import libs
import      scribus
import      palaso.unicsv as csv
import      operator
from        itertools                       import *

# Import local pa libs
from        pa_maker.process.img_process    import ImgProcess


class PAMaker (object) :

    def __init__ (self, parent=None) :
        '''Initialize and start up the script'''

#        import pdb; pdb.set_trace()

        self.img_process        = ImgProcess()

###############################################################################
########################### Script Setup Parameters ###########################
###############################################################################

        # This first set of vars are set by the user
        self.mode               = 'draft' # Whatever is inserted here will be the watermark
        self.projectDir         = '/home/dennis/Publishing/MSEAG/CPA2014'
        # Data file must be a csv file in the MS Excel dialect
        self.dataFileName       = 'ConferencePhotoBook-20140322.csv'
#        self.dataFileName       = 'test.csv'
        # Max height for print will be around 800-1000px, electronic view 200-400px
        self.maxHeight          = '1000'
        # Image density is 96 for electronic display and 300 for print
        self.imgDensity         = '300'
        # Turn on watermark (output mode)
        self.outputWatermark    = False
        # Have Scribus create/export the PDF
        self.makePdf            = True
        # View the PDF after it has been made
        self.viewPdf            = True
        # Use PNG images for lossless quality
        self.willBePngImg       = True
        # If Gray-scale color space is needed set to False
        self.rgbColor           = False
        # If hyphenation is wanted
        self.hyphenate          = False
        # Use page numbers?
        self.pageNumbers        = False

        # The following are auto generated vals
        self.dataDir            = os.path.join(self.projectDir, 'data')
        self.draftDir           = os.path.join(self.projectDir, 'draft')
        self.proofDir           = os.path.join(self.projectDir, 'proof')
        self.finalDir           = os.path.join(self.projectDir, 'final')
        self.deliverableDir     = os.path.join(self.projectDir, 'deliverable')
        self.imagesDir          = os.path.join(self.projectDir, 'images')
        self.orgImgDir          = os.path.join(self.imagesDir, 'org')
        self.jpgImgDir          = os.path.join(self.imagesDir, 'jpg')
        self.pngImgDir          = os.path.join(self.imagesDir, 'png')
        self.placeholderPic     = os.path.join(self.imagesDir, 'profile.png')
        self.watermark          = self.mode.upper()

# FIXME: File naming needs to use current dates, not the data set, gets confusing otherwise
#        Also, we need to add a name for the Scribus document as well and auto save it
#        when we get to that part of the process. The mode should be added to the name as well.

        # The PDF output location is determined by the mode
        self.pdfFile            = os.path.join(getattr(self, self.mode + 'Dir'), self.dataFileName.replace('csv', 'pdf'))
        self.dataFile           = os.path.join(self.dataDir, self.dataFileName)

        # Set the caption font info (font must be present on the system)
        self.fonts = {
                        'verse'     : {'regular' : 'Gentium Basic Regular', 'bold' : 'Gentium Basic Bold', 
                                            'italic' : 'Gentium Basic Italic', 'boldItalic' : 'Gentium Basic Bold Italic', 
                                                'size' : 9},
                        'nameLast'  : {'regular' : 'Arial Regular', 'bold' : 'Arial Bold', 'italic' : 'Arial Italic', 
                                        'boldItalic' : 'Arial Bold Italic', 'size' : 22},
                        'nameFirst' : {'regular' : 'Arial Regular', 'bold' : 'Arial Bold', 'italic' : 'Arial Italic', 
                                        'boldItalic' : 'Arial Bold Italic', 'size' : 10},
                        'text'      : {'regular' : 'Gentium Basic Regular', 'bold' : 'Gentium Basic Bold', 
                                        'italic' : 'Gentium Basic Italic', 'boldItalic' : 'Gentium Basic Bold Italic', 
                                        'size' : 11},
                        'pageNum'   : {'regular' : 'Gentium Basic Regular', 'bold' : 'Gentium Basic Bold', 
                                        'size' : 12}
                      }

        # Page dimension information (in points)
        self.dimensions  = {
                            'page'      : {'height' : 595, 'width' : 421, 'scribusPageCode' : 'PAPER_A5'},
                            'margins'   : {'left' : 30, 'right' : 30, 'top' : 40, 'bottom' : 20},
                            'rows'      : {'count' : 3}
                            }

        # Create project folders if necessary
        if not os.path.exists(self.projectDir) :
            os.makedirs(self.projectDir)
        if not os.path.exists(self.dataDir) :
            os.makedirs(self.dataDir)
        if not os.path.exists(self.draftDir) :
            os.makedirs(self.draftDir)
        if not os.path.exists(self.proofDir) :
            os.makedirs(self.proofDir)
        if not os.path.exists(self.finalDir) :
            os.makedirs(self.finalDir)
        if not os.path.exists(self.deliverableDir) :
            os.makedirs(self.deliverableDir)
        if not os.path.exists(self.imagesDir) :
            os.makedirs(self.imagesDir)
        if not os.path.exists(self.orgImgDir) :
            os.makedirs(self.orgImgDir)
        if not os.path.exists(self.jpgImgDir) :
            os.makedirs(self.jpgImgDir)
        if not os.path.exists(self.pngImgDir) :
            os.makedirs(self.pngImgDir)

###############################################################################
################################## Functions ##################################
###############################################################################

    def getCoordinates (self, dim) :
        '''Return a dictionary with all the coordinates for all elements on 
        a page.'''

        coords = []
        rows = dim['rows']['count']
        r = 0
        while r < rows :

            # Build some repeating coords and dimensions
            bodyYPos                = dim['margins']['top'] + 1
            bodyXPos                = dim['margins']['left'] + 1
            bodyHeight              = dim['page']['height'] - (dim['margins']['top'] + dim['margins']['bottom']) - 2
            bodyWidth               = dim['page']['width'] - (dim['margins']['left'] + dim['margins']['right']) - 2
            rowHeight               = ((bodyHeight / rows) * 0.8) - 1
            rowWidth                = bodyWidth -1
            rowVerticalGap          = (bodyHeight - (rowHeight * rows)) / (rows - 1)
            if r == 0 :
                rowYPos             = bodyYPos
            else :
                rowYPos             = bodyYPos + (rowHeight + rowVerticalGap) * r

            rowXPos                 = bodyXPos
            nameLastHeight          = (self.fonts['nameLast']['size'] * 1.3) + 2
            nameFirstHeight         = (self.fonts['nameFirst']['size'] * 1.5) + 2
            imageHeight             = (rowHeight - nameFirstHeight) - 1
            imageWidth              = (bodyWidth / 2) - 2
            pageNumWidth            = bodyWidth * 0.05

            # Append a dict of the coords for this row
            coords.append({
                'bodyYPos'          : bodyYPos,
                'bodyXPos'          : bodyXPos,
                'bodyHeight'        : bodyHeight,
                'bodyWidth'         : bodyWidth,
                'rowYPos'           : rowYPos,
                'rowXPos'           : rowXPos,
                'rowHeight'         : rowHeight,
                'rowWidth'          : rowWidth,
                'rowVerticalGap'    : rowVerticalGap,
                'nameLastYPos'      : rowYPos + rowHeight,
                'nameLastXPos'      : rowXPos,
                'nameLastHeight'    : nameLastHeight,
                'nameLastWidth'     : rowHeight,
                'nameFirstYPos'     : rowYPos,
                'nameFirstXPos'     : rowXPos + nameLastHeight + 1,
                'nameFirstHeight'   : nameFirstHeight,
                'nameFirstWidth'    : imageWidth * 1.25,
                'imageYPos'         : rowYPos + nameFirstHeight + 1,
                'imageXPos'         : rowXPos + nameLastHeight + 1,
                'imageHeight'       : imageHeight,
                'imageWidth'        : imageWidth,
                'countryYPos'       : rowYPos,
                'countryXPos'       : rowXPos + nameLastHeight + imageWidth + 2,
                'countryHeight'     : nameFirstHeight,
                'countryWidth'      : rowWidth - (nameLastHeight + imageWidth) - 1,
                'assignYPos'        : rowYPos + nameFirstHeight + 1,
                'assignXPos'        : rowXPos + nameLastHeight + imageWidth + 2,
                'assignHeight'      : (rowHeight - nameFirstHeight) * 0.3,
                'assignWidth'       : rowWidth - (nameLastHeight + imageWidth) - 1,
                'verseYPos'         : (rowYPos + nameFirstHeight) + (rowHeight - nameFirstHeight) * 0.35,
                'verseXPos'         : rowXPos + nameLastHeight + imageWidth + 2,
                'verseHeight'       : (rowHeight - nameFirstHeight) * 0.60,
                'verseWidth'        : rowWidth - (nameLastHeight + imageWidth) - 1,
                'pageNumYPos'       : bodyYPos - nameFirstHeight,
                'pageNumXPosOdd'    : bodyXPos + bodyWidth - (pageNumWidth - 1),
                'pageNumXPosEven'   : bodyXPos - pageNumWidth + (pageNumWidth - 1),
                'pageNumHeight'     : nameFirstHeight - 5,
                'pageNumWidth'      : pageNumWidth
            })

            # Move to the next row
            r +=1

        return coords


    def loadCSVData (self, csvFile) :
        '''Load up the CSV data and return a dictionary'''

        if os.path.isfile(csvFile) :
            records = list(csv.DictReader(open(csvFile,'r')))
            records = list(filter(self.select,
                    imap(self.sanitise, records)))

            # Now sort starting with least significant to greatest
            records.sort(key=operator.itemgetter('NameFirst'))
            records.sort(key=operator.itemgetter('NameLast'))
            return records
        else :
            result = scribus.messageBox ('File not Found', 'Data file: [' + csvFile + '] not found!', scribus.BUTTON_OK)


    def setPageNumber (self, crds, pageSide, row, pageNumber) :
        '''Place the page number on the page if called for.'''

        if self.pageNumbers :
            # Make the page number box
            pNumBox = scribus.createText(crds[row]['pageNumXPos' + pageSide], crds[row]['pageNumYPos'], crds[row]['pageNumWidth'], crds[row]['pageNumHeight'])
            # Put the page number in it and format according to the page we are on
            scribus.setText(`pageNumber`, pNumBox)
            if pageSide == 'Odd' :
                scribus.setTextAlignment(scribus.ALIGN_RIGHT, pNumBox)
            else:
                scribus.setTextAlignment(scribus.ALIGN_LEFT, pNumBox)

            scribus.setFont(self.fonts['pageNum']['bold'], pNumBox)
            scribus.setFontSize(self.fonts['pageNum']['size'], pNumBox)


    def sanitise (self, row) :
        '''Clean up a raw row input dict here.
        To do this we will add a "row =" for each step'''

        row = dict((k,v.strip()) for k,v in row.viewitems())
        return row


    def select (self, row) :
        '''Acceptance conditions for a row, tested after sanitise has run.'''

        return row['NameFirst'] != ''


    def addWatermark (self) :
        '''Create a Draft watermark layer. This was taken from:
            http://wiki.scribus.net/canvas/Adding_%27DRAFT%27_to_a_document'''

        L = len(self.watermark)                         # The length of the word 
                                                        # will determine the font size
        scribus.defineColor("gray", 11, 11, 11, 11)     # Set your own color here

        u  = scribus.getUnit()                          # Get the units of the document
        al = scribus.getActiveLayer()                   # Identify the working layer
        scribus.setUnit(scribus.UNIT_MILLIMETERS)       # Set the document units to mm,
        (w,h) = scribus.getPageSize()                   # needed to set the text box size

        scribus.createLayer("c")
        scribus.setActiveLayer("c")

        T = scribus.createText(w/6, 6*h/10 , h, w/2)    # Create the text box
        scribus.setText(self.watermark, T)              # Insert the text
        scribus.setTextColor("gray", T)                 # Set the color of the text
        scribus.setFontSize((w/210)*(180 - 10*L), T)    # Set the font size according to length and width

        scribus.rotateObject(45, T)                     # Turn it round antclockwise 45 degrees
        scribus.setUnit(u)                              # return to original document units
# FIXME: It would be nice if we could move the watermark box down to the lowest layer so 
# that it is under all the page text. Have not found a method to do this. For now we just
# plop the watermark on top of everything else.
        scribus.setActiveLayer(al)                      # return to the original active layer


    def fixText (self, text) :
        '''Fix common format problems like quote markers, etc.'''

        # Strip out problems characters
        text = re.sub(ur'\u200B', ur'', text)
        # Possessive marker
        text = re.sub(ur'([a-zA-Z])\u0027s', ur'\1\u2019s', text)
        # Abbreviation marker (we hope)
        text = re.sub(ur'([a-zA-Z])\u0027([a-zA-Z])', ur'\1\u2019\2', text)
        # Single open quote (start of line)
        text = re.sub(ur'^\u0027', ur'\u2018', text)
        # Single close quote (end of line)
        text = re.sub(ur'\u0027$', ur'\u2019', text)
        # Single open quote 
        text = re.sub(ur'\s\u0027', ur' \u2018', text)
        # Single close quote
        text = re.sub(ur'\u0027([\"\s\.\?\,])', ur'\u2019\1', text)
        # Double open quote (start of line)
        text = re.sub(ur'^\u0022', ur'\u201C', text)
        # Double close quote (end of line)
        text = re.sub(ur'\u0022$', ur'\u201D', text)
        # Double open quote (w/dash or space)
        text = re.sub(ur'([\-\s])\u0022', ur'\1\u201C', text)
        # Double close quote
        text = re.sub(ur'\u0022([\s\.\?\,])', ur'\u201D\1', text)
        # Em dash
        text = re.sub(ur'\u002D\u002D', ur'\u2014', text)
        text = re.sub(ur'\s\u002D\s', ur'\u2014', text)
        text = re.sub(ur'\s?\u007E\s?', ur'\u2014', text)
        # Ellipsis
        text = re.sub(ur'\.\.\.', ur'\u2026', text)

        return text


    def findVerseRef (self, text) :
        '''Look for and return any verse references found in
        a string. This will break if there is more than one
        ref used in a string. :-( '''

        if re.search(ur'.+(\([0-9a-zA-Z]+\..+\))', text) :
            return re.sub(ur'.+(\([0-9a-zA-Z]+\..+\))', ur'\1', text)


    def removeVerseRef (self, text) :
        '''Remove a verse ref from a string.'''

        return re.sub(ur'(.+)\s(\([0-9a-zA-Z]+\..+\))', ur'\1', text)


    def resizeFrame (self, frame) :
        '''Resize a frame in place so that it fits the text inside it.
        Code for this was take from: 
        http://wiki.scribus.net/canvas/Adjust_a_text_frame_to_fit_its_content'''

        # Now adjust the frame to fit the text
        # get some page and frame measure
        (x, ph) = scribus.getPageSize();
        (x, x, x, pm) = scribus.getPageMargins(); # warning: gets the margins from document setup not for the current page
        (x, y) = scribus.getPosition(frame)
        bottom = (ph - pm) - y
        (w, h) = scribus.getSize(frame)
        # if the frame doesn't overflow, shorten it to make it overflow
        while (((scribus.textOverflows(frame) == 0) or (h > bottom)) and (h > 0)) :
            h -= 10
            scribus.sizeObject(w, h, frame)
        # resize the frame in 10pt steps
        while ((scribus.textOverflows(frame) > 0) and (h < bottom)) :
            h += 10
            scribus.sizeObject(w, h, frame)
        # undo the latest 10pt step and fine adjust in 1pt steps
        h -= 10
        scribus.sizeObject(w, h, frame)
        while ((scribus.textOverflows(frame) > 0) and (h < bottom)) :
            h += 1
            scribus.sizeObject(w, h, frame)

        # For vertical sizing operations return the frame height
        return int(scribus.getSize(frame)[1])


###############################################################################
########################## Start the main process #############################
###############################################################################

    def main (self) :

        # Load up all the file and record information.
        # Use CSV reader to build list of record dicts
        records         = self.loadCSVData(self.dataFile)
        totalRecs       = len(records)

        # Reality check first to see if we have anything to process
        if totalRecs <= 0 :
            scribus.messageBox('Not Found', 'No records found to process!')
            sys.exit()

        pageNumber      = 1
        recCount        = 0
        row             = 0
        pageSide        = 'Odd'
        scribus.progressTotal(totalRecs)
        paIndex         = {}
        lastName        = ''
        firstName       = ''
        photoFirstName  = ''
        verseRef        = ''
        verseText       = ''

        # Get the page layout coordinates for this publication
        crds = self.getCoordinates(self.dimensions)

        # Make a new document to put our records on
        if scribus.newDocument(getattr(scribus, self.dimensions['page']['scribusPageCode']), 
                    (self.dimensions['margins']['left'], self.dimensions['margins']['right'], self.dimensions['margins']['top'], self.dimensions['margins']['bottom']),
                        scribus.PORTRAIT, 1, scribus.UNIT_POINTS, scribus.NOFACINGPAGES, 
                            scribus.FIRSTPAGERIGHT, 1) :

            self.setPageNumber(crds, pageSide, row, pageNumber)

            while recCount < totalRecs :

                # Output a new page on the first row after we have done the first page
                if row == 0 and recCount != 0:
                    scribus.newPage(-1)
                    if pageSide == 'Odd' :
                        pageSide = 'Even'
                    else :
                        pageSide = 'Odd'

                    self.setPageNumber(crds, pageSide, row, pageNumber)

                ########### Now set the current record in the current row ##########

                # Set the last name
                lastName = records[recCount]['NameLast']

                # Adjust the NameFirst field to include the spouse if there is one
                if records[recCount]['Spouse'] != '' :
                    firstName = records[recCount]['NameFirst'] + ' & ' + records[recCount]['Spouse']
                else :
                    firstName = records[recCount]['NameFirst']
                    
                # Make the photo file name
                photoFirstName = firstName.replace('&', '-').replace('.', '').replace(' ', '')

                # Set our record count for progress display and send a status message
                scribus.progressSet(recCount)
                scribus.statusMessage('Placing record ' + `recCount` + ' of ' + `totalRecs`)

                # Add a watermark if a string is specified
                if self.outputWatermark :
                    self.addWatermark()

                # Put the last name element in this row
                nameLastBox = scribus.createText(crds[row]['nameLastXPos'], crds[row]['nameLastYPos'], crds[row]['nameLastWidth'], crds[row]['nameLastHeight'])
                scribus.setText(lastName, nameLastBox)
                scribus.setTextAlignment(scribus.ALIGN_RIGHT, nameLastBox)
                scribus.setTextDistances(0, 0, 0, 0, nameLastBox)
                scribus.setFont(self.fonts['nameLast']['bold'], nameLastBox)
                scribus.setFontSize(self.fonts['nameLast']['size'], nameLastBox)
                scribus.setTextShade(80, nameLastBox)
                scribus.rotateObject(90, nameLastBox)

                # Place the first name element in this row
                nameFirstBox = scribus.createText(crds[row]['nameFirstXPos'], crds[row]['nameFirstYPos'], crds[row]['nameFirstWidth'], crds[row]['nameFirstHeight'])
                scribus.setText(records[recCount]['Caption'], nameFirstBox)
                scribus.setTextAlignment(scribus.ALIGN_LEFT, nameFirstBox)
                scribus.setFont(self.fonts['nameFirst']['boldItalic'], nameFirstBox)
                scribus.setFontSize(self.fonts['nameFirst']['size'], nameFirstBox)

                # Place the image element in this row
                # We will need to do some processing on the first pass
                # The default output format is JPG
                orgImgFileName = records[recCount]['Photo']
                orgImgFile = os.path.join(self.orgImgDir, orgImgFileName)
                baseImgFileName = lastName + '_' + photoFirstName
                if self.willBePngImg :
                    ext = 'png'
                else :
                    ext = 'jpg'
                if not self.rgbColor :
                    imgFile = os.path.join(getattr(self, ext + 'ImgDir'), baseImgFileName + '-gray' + '.' + ext)
                else :
                    imgFile = os.path.join(getattr(self, ext + 'ImgDir'), baseImgFileName + '.' + ext)

                # Process the image now if there is none
                if not os.path.exists(imgFile) :
                    self.img_process.sizePic(orgImgFile, imgFile, self.maxHeight)
#                    self.img_process.outlinePic(imgFile, imgFile)
                    self.img_process.scalePic(imgFile, imgFile, self.imgDensity)
                    self.img_process.addPoloroidBorder(imgFile, imgFile)
                    # Color RGB is the default
                    if not self.rgbColor :
                        self.img_process.makeGray(imgFile, imgFile)

                # Double check the output and substitute with placeholder pic
                if not os.path.exists(imgFile) :
                    imgFile = self.placeholderPic
                # Create the imageBox and load the picture
                imageBox = scribus.createImage(crds[row]['imageXPos'], crds[row]['imageYPos'], crds[row]['imageWidth'], crds[row]['imageHeight'])
                if os.path.isfile(imgFile) :
                    scribus.loadImage(imgFile, imageBox)
                scribus.setScaleImageToFrame(scaletoframe=1, proportional=1, name=imageBox)

                # Place the country element in this row (add second one if present)
                countryBox = scribus.createText(crds[row]['countryXPos'], crds[row]['countryYPos'], crds[row]['countryWidth'], crds[row]['countryHeight'])
                countryLine = records[recCount]['Country1']
                try :
                    if records[recCount]['Country2'] != '' :
                        countryLine = countryLine + ' & ' + records[recCount]['Country2']
                except :
                    pass
                scribus.setText(countryLine, countryBox)
                scribus.setTextAlignment(scribus.ALIGN_RIGHT, countryBox)
                scribus.setFont(self.fonts['text']['boldItalic'], countryBox)
                scribus.setFontSize(self.fonts['text']['size'], countryBox)

                # Place the assignment element in this row
                assignBox = scribus.createText(crds[row]['assignXPos'], crds[row]['assignYPos'], crds[row]['assignWidth'], crds[row]['assignHeight'])
                scribus.setText(self.fixText(records[recCount]['Assignment']), assignBox)
                # Assign style to box
#                scribus.createParagraphStyle(name='assignStyle', alignment=0, leftmargin=10, firstindent=-10)
#                scribus.setStyle('assignStyle', assignBox)
                # Hard formated box
                scribus.setTextAlignment(scribus.ALIGN_LEFT, assignBox)
                scribus.setFont(self.fonts['text']['italic'], assignBox)
                scribus.setFontSize(self.fonts['text']['size'], assignBox)
                scribus.setLineSpacing(self.fonts['text']['size'] + 1, assignBox)
                scribus.setTextDistances(4, 0, 0, 0, assignBox)
                # Resize the frame height and determine the difference for
                # placing the next frame below it
                assignHeightNew = self.resizeFrame(assignBox)
                assignHeightDiff = crds[row]['assignHeight'] - assignHeightNew

                # Place the verse element in this row
                verseYPosNew = crds[row]['verseYPos'] - assignHeightDiff
                verseBox = scribus.createText(crds[row]['verseXPos'], verseYPosNew, crds[row]['verseWidth'], crds[row]['verseHeight'])
                # The verse element may be either a Scripture verse or a prayer request
                # If it is Scripture, and it has a verse ref, we want to set that
                # seperatly so we need to do a little preprocess on the text to find
                # out if it has a ref. This script will only recognize references
                # at the end of the string that are enclosed in brackets. See the
                # findVerseRef() function for more details
                verseRef = self.findVerseRef(records[recCount]['Prayer'])
                if verseRef :
                    verseText = self.removeVerseRef(self.fixText(records[recCount]['Prayer']))
                    scribus.setText(verseText, verseBox)
                else :
                    scribus.setText(self.fixText(records[recCount]['Prayer']), verseBox)
                # Can't find a way to set alignment to justified using setTextAlignment()
#                scribus.setTextAlignment(scribus.ALIGN_LEFT, verseBox)
                # Because of this, we make a style which seems to work
                scribus.createParagraphStyle(name='vBoxStyle', alignment=3)
                scribus.setStyle('vBoxStyle', verseBox)
                scribus.setFont(self.fonts['verse']['regular'], verseBox)
                scribus.setFontSize(self.fonts['verse']['size'], verseBox)
                scribus.setLineSpacing(self.fonts['verse']['size'] + 1, verseBox)
                scribus.setTextDistances(4, 0, 4, 0, verseBox)
                if self.hyphenate :
                    scribus.hyphenateText(verseBox)
                # Get the height difference in case we need to set ref box
                verseHeightNew = self.resizeFrame(verseBox)
                verseHeightDiff = crds[row]['verseHeight'] - verseHeightNew
                if verseRef :
                    # Set coordinates for this box
                    vRefBoxX = crds[row]['verseXPos']
                    vRefBoxY = (verseYPosNew + verseHeightNew)
                    vRefBoxH = crds[row]['nameFirstHeight'] / 2
                    vRefBoxW = crds[row]['verseWidth']
                    verseRefBox = scribus.createText(vRefBoxX, vRefBoxY, vRefBoxW, vRefBoxH)
                    scribus.setText(verseRef, verseRefBox)
                    scribus.setTextAlignment(scribus.ALIGN_RIGHT, verseRefBox)
                    scribus.setFont(self.fonts['verse']['italic'], verseRefBox)
                    scribus.setFontSize(self.fonts['verse']['size'] - 2, verseRefBox)
                    scribus.setLineSpacing(self.fonts['verse']['size'], verseRefBox)
                    scribus.setTextDistances(2, 0, 0, 0, verseRefBox)

                # Up our counts
                if row >= self.dimensions['rows']['count'] - 1 :
                    row = 0
                    pageNumber +=1
                else :
                    row +=1
                    
                recCount +=1

            # Create the index page here
            # Output a new page for the index
            if row == 0 and recCount != 0:
                scribus.newPage(-1)
                if pageSide == 'Odd' :
                    pageSide = 'Even'
                else :
                    pageSide = 'Odd'

                self.setPageNumber(crds, pageSide, 0, pageNumber)

        # Outut the index entries at this point
#        for key in paIndex.keys() :

        # Report we are done now before we loose focus
        scribus.statusMessage('Process Complete!')

###############################################################################
############################## Output Results #################################
###############################################################################

        # Now we will output the results to PDF if that is desired
        if self.makePdf :
            pdfExport =  scribus.PDFfile()
            pdfExport.info = self.pdfFile
            pdfExport.file = self.pdfFile
            pdfExport.save()

        # View the output if set
        if self.makePdf and self.viewPdf :
            cmd = ['evince', self.pdfFile]
            try :
                subprocess.Popen(cmd)
            except Exception as e :
                result = scribus.messageBox ('View PDF command failed with: ' + str(e), scribus.BUTTON_OK)


###############################################################################
############################# PA_Maker Starts Here ############################
###############################################################################

if __name__ == '__main__' :

    thisClass = PAMaker()
    thisClass.main()
    sys.exit()





