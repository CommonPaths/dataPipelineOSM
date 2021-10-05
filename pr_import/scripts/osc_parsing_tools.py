# -*- coding: utf-8 -*-

import xml.etree.ElementTree as et

def list_of_nodes_from_osc(root, element = '*'):
    node_ids = set()
    for node in root.findall("./" + element + "/"):
        node_ids.add(node.attrib['id'])
    return node_ids

def node_ids_unique_to_public(public_ids, private_ids):
    return list(public_ids - private_ids)

def node_ids_shared_between_public_and_private(public_ids, private_ids):
    return list(public_ids & private_ids)

def find_node_element_by_id(node_id, modify_element):
    query_string = "./node[@id='" + str(node_id) + "']"
    node_element = modify_element.find(query_string)
    return node_element

# def find_node_element_by_id(node_id, osc_root, child_element = '*'):
#   nodes = osc_root.findall("./" + child_element)
#   query_string = "./node[@id='" + str(node_id) + "']"
#   node_elements = []
#   for node in nodes:
#     node_element = node.find(query_string)
#     if node_element is not None:
#       node_elements.append(node_element)
#   return node_elements

def remove_node_from_change_set(node_id, modify_element):
    node_element = find_node_element_by_id(node_id, modify_element)
    modify_element.remove(node_element)

def remove_nodes_given_an_array_of_nodes(array_of_node_ids, modify_element):
    for node_id in array_of_node_ids:
        remove_node_from_change_set(node_id, modify_element)

def find_all_node_elements(root_element):
    return root_element.findall("./modify/node")

def find_all_delete_elements(root_element):
    return root_element.findall("./delete/node")
  
def list_of_deleted_nodes(root_element):
    delete_nodes = find_all_delete_elements(root_element)
    delete_node_ids = set()
    for node in delete_nodes:
        delete_node_ids.add(node.attrib['id'])
    return list(delete_node_ids)


#########Kireet's Functions##########
    
def include_source_tag(root):
    for node in root.findall("./create/"):
        for child in node:
            if child.tag == 'tag' and child.attrib['k']=='source':
                break
        new_tag = et.SubElement(node, 'tag')
        new_tag.attrib["k"] = 'source'
        new_tag.attrib["v"] = 'KCM'
    return root

def list_of_nodes_with_source(root):
    node_ids1 = set()
    for node in root.findall("./create/"):
        for baby_node in node:
            if baby_node.tag == 'tag' and baby_node.attrib['k']=='source':
                node_ids1.add(node.attrib['id'])
    return node_ids1


def list_of_lat_lon_osc(array_of_nodes_with_source,root):
    lat_lon =[]
    for node_id in array_of_nodes_with_source:
        for node in root.findall("./create/"):
            if node.tag == 'node' and node.attrib['id']==node_id:
                temp=[]
                temp.append(node.attrib['lat'])
                temp.append(node.attrib['lon'])
        lat_lon.append(temp)
    return lat_lon

    
def lat_lon_comparision_private_public(private_lat_lon,public_lat_lon):
    duplicated_coordinate=[]
    for coordinate in private_lat_lon:
        if coordinate in public_lat_lon:
            duplicated_coordinate.append(coordinate)
    return duplicated_coordinate


def remove_nodes_given_list_of_coordinates(duplicated_coordinate,root):
    for lat,lon in duplicated_coordinate:
        for root_coordinate in root:
            for child_coordinate in root_coordinate:
                if child_coordinate.tag == 'node' and child_coordinate.attrib['lat']==lat and child_coordinate.attrib['lon']==lon:
                    root_coordinate.remove(child_coordinate)
    return root

def list_of_new_nodes_from_public(list_of_nodes,list_of_nodes_with_source):
    return (list_of_nodes - list_of_nodes_with_source)


#################     Tag_By_Tag_Reconciliation            ##############################


def tag_by_tag_reconciliation(duplicated_coordinate,private_root,public_root):
    for lat,lon in duplicated_coordinate:
        new_tags_in_private = extract_tag_value(lat,lon,private_root,public_root)
        for k,v in new_tags_in_private.items():
            for node in public_root.findall("./create/"):
                if node.tag == 'node' and node.attrib['lat']==lat and node.attrib['lon']==lon:
                    new_tag=et.SubElement(node,'tag')
                    new_tag.attrib["k"] = k
                    new_tag.attrib["v"] = v
    return public_root

        
def extract_tag_value(lat,lon,private_root,public_root):
    private_tags={}
    public_tags={}
    for root_coordinate in private_root.findall("./create/"):
        if root_coordinate.tag == 'node' and root_coordinate.attrib['lat']==lat and root_coordinate.attrib['lon']==lon:
            for child_coordinate in root_coordinate:
                private_tags.update({child_coordinate.attrib['k']: child_coordinate.attrib['v']})
    for root_coordinate in public_root.findall("./create/"):
        if root_coordinate.tag == 'node' and root_coordinate.attrib['lat']==lat and root_coordinate.attrib['lon']==lon:
            for child_coordinate in root_coordinate:
                public_tags.update({child_coordinate.attrib['k']: child_coordinate.attrib['v']})
    tag_compare = tag_comparison(private_tags,public_tags)
    return(tag_compare)

    
def tag_comparison(private_tags,public_tags):
    for k, v in (private_tags.items()&public_tags.items()):
        private_tags.pop(k)
    return(private_tags)
