## Anatomical Database
Acoustic scattering models that are applied to marine and freshwater animals often require digital representations of their morphometry and anatomy. echoSMs has developed a [data store](https://ices-tools-dev.github.io/echoSMs/datastore_intro/) for digital reprepesntations of fish and zooplankton. We provide code and the schema for providing data to the database and for those data to be input to acoustic scattering models.

The folders are arranged as:
- **Schema**
  - The JSON schema used by the data store
- **Example_Data**
  - JSON file that is used for each anatomical feature
  - toml file that is generated from the JSON file. The toml file is the file that is used in echoSMs to input data to a scattering model.
- **Python_Code**
  - Code to generate the toml file from the JSON file
  - Code to predict acoustic scattering using the KRM model
