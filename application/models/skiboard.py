import os.path
import logging
import json
import pytz
from datetime import datetime
from operator import itemgetter
from difflib import SequenceMatcher

# Infrastructure Imports
# --------------------------------------------------
from firebase_admin import firestore
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient



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

# Connect ElasticSearch credentials
f = open(os.path.dirname(__file__) + '/../config/bonsai_config.json')
es_config = json.load(f)

# --------------------------------------------------
# Slugify                            F U N C T I O N
# --------------------------------------------------
def slugify(strings):
    return '-'.join(strings).lower()

# --------------------------------------------------
# Nameify                            F U N C T I O N
# --------------------------------------------------
def nameify(strings):
    for s in strings:
        try:
            s = normaise_brand_model(s)
        except:
            continue

    return ' '.join(strings)

# --------------------------------------------------
# Is Duplicate                       F U N C T I O N
# --------------------------------------------------
def is_duplicate(category, brand, model, year):

    slug = slugify([brand, model, str(year)])

    # Check firestore for duplicate entries
    db = firestore.client()
    # skiboards = db.collection('SkiBoards').where('category', '==', category).where('brand', '==', brand).where('model', '==', model).where('year', '==', year)
    skiboards = db.collection('SkiBoards').where('slug', '==', slug)
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
            size = doc.id
            size_details = doc.to_dict()
            size_details['size'] = size
            collections.append(size_details)
        
        # Sort collections by size parameter
        collections = sorted(collections, key=itemgetter('size'))
        return skiboard.to_dict(), collections

    return False

# --------------------------------------------------
# Get By Item Slug                   F U N C T I O N
# --------------------------------------------------
def get_item_by_slug(slug):
    if not slug:
        return None, None
    
    # Get firestore doc by slug
    db = firestore.client()
    skiboard = None
    skiboard_id = None
    skiboards = db.collection('SkiBoards').where('slug', '==', slug)
    for doc in skiboards.stream():
        skiboard_id = doc.id
        skiboard = doc
        break

    if not skiboard or not skiboard_id:
        return None, None

    collection_docs = db.collection('SkiBoards').document(skiboard_id).collection('Sizes').get()
    collections = []
    if skiboard.exists:
        for doc in collection_docs:
            size = doc.id
            size_details = doc.to_dict()
            size_details['size'] = size
            collections.append(size_details)
        
        # Sort collections by size parameter
        collections = sorted(collections, key=itemgetter('size'))
        return skiboard.to_dict(), collections

    return None, None

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
def create(brand, model, year, category, author=None):
    if not brand or not model or not year or not category:
        return False, None

    try:
        db = firestore.client()
        create_time, skiboard = db.collection('SkiBoards').add({
            'brand': brand,
            'model': model,
            'year': year,
            'category': category,
            'created': datetime.now(pytz.timezone('Canada/Pacific')),
            'updated': datetime.now(pytz.timezone('Canada/Pacific')),
            'author': author,
            'slug': slugify([brand, model, str(year)]),
            'name': nameify([brand, model, str(year)])
        })
    except Exception as e:
        logging.error("Could not create SKiBoard:\n{}".format(e))
        return False, None
    
    return True, skiboard

# --------------------------------------------------
# Update SkiBoard                    F U N C T I O N
# --------------------------------------------------
def update_info(id, update_params={}, size_params={}):
    if not id and (not update_params or not size_params):
        return False, None, None
    
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
        skiboard['updated'] = datetime.now(pytz.timezone('Canada/Pacific'))

        # Update firestore
        doc_ref.update(skiboard)
        sizes = []
        for x in range(len(size_params['size'])):
            size_id = size_params['size'][x]
            size = {}
            for param in size_params:
                if param != 'size':
                    size[param] = size_params[param][x]

            # Add size as collection in firestore
            logging.info("Adding Size to SkiBoard:\n{}".format(size))
            doc_ref.collection('Sizes').document(size_id).set(size)
            size['size'] = size_id
            sizes.append(size)
        
        # Update ElasticSearch with skiboard object
        skiboard['sizes'] = sizes
        resp = update_es(id, skiboard)

        return True, resp, skiboard
    
    return False, None, None

# --------------------------------------------------
# Normalise Brand / Model Names      F U N C T I O N
# --------------------------------------------------
def normaise_brand_model(s):
    normalised = ''
    s_split = s.split(' ')
    for word in s_split:
        if len(word) > 1:
            normalised += word[0].upper() + word[1:] + ''
        else:
            normalised += word.upper() + ''
    
    return normalised.strip()



# --------------------------------------------------
# Update ElasticSearch               F U N C T I O N
# --------------------------------------------------
def update_es(id, skiboard, es_index='skiboards'):

    if not skiboard:
        return False

    # Connect to ElasticSearch
    es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))
    idx_manager = IndicesClient(es_client)
    active_index = list(idx_manager.get(es_index).keys())[0]

    # Create or Update document
    if not es_client.exists(index=es_index, id=id):
        return es_client.index(index=active_index, id=id, body=skiboard)

    return es_client.update(index=active_index, id=id, document=skiboard)


# --------------------------------------------------
# Search                             F U N C T I O N
# --------------------------------------------------
def search(query, es_index='skiboards'):
    
    # Connect to ElasticSearch
    es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))
    idx_manager = IndicesClient(es_client)
    active_index = list(idx_manager.get(es_index).keys())[0]

    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "name",
                    "brand",
                    "model"
                ]
            }
        }
    }
    resp = es_client.search(index=active_index, body=search_body)
    res = []
    for hit in resp['hits']['hits']:
        res.append({
            'id': hit['_source']['id'],
            'brand': hit['_source']['brand'],
            'model': hit['_source']['model'],
            'year': hit['_source']['year'],
            'slug': hit['_source']['slug']
        })
        
    logging.info("ElasticSearch:\nQuery: {}\nResponse: {}".format(query, res))

    return res

