# -*- coding: utf-8 -*-
__author__ = "DXC Technology"
__copyright__ = "© 2020 DXC Technology Services Company, LLC"
__credits__ = [""]
__license__ = ""
__version__ = "1.0.1"

import xml.etree.ElementTree as et
import sys, getopt
import osc_parsing_tools as op
import requests
import json
import argparse

def main(argv): #, private_osc_file, public_osc_file):

    private_osc_file = ''
    public_osc_file = ''
 
    try:
      opts, args = getopt.getopt(sys.argv[1:],'h:r:u:',['help', 'privatefile=', 'publicfile='])
    except getopt.GetoptError:
      print('osc_parser.py -r <private_osc_file> -u <public_osc_file>')
      sys.exit(2)
  
    for opt, arg in opts:
      if opt in ('-h', '--help'):
        sys.exit(2)
      elif opt in ('-r', '--privatefile'):
        private_osc_file = arg
      elif opt in ('-u', '--publicfile'):
        public_osc_file = arg
      else:
        sys.exit(2)

    private_osc = et.parse(private_osc_file)
    public_osc = et.parse(public_osc_file)  
    public_root = public_osc.getroot()
    private_root = private_osc.getroot() 

    private_node_ids = op.list_of_nodes_from_osc(private_root, 'modify')    
    public_node_ids = op.list_of_nodes_from_osc(public_root, 'modify')
    
    public_node_ids_create = op.list_of_nodes_from_osc(public_root, 'create')
    nodes_with_source_private = op.list_of_nodes_with_source(private_root)
    nodes_with_source_public = op.list_of_nodes_with_source(public_root)
    private_lat_lon_with_source = op.list_of_lat_lon_osc(nodes_with_source_private, private_root)
    public_lat_lon_with_source = op.list_of_lat_lon_osc(nodes_with_source_public, public_root)
    list_of_duplicated_coordinates = op.lat_lon_comparision_private_public(private_lat_lon_with_source, public_lat_lon_with_source)

    op.include_source_tag(private_root)
    op.tag_by_tag_reconciliation(list_of_duplicated_coordinates,private_root,public_root)
    op.remove_nodes_given_list_of_coordinates(list_of_duplicated_coordinates,private_root)
    op.list_of_new_nodes_from_public(public_node_ids_create,nodes_with_source_public)
    shared_nodes = nodes_shared_by_both_changesets(public_node_ids, private_node_ids, public_osc, private_osc)
    flag_deleted_nodes_for_review(public_root, public_osc, private_osc)
    identify_nodes_only_modified_public(public_node_ids, private_node_ids, public_osc, private_osc)
    
    if shared_nodes:
      sys.exit('33')

def nodes_shared_by_both_changesets(public_node_ids, private_node_ids, public_osc, private_osc):
  shared_nodes = op.node_ids_shared_between_public_and_private(public_node_ids, private_node_ids)
  for node_id in shared_nodes:
      send_node_to_db(node_id, public_osc, private_osc, "modify", True)
  return shared_nodes

def flag_deleted_nodes_for_review(public_root, public_osc, private_osc):
  deleted_nodes = op.list_of_deleted_nodes(public_root)
  for node_id in deleted_nodes:
      send_node_to_db(node_id, public_osc, private_osc, 'delete')
  return deleted_nodes

def identify_nodes_only_modified_public(public_node_ids, private_node_ids, public_osc, private_osc):
  nodes_modified_only_in_public = op.node_ids_unique_to_public(public_node_ids, private_node_ids)
  for node_id in nodes_modified_only_in_public:
      send_node_to_db(node_id, public_osc, private_osc, 'modify')
  return nodes_modified_only_in_public

def send_node_to_db(node_id, public_osc, private_osc, xml_element_type, req_manual_recon = False):
    public_element = public_osc.getroot().find("./" + xml_element_type + "/node[@id='" + str(node_id) + "']")
    private_element = private_osc.getroot().find("./" + xml_element_type + "/node[@id='" + str(node_id) + "']")
    # TODO: turn url into an environment variable
    url = 'http://ec2-3-225-236-8.compute-1.amazonaws.com:3000/reconciliation/create'

    if public_element is not None:
        params_to_send = build_params(public_element, private_element, xml_element_type, req_manual_recon)
        r = requests.put(url, params = params_to_send)

def build_params(public_node_element, private_node_element, xml_element_type, req_manual_recon):
    params_to_send = {}
    params_to_send.update({'type_of_change': xml_element_type,
                         'req_manual_recon': str(req_manual_recon),
                          'node_id': public_node_element.attrib['id'],
                          'public_node_tags': json.dumps(extract_tag_values_from_node(public_node_element)),
                          'public_node_data': json.dumps(public_node_element.attrib)})
    if private_node_element is not None:
        params_to_send['private_node_data'] = json.dumps(private_node_element.attrib)
        params_to_send.update({'private_node_data': json.dumps(private_node_element.attrib),
                               'private_node_tags': json.dumps(extract_tag_values_from_node(private_node_element))})
    return params_to_send

def extract_tag_values_from_node(node):
    tags = {}
    tag_elements = (node.findall('./tag'))
    for tag in tag_elements:
        tags.update({tag.attrib['k']: tag.attrib['v']})
    return tags
  
if __name__ == "__main__":
    # accept program command line arguments  
#    parser = argparse.ArgumentParser(description='Enter private and public file names')
#
#    parser.add_argument("-r", required=True, type=str, help="Private File Name")
#    parser.add_argument("-u", required=True, type=str, help="Public File Name")
#    
#    args = parser.parse_args()
#    privatefilename = args.r
#    publicfilename = args.u
    main(sys.argv[1:]) # , privatefilename, publicfilename)
