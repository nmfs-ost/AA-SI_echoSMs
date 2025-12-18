'''
Class to read the echoSMs schema file 

jech
'''

import sys
from pathlib import Path
import json
import pprint


class krm_schema():
    def __init__(self, schemafile=None):
        '''
        read the schema file. most likely it will be in JSON format

        Parameters:
        -----------
        None: if a JSON file is not given, it is assumed that taxonomic information will be passed
              via the main program
        Optional: schemafile- The path and file name to a JSON-format file with parameters that 
                  are needed to create a toml file for the specified species. The path and full 
                  file name need to be given. Preference for a pathlib object, but if not, it 
                  is converted to one. 

        Returns:
        --------
        none
        '''
        
        # initialize the schema dictionary 
        self.schema_md = {}

        # check whether the filename is a pathlib object. If not set it to one.
        if (schemafile):
            if (not isinstance(schemafile, Path)):
                schemafile = Path(schemafile)

            # open the file and read the file in one chunk as a list of strings
            try:
                with open(schemafile, 'r') as f:
                    self.schema_md = json.load(f)
            except FileNotFoundError:
                print(f'Error: The file {schemafile} was not found. Exiting the program')
                sys.exit() 



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
            case 'schema':
                pprint.pprint(self.schema_md)
            case _:
                print('Incorrect dictionary name: select "schema"')


