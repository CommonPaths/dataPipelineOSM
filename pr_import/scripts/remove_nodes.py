# /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "DXC Technology"
__copyright__ = "“© 2020 DXC Technology Services Company, LLC"
__credits__ = [""]
__license__ = ""
__version__ = "1.0.5"
__maintainer__ = "rpatel226"
__email__ = "rpatel226@dxc.com"
__status__ = "Production"
##################################################
## {Description}
## User Story: MTN-83 Ability to extract bounding box data from planet change set
## Remove all the nodes as well as nodes from WAY and RELATION that are not inside the bounding box from a given changeset.
## Usage: python remove_nodes.py [-h] -f <Change_set FILENAME> [-latmin <MINIMUM_LATITUDE>] [-latmax <MAXIMUM_LATITUDE>] [-lonmin <MINIMUM_LONGITUDE>] [-lonmax <MAXIMUM_LONGITUDE>] [-o <OUTPUT_FILENAME>]
## Additional Instructions: The bbox_node_id.txt , bbox_rel_id.txt and bbox_way_id.txt file should all be in the same directory as that of remove_nodes.py code file
## e.g.: python remove_nodes.py -f Trial.osc -latmin 47.070017 -latmax 47.794933 -lonmin -122.549826 -lonmax -121.044524 -o output2.osc
##################################################
## {License_info}
##################################################
import argparse
import xml.etree.ElementTree as ET
from lxml import etree
import os
import ast

def write_to_file(elem_set,name):
    f_elem = open(name,'w')
    for elem in elem_set:
        f_elem.write(elem)
        f_elem.write("\n")
    f_elem.close()

def read_set_from_file(name):
    f_node_list=open(name)
    bbox_list=[]
    for line in f_node_list:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]
            # add item to the list
            bbox_list.append(str(currentPlace))
    return set(bbox_list)



def remove_nodes(root,latmin,latmax,lonmin,lonmax):
    unwanted_nodes = set()
    wanted_nodes = set()
    for m_d_c in root:
        for node in m_d_c.findall('node'):
            lon = float(node.attrib['lon'])
            lat = float(node.attrib['lat'])
            if(((lat < latmin) or (lat > latmax)) or ((lon < lonmin) or (lon > lonmax))):
                unwanted_nodes.add(node.attrib['id'])
                m_d_c.remove(node)
            else:
                wanted_nodes.add(node.attrib['id'])
    return root,set(wanted_nodes)

def remove_from_way(root,wanted_nodes,NODE_ID):
    unwanted_way = set()
    wanted_way = set()
    for m_d_c in root:
        for way in m_d_c.findall('way'):
            flag = 0
            for node in way.findall('nd'):
                if((node.attrib.get('ref') in wanted_nodes) or (node.attrib.get('ref') in NODE_ID)):
                    flag = 1
                    break
            if(flag == 0):
                unwanted_way.add(way.attrib.get('id'))
                m_d_c.remove(way)
            else:
                wanted_way.add(way.attrib.get('id'))
    return root,set(wanted_way)

def remove_from_relation(root,wanted_way,wanted_nodes,NODE_ID,WAY_ID,REL_ID):
    wanted_rel = set()
    for m_d_c in root:
        for rel in m_d_c.findall('relation'):
            flag = 0
            for member in rel.findall('member'):
                if(member.attrib.get('type') == 'node'):
                    if((member.attrib.get('ref') in wanted_nodes) or (member.attrib.get('ref') in NODE_ID)):
                        flag = 1
                        break
                elif(member.attrib.get('type') == 'way'):
                    if((member.attrib.get('ref') in wanted_way) or (member.attrib.get('ref') in WAY_ID)):
                        flag = 1
                        break
                elif(member.attrib.get('type') == 'relation'):
                    if((member.attrib.get('ref') in wanted_rel) or (member.attrib.get('ref') in REL_ID)):
                        flag = 1
                        break
            if(flag == 0):
                m_d_c.remove(rel)
            else:
                wanted_rel.add(rel.attrib.get('id'))
    return root,wanted_rel

def remove_empty_elements_helper(root,m_d_c):
    for elem in m_d_c:
        if(len(elem) == 0):
            root.remove(elem)

def remove_empty_elements(root):
    remove_empty_elements_helper(root,root.findall('modify'))
    remove_empty_elements_helper(root,root.findall('create'))
    remove_empty_elements_helper(root,root.findall('delete'))

def main(f_name,lonmin,lonmax,latmin,latmax,output_fname):

    #Read the ids of elements saved from previous osm files
    node_filename = "bbox_node_id.txt"
    way_filename = "bbox_way_id.txt"
    rel_filename = "bbox_rel_id.txt"
    NODE_ID = read_set_from_file(node_filename)
    WAY_ID = read_set_from_file(way_filename)
    REL_ID = read_set_from_file(rel_filename)

    #Read in the current changeset
    tree = ET.parse(f_name)
    root = tree.getroot()

    #Remove all the nodes outside the bounding box coordinates
    vals = remove_nodes(root,latmin,latmax,lonmin,lonmax)
    root = vals[0]
    wanted_nodes_exclv = vals[1]

    #Remove all the ways that do not contain nodes inside bounding box or
    #nodes inside the OSM file node ids(N)
    vals = remove_from_way(root,wanted_nodes_exclv,NODE_ID)
    root = vals[0]
    wanted_way_exclv = vals[1]

    #Remove all the rels that do not contain nodes,way,relation inside bounding box or
    #relation inside the OSM file node ids(N)
    vals = remove_from_relation(root,wanted_way_exclv,wanted_nodes_exclv,NODE_ID,WAY_ID,REL_ID)
    root = vals[0]
    wanted_rel_exclv = vals[1]

    #Append the new found nodes,way,relation to the old ids of odm files
    new_N = NODE_ID.union(wanted_nodes_exclv)
    new_W = WAY_ID.union(wanted_way_exclv)
    new_R = REL_ID.union(wanted_rel_exclv)


    #Remove emplt elements of the tree and write the new changeset file to the
    #current directory
    remove_empty_elements(root)
    tree.write(output_fname)

    #Remove old id files from the current directory
    os.remove(node_filename)
    os.remove(way_filename)
    os.remove(rel_filename)

    #Write New id files to the current directory
    write_to_file(new_N,node_filename)
    write_to_file(new_W,way_filename)
    write_to_file(new_R,rel_filename)


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-f","--filename",type=str,required = True, help="The input changeset file name(required)")
    ap.add_argument("-latmin","--minimum_latitude",type=float,default = 47.070017, help="The minimum latitude of the bounding box(optional)")
    ap.add_argument("-latmax","--maximum_latitude",type=float,default = 47.794933, help="The maximum latitude of the bounding box(optional)")
    ap.add_argument("-lonmin","--minimum_longitude",type=float,default = -122.549826, help="The minimum longitude of the bounding box(optional)")
    ap.add_argument("-lonmax","--maximum_longitude",type=float,default = -121.044524, help="The maximum longitude of the bounding box(optional)")
    ap.add_argument("-o","--output_filename",type=str,default="output.osc",help="The output changeset file name(optional)")

    args = vars(ap.parse_args())

    f_name = args["filename"]

    lonmin = args["minimum_longitude"]
    lonmax = args["maximum_longitude"]
    latmin = args["minimum_latitude"]
    latmax = args["maximum_latitude"]

    output_fname = args["output_filename"]

    main(f_name,lonmin,lonmax,latmin,latmax,output_fname)
