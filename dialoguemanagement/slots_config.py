import configparser
import json

with open("../resources/CamRestaurants-rules.json") as file: #original path: resources//CamRestaurants-rules.json
    ontology = json.load(file)
# print(ontology['slots']) # yields a list: ['food', 'pricerange', 'name', 'area', 'signature', 'postcode', 'phone', 'addr']

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("Slots Configurations")

# ADD SETTINGS TO SECTION
# possible values come as lists, to be easily searchable
#first argument as section name, second as key and third as value.
# config_file.set("Slots Configurations", "slot_name", "['list', 'of', 'valid', 'values'") # blueprint

config_file.set("Slots Configurations", "valid_intents", "['find.restaurant', 'request.information', 'return.restaurant', 'return.information', 'ask.information']")
# possible intent for input and output in same list.

valid_areas = ["Don't care"] + ontology["slotvalues"]["area"]
config_file.set("Slots Configurations", "valid_areas", str(valid_areas))

valid_prices = ["Don't care"] + ontology["slotvalues"]["pricerange"]
config_file.set("Slots Configurations", "valid_priceranges", str(valid_prices))

valid_foods = ["Don't care"] + ontology["slotvalues"]["food"]
config_file.set("Slots Configurations", "valid_types", str(valid_foods))

valid_names = ["Don't care"] + ontology["slotvalues"]["name"]
config_file.set("Slots Configurations", "valid_restos", str(valid_names))


# SAVE CONFIG FILE
with open(r"slots_config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Slot Value Config file 'slots_config.ini' created")

# PRINT FILE CONTENT
read_file = open("slots_config.ini", "r")
content = read_file.read()
print("Content of the slots_config file are:\n")
print(content)
read_file.flush()
read_file.close()