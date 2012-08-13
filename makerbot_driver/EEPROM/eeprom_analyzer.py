"""
Analyzes the eeprom map in the Mightyboards Source code's
Eeprom.hh file.  Expects blocks of information in the form of:
//$BEGIN_ENTRY
//$S:<some size>
const static uint16_t <some name> = <some address>

Takes the above information and turns it into a python
dict in the form of:
{
  <some name> : {
      size  : <some size>,
      address : <some address>,
      }
}
"""

class EndOfNamespaceError(IOError):
  def __init__(self):
    pass

class EndOfEepromError(IOError):
  def __init__(self):
    pass

import json

class eeprom_analyzer(object):

  def __init__(self):
    self.filename = 'eeprom_map.json'
    self.eeprom_map = {}

  def parse_file(self):
    self.eeprom_map = {}
    try:
      while True:
        namespace_name = self.find_next_namespace().lower()
        namespace = {}
        try:
          while True:
            self.find_next_entry()
            variables = self.parse_out_variables(self.file.readline())
            (name, location) = self.parse_out_name_and_location(self.file.readline())
            v = {
                'offset'  : location,
                }
            for variable in variables:
              variable = variable.split(':')
              v[variable[0]] = variable[1]
            namespace[name] = v
        except EndOfNamespaceError:
          self.eeprom_map[namespace_name]  = namespace
    except EndOfEepromError:
      collated_map = {'eeprom_map' : self.collate_maps(self.eeprom_map['eeprom_offsets'])}
      self.dump_json('eeprom_map.json', collated_map)
      
  def find_next_entry(self):
    namespace_end = '}'
    entry_line = '//$BEGIN_ENTRY'
    line = self.file.readline()
    while entry_line not in line:
      if namespace_end in line:
        raise EndOfNamespaceError
      line = self.file.readline()
    return line

  def find_next_namespace(self):
    """
    Reads lines from the file until a line that 
    starts with namespace is encountered.  The name 
    of that namespace is then parsed out and returned.

    @return str name: The name of the current namespace
    """
    namespace = 'namespace'
    end_of_eeprom = '#endif'
    line = self.file.readline()
    while not line.startswith(namespace):
      if end_of_eeprom in line:
        raise EndOfEepromError
      line = self.file.readline()
    return self.parse_out_namespace_name(line)

  def parse_out_namespace_name(self, line):
    """
    Given a line in the form of 
      "namespace <name> {"
    parses out the name
  
    @param str line: The line with the namespace
    @return str name: The name of the namespace 
    """
    line = line.strip()
    for s in ['\n', '\r', '\t', '{']:
      line = line.rstrip(s)
    line = line.lstrip('namespace')
    line = line.replace(' ', '')
    return line

  def parse_out_name_and_location(self, line):
    """
    Given a line in the form of:
      const static uint16_t <name> = <location>;
    parses out the name and location.
    If we get a line not of this form, we will fail.

    @param str line: the line we want information from
    @return tuple: Information in the form of (name, location)
    """
    for w in ['const', 'static', 'uint16_t']:
      line = line.replace(w, '')
    for s in ["\r", "\n", ";"]:
      line = line.rstrip(s)
    line = line.replace('\t', '')
    line = line.replace(" ", "")
    (name, location) = line.split("=")
    return name, location

  def parse_out_variables(self, line):
    line = line.strip()
    for s in ['\n', '\r', '\t',]:
      line = line.rstrip(s)
    line = line.lstrip('//')
    line = line.replace(' ', '')
    parts = line.split('$')
    #Dont return the first, since its empty
    return parts[1:]

  def dump_json(self, name, eeprom_map):
    output = json.dumps(eeprom_map, sort_keys=True, indent=2) 
    with(open(name, 'w')) as f:
      f.write(output)

  def collate_maps(self, the_map):
#    main_map = 'eeprom_offsets'
#    collated_map = self.eeprom_map[main_map]
    collated_map = the_map
#    for key in self.eeprom_map[main_map]:
    for key in the_map:
#      if 'eeprom_map' in self.eeprom_map[main_map][key]:
      if 'eeprom_map' in the_map[key]:
#        sub_map_name = self.eeprom_map[main_map][key]['eeprom_map']
        sub_map_name = the_map[key]['eeprom_map']
        collated_map[key]['sub_map'] = self.eeprom_map[sub_map_name]
        self.collate_maps(collated_map[key]['sub_map'])
#    collated_map = {'eeprom_map'  : collated_map}
    return collated_map