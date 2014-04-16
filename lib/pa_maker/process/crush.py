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

# Import modules
import os, shutil, subprocess
from shrinkypic.process             import tools
from Tkinter                        import *
import tkMessageBox


class Crush (object) :
    '''PNG file reduction module.'''

    def __init__ (self) :
        self.tools          = tools.Tools()


    def crushPic (self, inFile) :
        '''Use the pngnq utility to take out the fluff from a PNG file.'''

        try :
            rc = subprocess.call(['pngnq', inFile])
        except Exception as e :
            self.tools.sendError('pngnq failed with: ' + str(e))

        # Clean up - The only way I could seem to get pngnq to work in this
        # configuration was to let it put its special extention on the back.
        # Because of this, some cleanup has to be done.
        crushFile = inFile.replace('.png', '-nq8.png')
        shutil.copyfile(crushFile, inFile)
        os.remove(crushFile)



