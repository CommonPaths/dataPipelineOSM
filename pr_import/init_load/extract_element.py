# /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "DXC Technology"
__copyright__ = "“© 2020 DXC Technology Services Company, LLC"
__credits__ = [""]
__license__ = ""
__version__ = "1.0.2"
__maintainer__ = "rpatel226"
__email__ = "rpatel226@dxc.com"
__status__ = "Production"
##################################################
## {Description}
## User Story: MTN-105 Create list of nodes,way and relation in bounding box and update as change sets comes in
## Extract the id of all the nodes, ways and relation from the osm file of a bounding box.
## Usage: python extract_element.py [-h] -f <osm FILENAME>
## e.g.: python extract_element.py -f kcmonly.osm
##################################################
## {License_info}
##################################################

import xml.etree.ElementTree as ET
import argparse


def extract_element(f_name):

    #osm_filename="new_filter.osm"
    osm_filename = f_name
    nodes_filename="bbox_node_id.txt"
    ways_filename="bbox_way_id.txt"
    relations_filename="bbox_rel_id.txt"

    print("Extracting Nodes, Ways and Relations, id's")
    parser = ET.iterparse(osm_filename,events=("start","end"))
    f_nodes = open(nodes_filename,'w')
    f_ways = open(ways_filename,'w')
    f_relations = open(relations_filename,'w')

    for event, elements in parser:
        if elements.tag == 'node':
            if elements.attrib != {}:
                f_nodes.write(elements.attrib['id'])
                f_nodes.write("\n")
        elif elements.tag == 'way':
            if elements.attrib != {}:
                f_ways.write(elements.attrib['id'])
                f_ways.write("\n")
                for way_elements in elements:
                    if way_elements.tag =='nd':
                        f_nodes.write(way_elements.attrib['ref'])
                        f_nodes.write("\n")
        elif elements.tag == 'relation':
            if elements.attrib != {}:
                f_relations.write(elements.attrib['id'])
                f_relations.write("\n")
                for way_elements in elements:
                    if way_elements.tag =='member':
                        if way_elements.attrib['type'] == 'node':
                            f_nodes.write(way_elements.attrib['ref'])
                            f_nodes.write("\n")
                        elif way_elements.attrib['type'] == 'way':
                            f_ways.write(way_elements.attrib['ref'])
                            f_ways.write("\n")
                        elif way_elements.attrib['type'] == 'relation':
                            f_relations.write(way_elements.attrib['ref'])
                            f_relations.write("\n")
        elements.clear()
    del parser

    f_nodes.close()
    f_ways.close()
    f_relations.close()

    print('finished')

def main(f_name):
    filename = f_name
    extract_element(f_name)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-f","--filename",type=str,required = True, help="The OSM filename of bounding box")
    args = vars(ap.parse_args())
    f_name = args["filename"]
    main(f_name)
