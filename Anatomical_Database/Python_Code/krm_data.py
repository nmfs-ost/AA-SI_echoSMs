'''
krm_data.py

Classes to read files that contain the silhouettes (aka outlines) of the organism's body and 
  inclusions for input to the KRM models of Clay, M. Jech, and J. Horne. These files have a .dat 
  suffix and were created by M. Jech and J. Horne.
Others have created KRM models, but I don't know their data file format. We will need to write code
to read other file formats

KRM .dat files are text files and come in two types:
    The first is from the original format that Clay used to store and import data.
    File Description:
    The first set of lines have several parameters and variables, e.g., metadata:
      "Pilchard 11, Namibia, June 99, CL=189"
      "total fish length mm =" 189
      "fish mass g =" 99
      "number of swimbladder chambers=" 1
    The next line is:
      "x, z-upper, z-lower, width"
      which provides the x, y, and z coordinate types.
    The next sets of lines are the silouhettes/outlines for the body parts. In all cases that 
      I know of, the fish body coordinates always are first and then the inclusions follow. The 
      number of inclusions is provided in the "number of swimbladder chambers" line.
    Each body part section is:
      Body part label, e.g., "fishbody" 
      Number with the total number of nodes for the body part. This is used to select
      the coordinates.
      Coordinate nodes with each set on a separate line.
    The final line is a comment string.

    The second is a modification of the 1st format that incorporated a metadata section. 
    This section collected the metadata in the Clay format into a section encompassed 
      by <meta> & </meta>.
    The <meta> section is always found at the top/beginning of the file.

The data are read and organized in a dictionary that follows the echoSMs datastore convention and
can be converted and exported to the toml format used by echoSMs.

jech
'''

import sys
from pathlib import Path
from dataclasses import dataclass, asdict
import re
import pprint
from datetime import datetime

