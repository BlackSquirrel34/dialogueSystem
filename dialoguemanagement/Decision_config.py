import configparser
# at the moment this file is not necessary, only the slots_config

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("DialogueDecider Settings")

# ADD SETTINGS TO SECTION
#first argument as section name, second as key and third as value.
# if you change key values here, remember to adapt their "call" in dialoguedecision-file. only values can be changed without that.

config_file.set("DialogueDecider Settings", "ask.intent", "'ask.information'") # „Bitte spezifiziere den intent!“
config_file.set("DialogueDecider Settings", "ask.area", "ask.information, ['area']") # „Bitte spezifiziere die area!“
config_file.set("DialogueDecider Settings", "ask.pricerange", "ask.information, ['pricerange']") # „Bitte gib eine Pricerange an!“
config_file.set("DialogueDecider Settings", "ask.type", "ask.information, ['type']") # „Bitte spezifiziere den foodtype!“
config_file.set("DialogueDecider Settings", "ask.specific.restaurant", "ask.information, [specific.restaurant]") # "Mehr Infos über welches Restaurant?"
config_file.set("DialogueDecider Settings", "return.restaurant", "return.restaurant, [state.resultList, state.retrievedList]") # „Hier ist die Resultlist mit den passenden Restaurants…“
config_file.set("DialogueDecider Settings", "return.information", "return.information, [state.resultList]") # „Hier kommen weitere Infos zu dem von dir gewählten Restaurant…“

# SAVE CONFIG FILE
with open(r"decider_config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'decider_config.ini' created")

# PRINT FILE CONTENT
read_file = open("decider_config.ini", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()

