'''
Program to read KRM .dat files, get taxonomic information from WORMS, and get remaining metadata
The program flow is:
1) Get metadata. The preferred method is to read a JSON file with the metadata and data file
   names. If a JSON file is not provided, TBD another method(s) to provide required
   metadata
   At a minimum, the required metadata are in the JSON file
2) get taxonomic information from WORMS
3) read .dat files for the KRM model that were created by M. Jech (and probably J. Horne)
   Others have created KRM models, but I don't know the data file format. 
   TBD write code to read other file formats.
   Metadata in the .dat files will overwrite those in the JSON file!

The data are read and organized in a dictionary that follows the echoSMs datastore convention and
can be converted and exported to the toml format used by echoSMs.

jech
'''

import sys
from pathlib import Path
from datetime import date
from krm_schema import krm_schema as ks
from krm_worms import krm_worms as kw
from krm_json import krm_json as kj
from krm_data import krm_data as kd
from krm_merge_data import krm_merge_data as km
from krm_validate import krm_validate as kv
from krm_toml import krm_toml as kt
import toml
#if sys.version_info >= (3, 11):
#    import tomllib
#else:
#    import tomli as tomllib

# get the schema json
print('Read Schema JSON')
schema_file = Path('echoSMs_datastore_schema.json')
schema_md = ks(schema_file)
printschema= 'n'
if (printschema == 'y'):
    print('SCHEMA METADATA')
    schema_md.display_dict('schema')
# validate the schema
validate_schema = kv(schema_ref=schema_md, schema_obj='schema_md', validate_schema=True) 

# read the specimen metadata
# read from a json file
print('Read Specimen Metadata')
jsonf = Path('Clupea_harengus_bd.json')
#jsonf = Path('Clupea_harengus_sb.json')
json_md = kj(jsonf)
printjson= 'n'
if (printjson == 'y'):
    print('METADATA')
    json_md.display_dict('json_md')
# validate the json with the schema
validate_json = kv(schema_ref=schema_md, schema_obj='schema_md', 
                   json_ref=json_md, json_obj='json_md', validate_schema=False)
if (validate_json):
    validjson = validate_json.validate()

# get taxonomic information from WORMS
print('Get WoRMS Data')
worms_md = kw(jsonf)
#aphiaID = worms_md.get_aphia_id_by_taxon(returnid=True)
wormranks = worms_md.get_taxon_ranks_by_aphia_id(returnranks=False)
vernaculars = worms_md.get_vernaculars_by_aphia_id(language='English', returnvernaculars=True)
printworms = 'n'
if (printworms == 'y'):
    print('WORMS')
    worms_md.display_dict('worms')

# read the data
# select the data file and path
print('Read the Data')
dat_filepath = Path('.')
# new metadata format file
dat_filename = Path('aherr001.dat')
# clay format file
#dat_filename = Path('plch11.dat')
dat_fname = dat_filepath / dat_filename
# read the data as an array of strings. each line in the file is a string
krm_data = kd(dat_fname)

# check whether the file is a new format with the <meta> section or a Clay-format file
if (krm_data.isnewformat(0)):
    # this is a new format file
    # start on the 2nd line so increment idx by one
    krm_data.increment_idx(1)
    # read the metadata section and put the data into a dictionary
    krm_data.new_meta_to_dict()
    # add one to the line index to start at the next line
    krm_data.increment_idx(1)
    # read the data for the body parts 
    krm_data.new_bps_to_dict()
else:
    # Clay format
    # metadata start on the 1st line
    krm_data.clay_meta_to_dict()
    krm_data.increment_idx(1)
    #read the data for the body parts
    krm_data.clay_bps_to_dict()
printdatameta = 'n'
if (printdatameta == 'y'):
    print('.dat METADATA')
    krm_data.display_dict('meta')
printdatadict = 'n'
if (printdatadict == 'y'):
    print('.dat BP')
    krm_data.display_dict('bp')

# merge the dictionaries
# this translates the KRM formats to the echoSMs format
print('merge data')
krm_merge = km(data=krm_data, worms=worms_md, json=json_md)
krm_merge.merge_dicts()
printmergedata = 'n'
if (printmergedata == 'y'):
    krm_merge.display_dict('data')
plotdata = 'y'
if (plotdata == 'y'):
    krm_merge.plot_silhouette('data')

# validate the merged data with the schema
validate_data = kv(schema_ref=schema_md, schema_obj='schema_md', 
                   data_ref=krm_merge, data_obj='krm_data_merged')
if (validate_data):
    validmerge = validate_data.validate()


# generate a toml format from the merged data
create_toml='y'
if (create_toml == 'y'):
    tomlf = jsonf.with_suffix('.toml')
    krm_toml = kt(data_ref=krm_merge, data_obj='krm_data_merged')
    toml_string = krm_toml.data_to_toml_string(return_toml=True)
    krm_toml.data_to_toml_file(toml_file=tomlf)


