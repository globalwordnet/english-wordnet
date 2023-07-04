import xml.etree.ElementTree as ET

e = ET.parse('ubuntu_list.html').getroot()

for tr in e.findall('tr'):
    print(','.join(td.text.strip() for td in tr.findall('td')))