class krm_data():
    def __init__(self, infn):
        '''
        Read the entire data file in one chunk

        Parameters:
        -----------
        infn: Input file name with full path. It should be a pathlib object, but will be converted
              to one if not.

        Returns:
        --------
        A list of strings where each string is a line in the data file
        '''

        # initialize some variables
        # string/line index
        self.idx = 0
        # new or Clay file format
        self.newformat = True
        # dictionary for the metadata
        self.data_md = {}
        # dictionary for the body part data
        self.data_bp = {}

        # check whether the filename is a pathlib object. If not set it to one.
        if (not isinstance(infn, Path)):
            infn = Path(infn)
        
        # open the file and read the file in one chunk as a list of strings
        try:
            with open(infn, 'r') as f:
                self.krmdata = f.readlines()
        except FileNotFoundError:
            print(f'Error: The file {infn} was not found. Exiting the program')
            sys.exit()

        # the number of strings (i.e., lines) in the string array (i.e., file)
        self.nlines = len(self.krmdata)


    def isnewformat(self, idx):
        '''
        Determine if the file is the Clay or new format

        Parameters:
        -----------
            the string number to use. Normally this should be set to zero.

        Returns:
        --------
           sets self.newformat as Boolean
           Boolean True = new format, False = Clay format
        '''

        self.idx = idx
        if (re.fullmatch('<meta>', self.krmdata[self.idx].strip())):
            self.newformat = True
        else:
            self.newformat = False

        return self.newformat


    def increment_idx(self, increment: int):
        '''
        Increment self.idx by the value provided

        Parameters:
        -----------
            increment: integer value to increment the number of strings to start reading

        Returns:
        --------
            none
        '''

        self.idx += increment


    def __istext(self, txt: str):
        '''
        Determine if the string has meaningful text, i.e., not a line return or empty spaces
        "strip" the text to remove preceeding and following spaces and a line feed

        Parameters:
        ----------
            txt: the string to test
        
        Returns:
        --------
            Boolean True or False
        '''

        return any(char.isalnum() for char in txt.strip())


    def new_meta_to_dict(self):
        '''
        Read the metadata section of the KRM new-format file
        
        Parameters:
        -----------
            uses self.idx and self.krmdata

        Returns:
        --------
            self.data_md
        '''

        while(not re.fullmatch('</meta>', self.krmdata[self.idx].strip())):
            tmpstr = self.krmdata[self.idx].strip()
            if(self.__istext(tmpstr)):
                match tmpstr:
                    case _ if re.match(r"^Title", tmpstr): 
                        self.data_md.setdefault('description', []).append(
                                ' '.join(tmpstr.split()[2:])
                                )
                    case _ if re.match(r"^Fish_Length", tmpstr): 
                        self.data_md['specimen_length'] = float(tmpstr.split()[-1])
                    case _ if re.match(r"^Fish_Mass", tmpstr): 
                        tmpw = float(tmpstr.split()[-1])
                        if (tmpw < 0):
                            tmpw = 0.0
                        self.data_md['specimen_weight'] = tmpw
                    case _ if re.match(r"^nsb", tmpstr): 
                        self.nsb = int(tmpstr.split()[-1])
                    case _ if re.match(r"^Bladder_Type", tmpstr): 
                        # put the bladder type in the description 
                        tmpstr = 'bladder type: '+' '.join(tmpstr.split()[2:])
                        self.data_md.setdefault('description', []).append(tmpstr)
                    case _ if re.match(r"^Rotated", tmpstr): 
                        self.data_md['rotate'] = True
                        self.data_md['rotate_method'] = ' '.join(tmpstr.split()[2:])
                    case _ if re.match(r"^Smooth", tmpstr): 
                        self.data_md['smooth'] = True
                        self.data_md['smooth_method'] = ' '.join(tmpstr.split()[2:])
                    case _ if re.match(r"^straighten", tmpstr): 
                        self.data_md['straighten'] = True
                        self.data_md['straighten_method'] = ' '.join(tmpstr.split()[2:])
                    case _ if re.match(r"^Images", tmpstr): 
                        self.data_md['image_files'] = ' '.join(tmpstr.split()[2:])
                    case _ if re.match(r"^Preparer", tmpstr): 
                        tmpstr = 'preparer: '+' '.join(tmpstr.split()[2:])
                        self.data_md.setdefault('description', []).append(tmpstr)
                    case _ if re.match(r"^File created", tmpstr): 
                        tmparr = (' '.join(tmpstr.split()[2:])).split()
                        tmpdt = datetime.strptime(tmparr[4]+'-'+tmparr[1]+'-'+tmparr[2],
                                                  '%Y-%b-%d')
                        self.data_md['date_created'] = tmpdt.strftime("%Y-%m-%d") 
                    case _:
                        self.data_md.setdefault('description', []).append(tmpstr)
            self.idx += 1


    def clay_meta_to_dict(self):
        '''
        Read the metadata section of the KRM Clay-format file
        
        Parameters:
        -----------
            uses self.idx and self.krmdata

        Returns:
        --------
            self.data_md
        '''

        # the Clay format is always four lines for metadata plus the final line in the file
        # the 1st line is a title/comment
        self.data_md.setdefault('description', []).append(
                self.krmdata[self.idx].strip().replace('"', '')
                )
        self.idx += 1
        # the 2nd line should be fish length, but confirm
        tmpstr = self.krmdata[self.idx].strip()
        if re.search(r"fish length", tmpstr):
            self.data_md['specimen_length'] = float(tmpstr.split()[-1])
            # the units are in the text
            if re.search(r" mm ", tmpstr):
                self.data_md['length_unit'] = 'millimeter'
            elif re.search(r" cm ", tmpstr):
                self.data_md['length_unit'] = 'centimeter'
            else:
                self.data_md['length_unit'] = 'unknown' 
        # the 3rd line should be fish weight/mass
        self.idx += 1
        tmpstr = self.krmdata[self.idx].strip()
        if re.search(r"fish mass", tmpstr):
            tmpw = float(tmpstr.split()[-1])
            if (tmpw < 0):
                tmpw = 0.0
            print(f'fish mass: {tmpw}')
            self.data_md['specimen_weight'] = tmpw
        if re.search(r" g ", tmpstr):
            self.data_md['specimen_weight_unit'] = 'gram'
        elif re.search(r" kg ", tmpstr):
            self.data_md['specimen_weight_unit'] = 'kilogram'
        else:
            self.data_md['specimen_weight_unit'] = 'unknown'
        # the 4th line is the number of inclusions/swimbladders
        self.idx += 1
        tmp = self.krmdata[self.idx].strip().split()
        self.nsb = int(tmp[-1])
        # get the last line of the file and add it to the description
        self.data_md.setdefault('description', []).append(
                self.krmdata[self.nlines-1].strip().replace('"', '')
                )

    def clay_bps_to_dict(self):
        '''
        Read the data for all the body parts into a dictionary

        Parameters:
        -----------
            uses self.krmdata

        Returns:
            self.data_bp
        '''

        # the first line of the data section is the header line
        # this is used for all the body parts
        self.data_bp['header'] = self.krmdata[self.idx].strip().replace('"', '')
        self.idx += 1

        # get the individual body parts
        # the first body part is always (I think?) the body, then the inclusions
        # the number of inclusions is given by self.nsb so the total number of
        #  body parts is nsb+1
        for i in range(self.nsb+1):
            self.__bp_to_dict()
        
    def new_bps_to_dict(self):
        '''
        Read the data for all the body parts into a dictionary

        Parameters:
        -----------
            uses self.krmdata

        Returns:
            self.data_bp
        '''

        # the first line of the data section is the header line
        # this is used for all the body parts
        tmpstr = self.krmdata[self.idx].strip()
        self.data_bp['header'] = tmpstr
        self.idx += 1

        # get the individual body parts
        # the first body part is always (I think?) the body, then the inclusions
        # the number of inclusions is given by self.nsb, so the total number of
        #  body parts is nsb+1
        for i in range(self.nsb+1):
            self.__bp_to_dict()
        

    def __bp_to_dict(self):
        '''
        Read the body part data section of the KRM new-format file

        Parameters:
        -----------
            uses self.idx and self.krmdata

        Returns:
        --------
            returns self.data_bp
        '''

        # parse the header to match to the coordinates"
        #self.data_bp['header'] = tmpstr
        hdrarr = self.data_bp['header'].split()
        # the next sections of data are organized by body part, number of sets of coordinates, and 
        #   the coordinates, each coordinate set is one line
        # body part label, which can have an operation (e.g., smoothed) in the description
        bp = self.krmdata[self.idx].strip().replace('"', '')
        # the next line is the number of data points
        self.idx += 1
        npts = int(self.krmdata[self.idx].strip().split()[0])
        self.data_bp[bp] = {'npts' : npts}
        # read the coordinate points. read them as a string and append them to a list 
        self.idx += 1
        for i in range(npts+1):
            tmpstr = self.krmdata[self.idx].strip()
            self.data_bp[bp].setdefault('nodes', []).append(tmpstr)
            self.idx += 1


    def display_dict(self, dictname):
        '''
        print the metadata dictionary to the display
        
        Parameters:
        -----------
            the name of the dictionary

        Returns:
        --------
           none
        '''

        match dictname:
            case 'meta':
                pprint.pprint(self.data_md)
            case 'bp':
                pprint.pprint(self.data_bp)
            case _:
                print('Incorrect dictionary name: select "meta" or "bp"')


