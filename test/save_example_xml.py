from loader.read_results import get_event, xmlstring2file

eventid = 23906
xmlroot, resp = get_event(eventid)
xmlstring2file(resp, 'Example.xml')
