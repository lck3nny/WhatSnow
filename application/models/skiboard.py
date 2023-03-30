import logging
from datetime import datetime
import pytz
from operator import itemgetter
from firebase_admin import firestore
from difflib import SequenceMatcher


__author__ = 'liamkenny'

unit_names = {
    'size':             ['size', 'length'],
    'nose_width':       ['nose width', 'tip width'],
    'waist_width':      ['waist width'],
    'tail_width':       ['tail width'],
    'sidecut':          ['sidecut', 'sidecut radius', 'turning radius'],
    'effective_edge':   ['effective edge', 'running length'],
    'setback':          ['stance setback'],
    'stance width':     ['stance width', 'stance range'],
    'profile':          ['bend', 'profile'],
    'flex':             ['flex', 'stiffness'],
    'asym':             ['asym', 'asymetric']
}

profile_types = {
    'full_camber': 'url_for_img',
    'hybrid_camber': 'url_for_img',
    'directional_camber': 'url_for_img',
    'flat': 'url_for_img',
    'directional_flat': 'url_for_img',
    'hybrid_rocker': 'url_for_img',
    'full_rocker': 'url_for_img'
}

param_names = ['size', 'nose_width', 'waist_width', 'tail_width', 'sidecut', 'effective_edge', 'setback', 'stance_width']

# --------------------------------------------------
# Is Duplicate                       F U N C T I O N
# --------------------------------------------------
def is_duplicate(category, brand, model, year):

    # Check firestore for duplicate entries
    db = firestore.client()
    skiboards = db.collection('SkiBoards').where('category', '==', category).where('brand', '==', brand).where('model', '==', model).where('year', '==', year)
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
        return skiboard.to_dict(), collections

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
    data_confidence = {}

    # Populate formatted dictionaries with given data
    for key in unformatted:
        matched, confidence = match_param(key)
        if matched not in data_confidence or (matched in data_confidence and confidence > data_confidence[matched]):
            #logging.info("Updating param matching...\nKey: {} - Confidence: {}\nDict: {}".format(matched, confidence, data_confidence))
            data_confidence[matched] = confidence
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
            #logging.info("param: {} - comparedto: {} - score: {}".format(param, option, similarity))
            if similarity > match_scores[unit]:
                match_scores[unit] = similarity
            
    matched = max(match_scores, key=match_scores.get)
    confidence = match_scores[max(match_scores)]
    #logging.info("Parameter Matching for: {} - best match: {}\n{}".format(param, matched, match_scores))

    return matched, confidence

# --------------------------------------------------
# Create SkiBoard                    F U N C T I O N
# --------------------------------------------------
def create(brand, model, year, category):
    if not brand or not model or not year or not category:
        return False

    try:
        db = firestore.client()
        create_time, skiboard = db.collection('SkiBoards').add({
            'brand': brand,
            'model': model,
            'year': year,
            'category': category,
            'created': datetime.now(pytz.timezone('Canada/Pacific')),
            'updated': datetime.now(pytz.timezone('Canada/Pacific'))
        })
    except:
        return False
    
    return skiboard

# --------------------------------------------------
# Update SkiBoard                    F U N C T I O N
# --------------------------------------------------
def update_info(id, update_params={}, sizes={}):
    if not id and (not update_params or not sizes):
        return False
    
    updatable_params = ['category', 'profile', 'flex','asym']

    # Check firestore for duplicate entries
    db = firestore.client()
    doc_ref = db.collection('SkiBoards').document(id)
    skiboard = doc_ref.get()
    # collection_docs = db.collection('SkiBoards').document(id).collection('Sizes').get()
    # collections = []
    if skiboard.exists:
        skiboard = skiboard.to_dict()
        for key in updatable_params:
            skiboard[key] = update_params[key]

        # Update firestore
        doc_ref.update(skiboard)
        for x in range(len(sizes['size'])):
            id = sizes['size'][x]
            size = {}
            for param in sizes:
                if param != 'size':
                    size[param] = sizes[param][x]

            # Add size as collection in firestore
            logging.info("Adding Size to SkiBoard:\n{}".format(size))
            doc_ref.collection('Sizes').document(id).set(size)
        
        # Sort collections by size parameter
        # collections = sorted(collections, key=itemgetter('size'))
        # return skiboard.to_dict(), collections
        return skiboard
    
    return False
