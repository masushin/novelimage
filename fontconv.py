import argparse
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser()
parser.add_argument("infile")
args = parser.parse_args()

tree = ET.parse(args.infile)
root = tree.getroot()

list_index = []
cid_replace_dic = {}

for gsub_elements in root.iter('GSUB'):
    for featurerecords in gsub_elements.iter('FeatureRecord'):
        for featuretags in featurerecords.iter('FeatureTag'):
            if featuretags.attrib['value'] == "vert" or \
                    featuretags.attrib['value'] == "vrt2" or \
                    featuretags.attrib['value'] == "vtrt":
                for lookuplistindexs in featurerecords.iter('LookupListIndex'):
                    if not lookuplistindexs.get('value') in list_index:
                        list_index.append(lookuplistindexs.get('value'))

    for lookup in gsub_elements.iter('Lookup'):
        if lookup.get('index') in list_index:
            for substitution in lookup.iter('Substitution'):
                cid_replace_dic[substitution.get('in')] = substitution.get('out')


for cmap in root.iter('cmap'):
    for maps in cmap.iter('map'):
        if maps.get('name') in cid_replace_dic.keys():
            maps.set('name', cid_replace_dic[maps.get('name')])

tree.write("output.xml")
