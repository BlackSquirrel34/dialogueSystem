from datastructures.dialoguestate import DialogueState
from datastructures.dialogueact import DialogueAct
from database.database import Database
import json

with open("./resources/CamRestaurants-rules.json") as file:
    ontology = json.load(file)
ontologyNames = ontology["slotvalues"]["name"]

with open("./resources/ReferenceResolution-Ontology.json") as file:
    references = json.load(file)
mappings = dict(zip(*references.values()))

class SimpleStateUpdater(object):
    
    database = None

    def __init__(self):
        self.database = Database()
        
    def mapReferences(self, references:list, targetRestaurants:list) -> list:
        mappedNames = []
        for referenceTerm in references:

            # case 1: restaurant is directly referenced by its name in the user query -> assign this as name
            if referenceTerm in ontologyNames:
                name = referenceTerm # e.g. referenceTerm = "curry king"
                
            # case 2: restaurant is mentioned by some terms such as "last, first, number three, 10" etc.
            # assumption that user refers to a specific restaurant previously mentioned in a result list
            # --> get the corresponding index for the term from mappings dict and assign retrievedList at this index as name
            else:
                try:
                    index = mappings[referenceTerm] # e.g. mappings["first"] = 0
                    name = targetRestaurants[index] # e.g. state.retrievedList[0] = "curry queen"
                except:
                    continue
                
            mappedNames.append(name)

        return mappedNames
    
    def updateHistory(self, state:DialogueState, inputAction:DialogueAct, systemAction:DialogueAct) -> DialogueState:

        state.historyInput = inputAction
        state.historyOutput = systemAction
        state.resultList = []

        # add names of restaurants from previous output to list of retrieved restaurants, if not already in there
        if systemAction.intent in ["return.restaurant", "return.information"] and systemAction.outputList:
            results = systemAction.outputList[0]
            for restaurant in results:
                if restaurant["name"].lower() not in state.retrievedList:
                    state.retrievedList.append(restaurant["name"].lower())

        # if last output dialogue act was successful (not empty results), reset the state slots to empty lists
        if systemAction.intent in ["return.restaurant", "return.information"] and systemAction.outputList:
            state = state.resetSlots()
        # if no restaurants were found, don't delete all state slots, only those related to return.information
        # reason: user prompted to add other attribute values --> existing ones should remain
        elif systemAction.intent=="return.restaurant":
            state = state.resetSlots(include=["ofInterest", "specificRestaurant"])
        # if no information was found, don't delete all state slots, only those related to return.restaurant
        # reason: user prompted to say a valid restaurant name or number --> attributes of interest should remain
        elif systemAction.intent=="return.information":
            state = state.resetSlots(exclude=["intent", "ofInterest"])

        return state

    def update(self, state:DialogueState, act:DialogueAct) -> DialogueState:

        # only update if new DialogueAct has been recognised
        if (act is not None and (act.intent or act.slots)):
            
            # update intent (current assumption, yet to decide: there can be more than one intent --> list)
            if act.intent:
                state["intent"].extend(act.intent if isinstance(act.intent, list) else [act.intent])
                
            # update slot values (assumption: slots can have more than one value)
            if act.slots:
                for slot, slotvalues in act.slots.items():
                    if slotvalues and isinstance(slotvalues, list): 
                        state[slot].extend([sv for sv in slotvalues if sv not in state[slot]]) 
                        if "Don't care" in state[slot]:
                            state[slot] = ["Don't care"]
            # open issue: deal with negative slot values (things to be excluded from search)

            if state["intent"]:
                intent = state["intent"][-1]

                # query database to get list of restaurants matching user-specified slot value pairs
                if intent == "find.restaurant":
                    # "Don't care" means the constraint does not apply
                    query = {slot: ([] if "Don't care" in value else value) for slot, value in state.items() if slot!="name"}
                    state.resultList = self.database.findRestaurants(query)
                
                # assumption: only request information about restaurants that have been shown to user before or by (exact) name
                elif intent == "request.information" and state["specificRestaurant"]:

                    # map terms used in natural language (e.g. "last") to the corresponding index (e.g. -1) to find them in the retrievedList
                    restaurantNames = self.mapReferences(state["specificRestaurant"], state.retrievedList)

                    # return information for all restaurants retrieved so far if "all" or "every" mentioned in user input
                    if "All" in state["specificRestaurant"]:
                        restaurantNames.extend(state.retrievedList)

                    state["specificRestaurant"] = restaurantNames

                    if restaurantNames:
                        # if no attributes of interest are specified, return all available attributes
                        # e.g. if user only requests "general info" --> return all slots
                        if not state["ofInterest"] or "info" in state["ofInterest"]:
                            state["ofInterest"] = list(state.keys()) + ["description"]

                        # query database with name as only constraint --> returns all information for specified restaurants
                        restaurantInfo = self.database.findRestaurants({"name": restaurantNames})
                        # then filter the result by removing all slots that are not in list of interesting attributes
                        state.resultList = [{slot: value for slot, value in restaurant.items() if slot in state["ofInterest"]+["name"]}
                                            for restaurant in restaurantInfo]

        return state