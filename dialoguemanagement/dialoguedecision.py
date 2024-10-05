from datastructures.dialoguestate import DialogueState
from datastructures.dialogueact import DialogueAct
import configparser

# Method to read config file settings for slots
def read_slot_config():
    config = configparser.ConfigParser()
    config.read('dialoguemanagement/slots_config.ini') # check for correct path. depends on environment.
    # if in another environment (IDE, git) the path is no longer known, there'll be a keyerror.
    return config

# call reading methods
slotConfig = read_slot_config()

# read slot configurations from config-file: section name first, then section key.
# valid_intents and all the others is going to be a list that can be checked for occurence with in operator:
valid_intents = slotConfig['Slots Configurations']['valid_intents']
valid_areas = slotConfig['Slots Configurations']['valid_areas']
valid_priceranges = slotConfig['Slots Configurations']['valid_priceranges']
valid_types = slotConfig['Slots Configurations']['valid_types']
valid_restos = slotConfig['Slots Configurations']['valid_restos'] #all restos existing


class DialogueDecider(object):

    def __init__(self):
        pass

 #definition area
    def actOn(self, state:DialogueState) -> DialogueAct:
# create empty lists
        intentList = []
        areaList = []
        pricerangeList = []
        typeList = []
        specificRestaurantList = []
        ofInterestList = []

#pull values from DialogueAct into lists
        intentList.append(state['intent'])
        areaList.append(state['area'])
        pricerangeList.append(state['pricerange'])
        typeList.append(state['food'])
        specificRestaurantList.append(state['specificRestaurant'])
        ofInterestList.append(state['ofInterest'])

        # print("\n ########### what lists look alike without flattening... ")
       #  print(intentList)

# flatten lists for further parsing
        intentList = sum(intentList, [])
        areaList = sum(areaList, [])
        pricerangeList = sum(pricerangeList, [])
        typeList = sum(typeList, [])
        specificRestaurantList = sum(specificRestaurantList, [])
        ofInterestList = sum( ofInterestList, [])

      #  print("\n ########### successfully flattened the list?")
      #  print(intentList)
      #  print(areaList)

        # in a state, there are: dict_keys(['intent', 'food', 'pricerange', 'name', 'area', 'signature',
        # 'postcode', 'phone', 'addr','specificRestaurant', 'ofInterest'])
        # and also: dummyStateInstance.retrievedList and  dummyStateInstance.resultList (originally [])

#dummy: systemAction = DialogueAct("ask.information", outputList = ["area"])
# decision rules
        if intentList != []:
            intentList = intentList[-1:]
            for intent in intentList:
                if intent not in valid_intents:
                    askintent = DialogueAct()   
                    askintent.create("ask.information", outputList = ['intent'])    #askintent.create instantiates the actual DialogueAct named askintent
                    return askintent # „Bitte spezifiziere den intent!“

                elif any("find.restaurant" in str for str in intentList): # find.restaurant got detected. so next?

                    if areaList != []:
                        for area in areaList:
                            if area not in valid_areas:
                                askarea = DialogueAct()
                                askarea.create("ask.information", outputList = ['area'])
                                return askarea  # "Please define some area!"
                                break

                            elif area in valid_areas: # some area got specified/ don't care
                            # find.restaurant detected, area valid? let's check for the pricerange!
                                if pricerangeList != []:
                                    for pricerange in pricerangeList:
                                        if pricerange not in valid_priceranges:
                                            askpricerange = DialogueAct()
                                            askpricerange.create("ask.information", outputList = ['pricerange'])
                                            return askpricerange    # "please specify a pricerange!"

                                        elif pricerange in valid_priceranges:
                                    # find.restaurant detected, area, pricerange valid? let's check for the type!

                                            if typeList != []:
                                                for type in typeList:
                                                    if type not in valid_types:
                                                        asktype = DialogueAct()
                                                        asktype.create("ask.information", outputList = ['food'])
                                                        return asktype  # „Please specify a foodtype!"

                                                    else:    # "Okay, I search a match for your preferences."
                                                        returnrestos = DialogueAct()
                                                        returnrestos.create("return.restaurant",outputList = [state.resultList, state.retrievedList])
                                                        return returnrestos   # „That's the result list with restos..."

                                            else: # typeList == []
                                                asktype = DialogueAct()
                                                asktype.create("ask.information", outputList = ['food'])
                                                return asktype  # „Please specify a foodtype!"

                                else: # pricerangeList == []
                                    askpricerange = DialogueAct()
                                    askpricerange.create("ask.information", outputList = ['pricerange'])
                                    return askpricerange  # „Please specify a pricerange! It's empty."

                    else: # means: areaList == []
                        askarea = DialogueAct()
                        askarea.create("ask.information", outputList = ['area'])
                        return askarea  # "Please define some area! Slot is empty."

# other intent: request information on a specified restaurant
                elif any("request.information" in str for str in intentList):
                    if specificRestaurantList != []:
                        for specificResto in specificRestaurantList:
                            if specificResto not in valid_restos:                          
                                askspecificresto = DialogueAct()
                                askspecificresto.create("ask.information", outputList = ["specificRestaurant"])
                                return askspecificresto    # "Which restaurant are you interested in?"

                            elif specificResto in valid_restos:
                                returninfos = DialogueAct()
                                returninfos.create("return.information", outputList = [state.resultList, state.retrievedList])
                                return returninfos   # "About this particular restaurant you've chosen, the db says..."

                    else: # slot for specifying the resto the information is supposed to be about is empty?
                        askspecificresto = DialogueAct()
                        askspecificresto.create("ask.information", outputList = ["specificRestaurant"])
                        return askspecificresto  # "you didn't give any particular restaurant"
                      
        else: #intentList == []
            askintent = DialogueAct()
            askintent.create("ask.information", outputList = ['intent'])
            return askintent # "Please give your intent. It's empty"
