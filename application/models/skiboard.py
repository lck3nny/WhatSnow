import logging
from operator import itemgetter
from firebase_admin import firestore
from difflib import SequenceMatcher


__author__ = 'liamkenny'

unit_names = {
    'size':         ['size', 'length'],
    'nose_width':   ['nose width', 'tip width'],
    'waist_width':  ['waist width'],
    'tail_width':   ['tail width'],
    'sidecut':      ['sidecut', 'sidecut radius' 'turning radius'],
    'setback':      ['stance setback'],
    'stance width': ['stance width', 'stance range'],
    'profile':      ['bend', 'profile'],
    'flex':         ['flex', 'stiffness'],
    'asym':         ['asym', 'asymetric']
}


# --------------------------------------------------
# Is Duplicate                       F U N C T I O N
# --------------------------------------------------
def is_duplicate(type, brand, model, year):

    # Check firestore for duplicate entries
    db = firestore.client()
    skiboards = db.collection('SkiBoards').where('type', '==', type).where('brand', '==', brand).where('model', '==', model).where('year', '==', year)
    for skiboard in skiboards.stream():
        # ToDo...
        # Return existing skiboard ID???
        return True, skiboard

    return False, None

# --------------------------------------------------
# Get By Item ID                     F U N C T I O N
# --------------------------------------------------
def get_item_by_id(id):
    if not id:
        return False
    
    # Get firestore doc by ID
    db = firestore.client()
    skiboard = db.collection('SkiBoards').document(id).get()
    collection_docs = db.collection('SkiBoards').document(id).collection('Sizes').get()
    collections = []
    if skiboard.exists:
        for doc in collection_docs:
            collections.append(doc.to_dict())
        
        # Sort collections by size parameter
        collections = sorted(collections, key=itemgetter('size'))
        return skiboard, collections

    return False

# --------------------------------------------------
# Extract Params from Text           F U N C T I O N
# --------------------------------------------------
def extract_params_from_text(raw_input):
    # Initialise empty dictionaries
    sizes = 0
    params = {}
    param_units = {}

    # Itterate throguh each row
    for row in raw_input.split('\n'):
        split_row = row.split(" ")

        # Extract name from row
        row_name = " ".join(split_row[:-1])

        # Extract unit from row
        if '(' in str(row):
            units = str(row)[row.find('(') +1:row.find(')')]
        else:
            units = None

        # Extract values from row
        values = split_row[-1].split('\t')[1:]

        # Remove rogue characters
        for x, v in enumerate(values):
            values[x] = v.replace('\r', '')

        # Create dict for params and units
        params[row_name.replace(' ', '_').lower()] = values
        param_units[row_name.replace(' ', '_').lower()] = units

        sizes += 1
        
    return params, param_units, sizes

# --------------------------------------------------
# Format Params                      F U N C T I O N
# --------------------------------------------------
def format_params(unformatted, units):
    formatted_data = {}
    formatted_units = {}

    # Populate formatted dictionaries with given data
    for key in unformatted:
        matched = match_param(key)
        formatted_data[matched] = unformatted[key]
        formatted_units[matched] = units[key]

    return formatted_data, formatted_units


# --------------------------------------------------
# Match Param                        F U N C T I O N
# --------------------------------------------------
def match_param(param):

    # Calculate best similarity score for each unit name
    match_scores = {}
    for unit in unit_names:
        match_scores[unit] = 0
        for option in unit_names[unit]:
            similarity = SequenceMatcher(None, param.replace('_', ' '), option).ratio()
            if similarity > match_scores[unit]:
                match_scores[unit] = similarity
            
    matched = max(match_scores, key=match_scores.get)
    logging.info("Parameter Matching for: {} - best match: {}\n{}".format(param, matched, match_scores))

    return matched

