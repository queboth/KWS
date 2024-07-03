"""
    This is the new Keyword Spotting Tool, which spot's search terms 
    in the PyLaia ConfMats.ark. 
    
    This class module contains methods for reading and traversing the 
    Page XML's.
    
    Copyright (C) 2023  Raphael Unterweger

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""



'''
Created on 17.10.2023

@author: run
'''

import xml.etree.ElementTree as ET


class XMLUtils(object):
    '''
    classdocs
    '''
    namespace="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"

    def __init__(self):
        '''
        Constructor
        '''
    
    
    def createMetadataDict(self, array_of_xml_paths):
        """
        This method reads pageNr, imgUrl and docId from the TranskribusMetadata-Element in the 
        PageXML Header for all given xml file pathes.
        """
        # Create an empty dictionary to store the extracted data
        namespace="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
        result_dict = {}
    
        # Iterate through the XML file paths
        for xml_path in array_of_xml_paths:
            # Parse the XML file
            tree = ET.parse(xml_path)
            root = tree.getroot()
    
            # Find all elements with the specified name
            elements = root.findall(".//{%s}%s" % (namespace, "TranskribusMetadata"))
    
            for element in elements:
                # Get the first attribute as the dictionary key
                
                key = element.get("pageId")
                
                # Use the remaining attributes as values
                attribute_names = ["pageNr", "imgUrl", "docId"]
                values = [element.get(attr) for attr in attribute_names]
    
                # Store the data in the dictionary
                result_dict[key] = values
    
    
        return result_dict
    
    def createTextLineDict(self, array_of_xml_paths):
        """
        This method will read the coords for every line in the document and
        will create a dictionary with the line identifiers as key and coords as value
        """
        
        namespace="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"
        result_dict = {}
    
        # Iterate through the XML file paths
        for xml_path in array_of_xml_paths:
            # Parse the XML file
            tree = ET.parse(xml_path)
            root = tree.getroot()
    
            # Find all elements with the specified name
            elements = root.findall(".//{%s}%s" % (namespace, "TextLine"))
    
            for element in elements:
                # Get the first attribute as the dictionary key
                
                key = element.get("id")
                
                data = []
                coords = element.find("{%s}Coords" % namespace)
                bounding_rect = self.bounding_rect(coords.get("points"))
                
                data.append(bounding_rect)
                
                # Store the data in the dictionary
                result_dict[key] = data
    
    
        return result_dict
    
    
    def bounding_rect(self, coords):
        """
        This method will create a bounding rectangle for a given set of points/coords
        """
        # Split the string into individual (x, y) pairs
        coordinates = [tuple(map(int, coord.split(',')) ) for coord in coords.split()]
    
        if not coordinates:
            return None  # No coordinates provided
    
        # Initialize variables to track min and max values
        min_x, min_y = float('inf'), float('inf')
        max_x, max_y = -float('inf'), -float('inf')
    
        # Find min and max values
        for x, y in coordinates:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
    
        # Calculate width and height of the bounding rectangle
        width = max_x - min_x
        height = max_y - min_y
    
        return str(min_x)+"x"+str(min_y)+"x"+str(width)+"x"+str(height)