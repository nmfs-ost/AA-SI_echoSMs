'''
Merge the KRM dictionaries

jech
'''

import sys
import pprint
import re
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure, show, subplots_adjust, get_cmap, cm
import numpy as np

class krm_merge_data():
    def __init__(self, data=None, worms=None, json=None):
        '''
        references to other dictionaries are passed as arguments

        Parameters:
        -----------
        dictionaries to merge

        Returns:
        --------
        none
        '''

        # merged dictionary
        self.krm_data_merged = {}
        self.add_json = False
        self.add_worms = False
        self.add_data = False

        if (json):
            self.json_ref = json
            self.add_json = True
        if (worms):
            self.worms_ref = worms
            self.add_worms = True
        if (data):
            self.data_ref = data
            self.add_data = True


    def merge_dicts(self, returndict=False):
        '''
        # merge the dictionaries one at a time
        Parameters:
        -----------
        None - use self
        Optional - returndict will return the dictionary

        Returns:
        --------
        The merged dictionary if requested
        '''

        if (self.add_json):
            #print('JSON')
            #pprint.pprint(self.json_ref.json_md)
            self.krm_data_merged = self.krm_data_merged | self.json_ref.json_md
        if (self.add_worms):
            #print('WORMS')
            #pprint.pprint(self.worms_ref.worms_md)
            self.krm_data_merged = self.worms_ref.worms_md | self.krm_data_merged
        if (self.add_data):
            self.krm_data_merged = self.krm_data_merged | self.data_ref.data_md 
            #self.krm_data_merged = self.data_ref.data_md | self.krm_data_merged
            # the schema allows for one body part (i.e., anatomical feature) per toml file. 
            # the KRM data files usually have data for more than one body part. Use the 
            # data metadata to get the body part and merge those
            bp = self.__get_anatomical_feature()
            if (bp):
                header = ''
                tmp_dict = {}
                for k in self.data_ref.data_bp.keys():
                    # the data files should always have a header line preceeding the data section
                    if re.search('header', k):
                        header = self.data_ref.data_bp[k]
                    if re.search(bp, k):
                        tmp_dict = { 'data': self.data_ref.data_bp[k]['nodes'] }
                # tmp_dict should be a list of strings. each string is a coordinate.
                # convert these to the toml coordinates of x, y, z, height, and width
                npts = len(tmp_dict['data'])
                # get the specimen length unit and scaler to convert to meters
                self.__get_specimen_length_unit()
                # the KRM data can be symmetric about the x-axis, i.e., the body part only has
                # width with the center at y=0, or it can "wiggle". For the former, there are
                # no stbd and port coordinates and there are only four values in each string.
                # for the "wiggley" data, there are stbd and port coordinates and there are
                # six coordinates per string.
                tmp = tmp_dict['data'][0].split()
                if (len(tmp) == 4):
                    # symmetric data
                    dict_out = self.__symmetric_data(tmp_dict)
                elif (len(tmp) == 6):
                    # nonsymmetric data
                    dict_out = self.__nonsymmetric_data(tmp_dict)
                else:
                    print(f'number of coordintes is {len(tmp)}. Unable to load data')
            else:
                print(f'The requested anatomical feature was not found. No data will be added')
            self.krm_data_merged = dict_out | self.krm_data_merged
            #print('MERGED')
            #pprint.pprint(self.krm_data_merged)


    def __symmetric_data(self, dict_in):
        '''
        read the KRM coordinates for symmetrical dorsal-view (about the x axis) data
        convert the KRM coordinates to echoSMs coordinates (x, y, z, height, width)
        put the new coordinates into a dictionary to return

        Parameters:
        -----------
        data dictionary with KRM coordintes 

        Returns:
        --------
        dictionary with the coordinates in echoSMs format
        '''

        # I leave the original KRM coordinates as they are in the data file and will use 
        # echoSMs tools to do the coordinate conversion.
        # in echoSMs, x, y, and z are the center line and height and width are the
        # 1/2 total height and width. This makes the outlines symmetric with respect
        # to the center line
        x = []
        y = []
        z = []
        height = []
        width = []
        for l in dict_in['data']:
            crds = [float(x) for x in l.split()]
            x.append(round(crds[0], 5))
            y.append(0.0)
            z_center = (crds[1]+crds[2])/2
            z.append(round(z_center, 5))
            half_height = (crds[1]-crds[2])/2
            height.append(round(half_height, 5))
            half_width = crds[3]/2
            width.append(round(half_width, 5))

        shape_type = self.__get_shape_type()
        if (shape_type):
            dict_out = {'shape_data': {
                            'shape_type': shape_type,
                            'x': x,
                            'y': y,
                            'z': z,
                            'height': height,
                            'width': width
                           }
                        }
        else:
            dict_out = {}
            print('Shape type not valid. Can not merge the data!')

        return dict_out


    def __nonsymmetric_data(self, dict_in):
        '''
        read the KRM coordinates for nonsymmetrical dorsal-view (about the x axis) data
        these data have stbd and port coordinates
        convert the KRM coordinates to echoSMs coordinates (x, y, z, height, width)
        put the new coordinates into a dictionary to return

        Parameters:
        -----------
        data dictionary with KRM coordintes 

        Returns:
        --------
        dictionary with the coordinates in echoSMs format
        '''

        x = []
        y = []
        z = []
        height = []
        width = []
        for l in dict_in['data']:
            crds = [float(x) for x in l.split()]
            # I leave the original KRM coordinates as they are in the data file and will use 
            # echoSMs tools to do the coordinate conversion.
            # in echoSMs, x, y, and z are the center line and height and width are the
            # 1/2 total height and width. This makes the outlines symmetric with respect
            # to the center line
            x.append(round(crds[0], 5))
            y_center = (crds[4]+crds[5])/2
            y.append(round(y_center, 5))
            z_center = (crds[1]+crds[2])/2
            z.append(round(z_center, 5))
            half_height = (crds[1]-crds[2])/2
            height.append(round(half_height, 5))
            half_width = (crds[4]-crds[5])/2
            width.append(round(half_width, 5))

        shape_type = self.__get_shape_type()
        if (shape_type):
            dict_out = {'shape_data': {
                            'shape_type': shape_type,
                            'x': x,
                            'y': y,
                            'z': z,
                            'height': height,
                            'width': width
                           }
                        }
        else:
            dict_out = {}
            print('Shape type not valid. Can not merge the data!')

        return dict_out


    def __get_shape_type(self):
        '''
        Get the shape type requested in the json metadata

        Parameters:
        -----------
        None. Use self.

        Return:
        -------
        The requested shape type.
        '''

        if ('shape_type' in self.json_ref.json_md):
            st = self.json_ref.json_md['shape_type']
            print(f'requested shape type: {st}')
            return st
        else:
            print(f'shape type is not in the dictionary. Can not get requested data')
            return False


    def __get_anatomical_feature(self):
        '''
        Get the anatomical feature requested in the json metadata

        Parameters:
        -----------
        None. Use self.

        Return:
        -------
        The requested anatomical feature.
        '''

        if ('anatomical_feature' in self.json_ref.json_md):
            bp = self.json_ref.json_md['anatomical_feature']
            print(f'requested anatomical feature: {bp}')
            return bp
        else:
            print(f'anatomical feature is not in the dictionary. Can not get requested data')
            return False


    def __get_specimen_length_unit(self):
        '''
        Get the length unit of the specimen measurements in the json metadata and set the
        scaler for converting lengths to meters for echoSMs

        Parameters:
        -----------
        None. Use self.

        Return:
        -------
        None. variables are written to self
        '''

        if ('specimen_length_unit' in self.json_ref.json_md):
            self.slu = self.json_ref.json_md['specimen_length_unit']
            print(f'specimen_length_unit: {self.slu}')
            if (self.slu):
                match self.slu:
                    case "millimeter":
                        self.slu_scale_to_meter = 0.001
                    case "centimeter":
                        self.slu_scale_to_meter = 0.01
                    case "meter":
                        self.slu_scale_to_meter = 1.0
                    case _:
                        self.slu_scale_to_meter = 1
            else:
                self.slu_scale_to_meter = 1
        else:
            print(f'specimen length unit is not in the dictionary. Can not get requested data')
            self.slu = False
            self.slu_scale_to_meter = 1


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
            case 'data':
                pprint.pprint(self.krm_data_merged, sort_dicts=True)
            case _:
                print('Incorrect dictionary name: select "data"')


    def plot_silhouette(self, dictname):
        '''
        plot the outlines

        Parameters:
        -----------
        'data' to plot the data 

        Returns:
        --------
           none
        '''

        match dictname:
            case 'data':
                #pprint.pprint(self.krm_data_merged, sort_dicts=True)
                # plot the lateral and dorsal outlines
                nrow = 2
                ncol = 1
                x = np.array(self.krm_data_merged['shape_data']['x'])
                y = np.array(self.krm_data_merged['shape_data']['y'])
                z = np.array(self.krm_data_merged['shape_data']['z'])
                height = np.array(self.krm_data_merged['shape_data']['height'])
                width = np.array(self.krm_data_merged['shape_data']['width'])
                lim_pct = 0.1
                max_ordinate = max([max(width)*2, max(height)*2])
                max_ordinate += max_ordinate*lim_pct
                maxx = max(x)
                maxx += maxx*lim_pct
                fig, (ax0, ax1), = plt.subplots(nrows=nrow, ncols=ncol, figsize=(9,9))
                ax0.plot(x, y, linestyle='dashed')
                ax0.plot(x, (width+y), linewidth=2, color='red')
                ax0.plot(x, ((-1)*width+y), linewidth=2, color='blue')
                ax0.set_xlim(maxx, 0)
                ax0.set_ylim((-1)*max_ordinate, max_ordinate)
                ax0.set_xlabel('x ['+self.slu+']')
                ax0.set_ylabel('y ['+self.slu+']')
                ax0.set_title('Dorsal View')
                ax1.plot(x, z, linestyle='dashed')
                ax1.plot(x, (height+z), linewidth=2, color='red')
                ax1.plot(x, ((-1)*height+z), linewidth=2, color='blue')
                ax1.set_xlim(maxx, 0)
                ax1.set_ylim((-1)*max_ordinate, max_ordinate)
                ax1.set_xlabel('x ['+self.slu+']')
                ax1.set_ylabel('z ['+self.slu+']')
                ax1.set_title('Lateral View')
                plt.show(block=False)

            case _:
                print('Incorrect dictionary name: select "data"')

