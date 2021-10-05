#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "DXC Technology"
__copyright__ = "© 2020 DXC Technology Services Company, LLC"
__credits__ = [""]
__license__ = ""
__version__ = "1.0.1"
__maintainer__ = "hsidelil"
__email__ = "hsidelil@dxc.com"
__status__ = "Production"
##################################################
## {Description}
## Removes PII tags (case insensitive) from change stream OSC xml file and saves a sanitized OSC output file 
## Usage: python sanitize_PII.py -i <input osc file name> -o <output osc file name> -t < list of tag names to be removed>
## e.g.: python sanitize_PII.py -i /home/ubuntu/daily_pr_osm.osc -o /home/ubuntu/daily_pr_osm_noPII.osc -t clientID COMPKEY
##################################################
## {License_info}
##################################################

import argparse
import xml.etree.ElementTree as ET

def read_osc_xml_file(in_osc_filename): 
    try:
        # load OSC XML file changeset from private OSM
        xtree = ET.parse(in_osc_filename) 
        in_osc_xml = xtree.getroot()
        if in_osc_xml.tag != "osmChange":
            print("file is not an OSC change stream")
            exit()
    except:
        print("exception error occured opening file") 
        exit()
    return in_osc_xml

def write_osc_xml_file(out_osc_filename, out_osc_xml):
    # write element tree object as osc xml change stream file 
    try:
        out_xtree=ET.ElementTree(out_osc_xml)
        out_xtree.write(out_osc_filename, encoding="utf-8", xml_declaration=True, method="xml")
    except:
        print("exception error occured writing file")
        exit()

def tag_remover(in_osc_xml, tag_to_rm):
    # removes specified tag from the element tree object of the osc xml change stream 
    count_rm=0
    for root_node in in_osc_xml:
        for child_node in root_node:
            for baby_node in child_node:
                if baby_node.tag == 'tag' and baby_node.attrib['k'].casefold()==tag_to_rm.casefold():
                    child_node.remove(baby_node)
                    count_rm+=1
    print("Number of times tag named: ", tag_to_rm," removed: ", count_rm) # removal status can be directed to log file
    return in_osc_xml  

def main(in_osc_filename, out_osc_filename, tags_to_rm):
    # open input osc file, remove specified tags and save sanitized output osc file 
    in_osc_xml = read_osc_xml_file(in_osc_filename)
    for tag in tags_to_rm:
        out_osc_xml = tag_remover(in_osc_xml,tag)
    write_osc_xml_file(out_osc_filename, out_osc_xml)


if __name__ == "__main__":
    # accept program command line arguments  
    parser = argparse.ArgumentParser(description='Enter file names and tag names be removed')

    parser.add_argument("-i", required=True, type=str, help="Input File Name")
    parser.add_argument("-o", required=True, type=str, help="Output File Name")
    parser.add_argument("-t", nargs='+', required=True, type=str, help="Tag names list to be removed")
    
    args = parser.parse_args()
    in_osc_filename = args.i
    out_osc_filename = args.o
    tags_to_rm = args.t
    main(in_osc_filename, out_osc_filename, tags_to_rm)
    

