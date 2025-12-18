'''
Class to get KRM metadata that adheres to the datastore schema. Default is from a JSON file.
TBD: get metadata another way (e.g., keyboard input)

jech
'''

import sys
from pathlib import Path
import json
import pprint

class krm_json():
    def __init__(self, jsonfile=None):
        '''
        Initialize metadata from JSON file 

        Parameters:
        -----------
        None: if a JSON file is not given, it is assumed that taxonomic information will be passed
              via the main program
        Optional: jsonfile- The path and file name to a JSON-format file with parameters that 
                  are needed to create a toml file for the specified species. The path and full 
                  file name need to be given. Preference for a pathlib object, but if not, it 
                  is converted to one.

        Returns:
        --------
        none
        '''
        
        json_md = {}

        # check whether the filename is a pathlib object. If not set it to one.
        if (jsonfile):
            if (not isinstance(jsonfile, Path)):
                jsonfile = Path(jsonfile)

            # open the file and read the file in one chunk as a list of strings
            # schema_dict is a dictionary with the json parameters
            try:
                with open(jsonfile, 'r') as f:
                    self.json_md = json.load(f)
            except FileNotFoundError:
                print(f'Error: The file {jsonfile} was not found. Exiting the program')
                sys.exit() 
        else:
            # methods to get metadata
            print('No JSON file provided. Metadata are generated via ...')


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
            case 'json_md':
                pprint.pprint(self.json_md, sort_dicts=True)
            case _:
                print('Incorrect dictionary name: select "json_md"')


