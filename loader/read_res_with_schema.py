import xmlschema
from xml.etree import ElementTree
import os
from loader.loader_utils import rel2fullpath, getexample
#from pprint import pprint

xsdfile = os.path.join(rel2fullpath('input'), 'EventorApi.xsd')

xs = xmlschema.XMLSchema(xsdfile)

xmlfile = getexample()
xt = ElementTree.parse(xmlfile)

eventid = 23906
xmlroot, resp = get_event(eventid)

root = xt.getroot()
#pprint(xs.elements['cars'].decode(root[0]))