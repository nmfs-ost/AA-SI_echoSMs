'''
Class to get taxonomic information from WORMS

jech
'''

import sys
from pathlib import Path
import pyworms
import json
import pprint
import subprocess
import ast


class krm_worms():
    def __init__(self, jsonfile=None):
        '''
        Initialize taxonomic paramters from the WORMS database 

        Parameters:
        -----------
        None: if a JSON file is not given, it is assumed that taxonomic information will be passed
              via the main program
        Optional: jsonfile- The path and file name to a JSON-format file with parameters that 
                  are needed to create a toml file for the specified species. The path and full 
                  file name need to be given. Preference for a pathlib object, but if not, it 
                  is converted to one. 
                  WoRMS only needs the Aphia ID from the json file.

        Returns:
        --------
        none
        '''
        
        # initialize the taxonomic dictionary 
        self.worms_md = {}
        # the taxonomic ranks echoSMs uses
        self.taxon_ranks = ['class', 'order', 'family', 'genus', 'species']
        # the krm parameters from the json file
        krmpars = {}
        # the echoSMs schema has "specimen_" as a prefix to the ranks.
        self.sp_str = 'specimen_'

        # check whether the filename is a pathlib object. If not set it to one.
        if (jsonfile):
            if (not isinstance(jsonfile, Path)):
                jsonfile = Path(jsonfile)

            # open the file and read the file in one chunk as a list of strings
            # krmpars is a dictionary with the json parameters
            try:
                with open(jsonfile, 'r') as f:
                    krmpars = json.load(f)
            except FileNotFoundError:
                print(f'Error: The file {jsonfile} was not found. Exiting the program')
                sys.exit() 

        if (krmpars['aphia_id']):
            self.worms_md['aphia_id'] = krmpars['aphia_id']
        else:
            print(f'Error: Aphia ID was not found in the file {jsonfile}. Exiting the program')
            sys.exit() 


    def _docurl(self, cline):
        '''
        execute the curl command to get the vernaculars from WoRMS
        pyworms does not have a function to do that
        
        Parameters:
        -----------
        cline: the command line string that will be executed. Needs to built outside of this
               function

        Returns:
        --------
        the WoRMS vernacular standard output
        '''

        command = ['curl', cline]
        vernacular = subprocess.run(command, capture_output=True, text=True, check=True)

        return vernacular


    def get_aphia_id_by_taxon(self, taxon=None, returnid=False):
        '''
        Get the Aphia ID for the specified taxon. Because Aphia ID is required this function 
        is not typically used.

        Parameters:
        -----------
        default: use the taxon provided in the json file
                 This will overwrite the Aphia ID from the json file
        optional: taxon- the lowest taxonomic rank for the organism
                  returnid- return the Aphia ID. Default is False

        Returns:
        --------
        the Aphia ID from the WORMS database
        '''

        if (taxon):
            result = pyworms.aphiaRecordsByName(taxon)
        elif ('taxon' in self.worms_md):
                taxon = self.worms_md['taxon']
                result = pyworms.aphiaRecordsByName(taxon)
        else:
            print(f'taxon: {taxon} does not seem to be provided')

        if result:
            self.worms_md['aphia_id'] = result[0]['AphiaID']
        else:
            print(f'Could not find {taxon} in WORMS. Maybe check the spelling? Exit the program')
            sys.exit()

        if (returnid):
            return self.worms_md['aphia_id']


    def get_taxon_ranks_by_aphia_id(self, aphiaid=None, returnranks=False):
        '''
        Get the taxonomic ranks for the specified Aphia ID. This will get the taxonomic ranks
          starting with the highest rank in self.taxon_ranks and going down to the rank given 
          by the Aphia ID.

        Parameters:
        -----------
        Default: uses aphia_id from self.worms_md
        Optional: aphiaid- specify an Aphia ID
                  returnranks- return the dictionary. Default is False

        Returns:
        --------
        Dictionary with the taxonomic ranks start with class to the rank of the Aphia ID
        For example, if the lowest rank is family, then only class, order, and family are 
          loaded into the dictionary
        '''

        if aphiaid:
            classification = pyworms.aphiaClassificationByAphiaID(aphiaid)
        else:
            classification = pyworms.aphiaClassificationByAphiaID(self.worms_md['aphia_id'])

        if classification:
            for tr in self.taxon_ranks:
                if (tr in classification):
                    self.worms_md[self.sp_str+str(tr)] = classification[tr]
        else:
            print(f'Could not find AphiaID {aphia_id} in WoRMS. Maybe check the code? \
                  Exit the program')
            sys.exit()

        if (returnranks):
            return self.worms_md



    def get_vernaculars_by_aphia_id(self, aphiaid=None, language='English', returnvernaculars=False):
        '''
        Get the vernacular names for the specified Aphia ID. 

        Parameters:
        -----------
        Default: uses aphia_id from self.worms_md
                 the default language is English. Use another language if provided.
        Optional: aphiaid- specify an Aphia ID
                  returnvernaculars- return the dictionary. Default is False

        Returns:
        --------
        Dictionary with the vernacular names of the Aphia ID
        '''

        if aphiaid:
            cline = 'https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/'+str(aphiaid)
        elif (self.worms_md['aphia_id']):
            aphiaid = self.worms_md['aphia_id']
            cline = 'https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/'+\
                    str(aphiaid)
        else:
            print(f'AphiaID not provided. Check the json file. Exit the program')
            sys.exit()

        vernaculars = self._docurl(cline)
        if (not vernaculars):
            print(f'Vernaculars for Aphia ID {aphiaid} were not found in WoRMS.')
            if (returnvernaculars):
                return self.worms_md

        # the curl command returns text with a list of dictionaries as well as other characters
        # use ast to convert to a list of dictionaries
        vlist = ast.literal_eval(vernaculars.stdout)
        # reconfigure the list of dictionaries to a dictionary with the language as the key
        # and the language code and vernacular as a list
        # I drop the language code from the final dictionary. Make a list of lists if 
        # we need it. See the commented lines.
        # there can be multiple vernaculars for each language, so append vernaculars to a list
        vdict = {}
        for v in vlist:
            vdict.setdefault(v['language'], []).append(v['vernacular'])
        #    vdict.setdefault(v['language'], []).append([v['language_code'],
        #                                                v['vernacular']
        #                                               ] )

        # set the dictionary vernacular to the list of vernaculars
        if (language in vdict.keys()):
            self.worms_md[self.sp_str+'vernaculars'] = vdict[language]
        else:
            self.worms_md[self.sp_str+'vernaculars'] = []
            print(f'Vernaculars in {language} were not found')

        if (returnvernaculars):
            return self.worms_md


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
            case 'worms':
                pprint.pprint(self.worms_md, sort_dicts=True)
            case _:
                print('Incorrect dictionary name: select "worms"')


