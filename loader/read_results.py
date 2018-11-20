import requests
import xml.etree.ElementTree as ET
import os

url = "https://eventor.orientering.se/api/results/event"
apikey = os.environ["apikey"]
headers = {'ApiKey': apikey}
#eventid = 18667
eventid = 23906

response = requests.get(url, headers=headers, params={'eventId': eventid, 'includeSplitTimes': False})

root = ET.fromstringlist(response.text)
print(root)

for child in root:
    # print('-------------------')
    # print(child.tag)
    # print(child.attrib)
    print(child.text)
    for child2 in child:
        # print('******************')
        # print(child.tag + '/' +child2.tag)
        # print(child2.attrib)
        for child3 in child2:
            # print('3:  ')
            print(child.tag + '/' + child2.tag + '/' + child3.tag)
            # print(child3.attrib)
            # print(child3.text)
            for child4 in child3:
                print(child.tag + '/' + child2.tag + '/' + child3.tag+ '/' + child4.tag)
                # print(child4.tag)
                # print(child4.attrib)
                # print(child4.text)



for racename in root.findall('ClassResult/EventClass/Name'):
    print('+++')
    print(racename.text)
    # personresult.get('Person')
    # personresult.get('Result')
    # personresult.get('Organisation')

for x in root.findall('ClassResult/PersonResult/Result/'):
    x.get('ResultPosition')
    print(str(x.tag) + ': ' + str(x.text))
    print('++++ ')

print('Finished')


