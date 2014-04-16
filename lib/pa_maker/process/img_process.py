#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Copyright 2014, Dennis Drescher
#    All rights reserved.
#
#    This library is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 2.1 of License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should also have received a copy of the GNU Lesser General Public
#    License along with this library in the file named "LICENSE".
#    If not, write to the Free Software Foundation, 51 Franklin Street,
#    suite 500, Boston, MA 02110-1335, USA or visit their web page on the 
#    internet at http://www.fsf.org/licenses/lgpl.html.

# Description
#
# This module provides a simple Python interface to various ImageMagick
# functions it will access through the subprocess module.


# Import modules
import sys, os, shutil, subprocess, tempfile


class ImgProcess (object) :

#    def __init__ (self, parent=None) :


    ###############################################################################
    ############################## General Functions ##############################
    ###############################################################################

    def scalePic (self, inFile, rtnFile, density) :
        '''Change the image density (dpi).'''

        # Begin the output command set
        cmd = ['convert', inFile, '-set', 'units', 'pixelsperinch', '-density', density, rtnFile]

        # Run the command
        try :
            rCode = subprocess.call(cmd)
            return true
        except Exception as e :
            print 'Error: Imagemagick outline failed with: ' + str(e)


    def sizePic (self, inFile, rtnFile, maxHeight) :
        '''Create a resized picture, in the specified format,
        according to the input values given. Output to the rtnFile
        handle location.'''

        # Begin the output command set
        cmd = ['convert', inFile, '-resize', 'x' + maxHeight, rtnFile]

        # Run the command
        try :
            rCode = subprocess.call(cmd)
            return true
        except Exception as e :
            print 'Error: Imagemagick outline failed with: ' + str(e)


    def outlinePic (self, inFile, rtnFile) :
        '''Add a simple outline to a picture. Return the name of the file
        that was just created.'''

        cmd = ['convert', inFile, '-bordercolor', 'black', '-border', '0.5x0.5', rtnFile]

        # Run the command
        try :
            rCode = subprocess.call(cmd)
            return True
        except Exception as e :
            self.pa_tools.sendError('Imagemagick outline failed with: ' + str(e))
            return False


    def addPoloroidBorder (self, inFile, rtnFile) :
        '''Add a Poloroid-like boarder to the picture.'''

        cmd = ['convert', inFile, '-bordercolor', 'white', '-border', '20',
                 '-bordercolor', 'grey60', '-border', '1',
                  '-background', 'none', '-rotate', '0',
                   '-background', 'black', '( +clone -shadow 60x4+4+4 )', '+swap',
                    '-background', 'none', '-flatten', rtnFile]
        # Run the command
        try :
            rCode = subprocess.call(cmd)
            return True
        except Exception as e :
            self.pa_tools.sendError('Imagemagick outline failed with: ' + str(e))
            return False


    def makeGray (self, inFile, rtnFile) :
        '''Change the color space on an image to gray.'''

        cmd = ['convert', inFile, '-colorspace', 'Gray', rtnFile]
        # Run the command
        try :
            rCode = subprocess.call(cmd)
            return True
        except Exception as e :
            self.pa_tools.sendError('Imagemagick outline failed with: ' + str(e))
            return False







