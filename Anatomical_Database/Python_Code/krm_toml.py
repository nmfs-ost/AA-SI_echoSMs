'''
Class to convert dictionary to toml

jech
'''

import sys
from pathlib import Path
import json
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for
import pprint
import toml
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class krm_toml():
    def __init__(self, data_ref=None, data_obj=None):
        '''
        Convert a dictionary to toml

        Parameters:
        -----------
        data_ref- data reference 
        data_obj- data object

        Returns:
        --------
        none
        '''
        
        self.tomled = False

        if (data_ref and data_obj):
            self.data_to_toml = getattr(data_ref, data_obj)
        else:
            print('Data ref and/or object were not provided. Can not transform the data to toml')
            return False


    def data_to_toml_string(self, return_toml=False):
        '''
        transform the dictionary to a toml string
        
        Parameters:
        -----------
        none- use the dictionaries defined in self
        Optional- return_toml- return the toml string

        Returns:
        --------
        toml string if requested
        '''
        
        self.toml_string = toml.dumps(self.data_to_toml)
        self.tomled = True

        if (return_toml):
            return self.toml_string


    def data_to_toml_file(self, toml_file=None):
        '''
        outputs the dictionary to a toml file
        
        Parameters:
        -----------
        toml_file- output file as a pathlib object. if not pathlib, will convert

        Returns:
        --------
        boolean that the file was created
        '''
        # check whether the filename is a pathlib object. If not set it to one.
        if (toml_file):
            if (not isinstance(toml_file, Path)):
                toml_file = Path(toml_file)

        with open(toml_file, 'w') as f:
            toml.dump(self.data_to_toml, f)

        return True


    def display_toml(self):
        '''
        print the toml string to the display

        Parameters:
        -----------
        none

        Returns:
        --------
        none
        '''

        if (self.tomled):
            pprint.pprint(self.data_to_toml, sort_dicts=True)
        else:
            print('No toml string created. Can not display the toml string')


