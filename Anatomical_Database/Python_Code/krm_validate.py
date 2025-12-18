'''
Class to validate data and/or dictionary to the echoSMs schema

jech
'''

import sys
from pathlib import Path
import json
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for
import pprint


class krm_validate():
    def __init__(self, schema_ref=None, schema_obj=None, schema_file=None, 
                       json_ref=None, json_obj=None, json_file=None, 
                       data_ref=None, data_obj=None, validate_schema=False):
        '''
        Validate the data and/or dictionary to the echoSMs schema

        Parameters:
        -----------
        schema_ref- if the schema file was read previously and if it is an instance to another
                   class, then use this as a reference to that instance
        schema_obj- the name of the object in the schema reference
        schema_file- the schema in a JSON-format file
        json_ref- if the metadata was previously input from a JSON file and if it is 
                 an instance to another class, then use this as a reference to that instance
        json_obj- the name of the object in the json reference
        json_file- The path and file name to a JSON-format file with parameters that 
                  are needed to create a toml file for the specified species. The path and full 
                  file name need to be given. Preference for a pathlib object, but if not, it 
                  is converted to one. 
        data_ref- if the metadata was previously input or generated and if it is an 
                 instance to another class, then use this as a reference to that instance
        data_obj- the name of the object in the data reference
        validate_schema- validate the schema

        Returns:
        --------
        boolean as to whether the data and/or file is validated
        '''
        
        if (schema_file or schema_ref or schema_obj):
            if (schema_file):
                if (not isinstance(schema_file, Path)):
                    self.schema_file = Path(schema_file)
                else:
                    self.schema_file = schema_file
                try:
                    with open(self.schema_file, 'r') as f:
                        self.schema_dict = json.load(f)
                except FileNotFoundError:
                    print(f'Error: The file {self.schema_file} was not found. Exiting the program')
                    sys.exit() 
            elif (schema_ref and schema_obj):
                self.schema_dict = getattr(schema_ref, schema_obj)
            else:
                print('No schema file, reference, or object provided. Can not validate the data')
                return False

        # validate the schema
        if (validate_schema):
            try:
                validator = validator_for(self.schema_dict)
                validator.check_schema(self.schema_dict)
                print('Valid schema')
            except SchemaError as e:
                print(f'Schema failed: {e}')

        if (json_file or json_ref or json_obj):
            if (json_file):
                if (not isinstance(json_file, Path)):
                    self.json_file = Path(json_file)
                else:
                    self.json_file = json_file
                try:
                    with open(self.json_file, 'r') as f:
                        self.data_dict= json.load(f)
                except FileNotFoundError:
                    print(f'Error: The file {self.json_file} was not found. Exiting the program')
                    sys.exit() 
            elif (json_ref and json_obj):
                self.data_dict = getattr(json_ref, json_obj)
                #self.data_dict = json_ref.json_obj
            else:
                print('No json file, reference, or object provided')
                return False

        if (data_ref or data_obj):
            if (data_ref and data_obj):
                self.data_dict = getattr(data_ref, data_obj)
            else:
                print('No data reference or object provided. Can not validate the data')
                return False

    def validate(self):
        '''
        use jsonschema to validate the json to the schema
        
        Parameters:
        -----------
        none- use the dictionaries defined in self

        Returns:
        --------
        boolean whether the file was validated
        '''
        
        valid = False

        try:
            validate(instance=self.data_dict, schema=self.schema_dict)
            print("Data adhere to the schema.")
            valid = True
        except ValidationError as e:
            print(f"Data do NOT adhere to the schema. Error: {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred during validation: {e}")

        return valid


    def display_dict(self, dictname):
        '''
        print the schema or JSON dictionary to the display

        Parameters:
        -----------
        schema- the schema dictionary
        json- the json dictionary

        Returns:
        --------
           none
        '''

        match dictname:
            case 'schema':
                pprint.pprint(self.schema_dict, sort_dicts=True)
            case 'data':
                pprint.pprint(self.data_dict, sort_dicts=True)
            case _:
                print('Incorrect dictionary name: select "schema", or "data"')


