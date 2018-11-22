import requests
import xml.etree.ElementTree as ET
import os
from bs4 import BeautifulSoup

url = "https://eventor.orientering.se/api/results/event"
apikey = os.environ["apikey"]
headers = {'ApiKey': apikey}
#eventid = 18667
eventid = 23906

response = requests.get(url, headers=headers, params={'eventId': eventid, 'includeSplitTimes': False})

root = ET.fromstringlist(response.text)
#soup = BeautifulSoup(response.text, 'html.parser')
#print(soup.prettify())
#print(root)

# for child in root:
#     # print('-------------------')
#     # print(child.tag)
#     # print(child.attrib)
#     print(child.text)
#     for child2 in child:
#         # print('******************')
#         # print(child.tag + '/' +child2.tag)
#         # print(child2.attrib)
#         for child3 in child2:
#             # print('3:  ')
#             print(child.tag + '/' + child2.tag + '/' + child3.tag)
#             # print(child3.attrib)
#             # print(child3.text)
#             for child4 in child3:
#                 print(child.tag + '/' + child2.tag + '/' + child3.tag+ '/' + child4.tag)
#                 # print(child4.tag)
#                 # print(child4.attrib)
#                 # print(child4.text)



# for racename in root.findall('ClassResult/EventClass/Name'):
#     print('+++')
#     print(racename.text)
#     # personresult.get('Person')
#     # personresult.get('Result')
#     # personresult.get('Organisation')

# for x in root.findall('ClassResult/PersonResult/Result/'):
#     x.get('ResultPosition')
#     print(str(x.tag) + ': ' + str(x.text))
#     print('++++ ')

for x in root.findall('ClassResult'):
    print(x.attrib)
    obj_eventclass = x.find('EventClass')
    eventname = obj_eventclass.find('Name').text
    print(eventname)

    for y in x.findall('PersonResult'):
        obj_person = y.find('Person')
        name = obj_person.find('PersonName/Given').text +' ' + obj_person.find('PersonName/Family').text
        position = obj_person.find('PersonName/Given').text

        obj_org = y.find('Organisation')
        if obj_org==None:
            orgid = '?'
        else:
            orgid = obj_org.find('OrganisationId').text


        obj_res = y.find('Result/ResultPosition')
        if obj_res==None:
            position = 'x'
        else:
            position = obj_res.text
        print(name + ' ' + position)
    print('++++ ')

print('Finished')


