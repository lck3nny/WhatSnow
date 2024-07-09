import os.path
import logging
import json
import pytz
from datetime import datetime
from operator import itemgetter
from difflib import SequenceMatcher

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.core import setupdb, db


# F R A M E W O R K                              I M P O R T S
# ------------------------------------------------------------
from flask import session
from firebase_admin import firestore
#from elasticsearch import Elasticsearch
#from elasticsearch.client import IndicesClient





__author__ = 'liamkenny'

default_size_units = {
    'size':             {'aliases': ['size', 'length'], 'list': False},
    'nose_width':       {'aliases': ['nose width', 'tip width'], 'list': False},
    'waist_width':      {'aliases': ['waist width'], 'list': False},
    'tail_width':       {'aliases': ['tail width'], 'list': False},
    'sidecut':          {'aliases': ['sidecut', 'sidecut radius', 'turning radius'], 'list': False},
    'effective_edge':   {'aliases': ['effective edge', 'running length'], 'list': False},
    'setback':          {'aliases': ['stance setback'], 'list': True},
    'stance width':     {'aliases': ['stance width', 'stance range'], 'list': False},
    'profile':          {'aliases': ['bend', 'profile'], 'list': False},
    'flex':             {'aliases': ['flex', 'stiffness'], 'list': False},
    'asym':             {'aliases': ['asym', 'asymetric'], 'list': False}
}

default_skiboard_units = {
    'brand':            {'aliases': ['brand', 'manufacturer', 'company'], 'list': False},
    'model':            {'aliases': ['model'], 'list': False},
    'year':             {'aliases': ['year'], 'list': False},
    'name':             {'aliases': ['name'], 'list': False},
    'slug':             {'aliases': ['slug'], 'list': False},
    'family':           {'aliases': ['family'], 'list': False},
    'stiffness':        {'aliases': ['stiffness', 'flex'], 'list': False},
    'shape':            {'aliases': ['shape'], 'list': False},
    'flex_profile':     {'aliases': ['flex profile'], 'list': False},
    'camber_profile':   {'aliases': ['camber profile', 'camber'], 'list': False},
    'camber_details':   {'aliases': ['camber details'], 'list': False},
    'core':             {'aliases': ['core'], 'list': False},
    'core_profiling':   {'aliases': ['core profile', 'core profiling'], 'list': False},
    'fibreglass':       {'aliases': ['fibreglass', 'glass'], 'list': False},
    'laminates':        {'aliases': ['laminates'], 'list': False},
    'resin':            {'aliases': ['resin', 'epoxy'], 'list': False},
    'base':             {'aliases': ['base', 'base material'], 'list': False},
    'edges':            {'aliases': ['edges', 'edge material'], 'list': False},
    'edge_tech':        {'aliases': ['edge tech', 'edge technology', 'disrupted sidecut', 'traction tech'], 'list': False},
    'topsheet':         {'aliases': ['topsheet'], 'list': False},
    'sidewall':         {'aliases': ['sidewall'], 'list': False},
    'inserts':          {'aliases': ['inserts', 'insert pattern', 'mounting hardwear', 'mounting pattern'], 'list': False},
    'asym':             {'aliases': ['asym', 'asymetric'], 'list': False},
    'weight':           {'aliases': ['weight'], 'list': False},
    'womens':           {'aliases': ['womens', 'ladies', 'female'], 'list': False},
    'youth':            {'aliases': ['youth', 'kids'], 'list': False}
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


# A D V A N C E D   S E A R C H
# B U I L D   Q U E R Y                        F U N C T I O N   
# ------------------------------------------------------------
# Generates the SQL query for 
# querying using advanced search params
# ------------------------------------------------------------
def build_advanced_search_query(data):
    empty = True
    query = "SELECT SkiBoards.skiboard_id, brand, model, year, name, slug, category, size FROM SkiBoards INNER JOIN Sizes ON SkiBoards.skiboard_id = Sizes.skiboard_id"
    if data['SkiBoards'] or data['Sizes']:
        empty = True
        query += " WHERE"
        # Loop through each table to query (SkiBoards, Sizes)
        for table in data:
            for param in data[table]:
                if data[table][param]['val']:
                    data[table][param]['val'] = validate_param(param, data[table][param])
                    if not data[table][param]['val']:
                        continue

                    # Append 'AND' for additional clauses
                    if not empty:
                        query += " AND "    

                    empty = False
                    # Append list of filters
                    # WHERE camber_profile IN (Full Camber, Hybrid Camber, Directional Camber)
                    if data[table][param]['operator'] == "IN":
                        s = "', '".join(data[table][param]['val'])
                        query += f" {param} {data[table][param]['operator']} ('{s}')"

                    # Append a range of filters
                    # WHERE waist_width BETWEEN 250 AND 260
                    elif data[table][param]['operator'] == "BETWEEN":
                        query += f" {param} {data[table][param]['operator']} {data[table][param]['val'][0]} AND {data[table][param]['val'][-1]}"
                    
                    # Append specific value filters
                    # WHERE model = Deep Thinker
                    else:
                        query += f" {param} {data[table][param]['operator']} '{data[table][param]['val']}'"
                    
                            
        # Example Query String:
        # ....................................................
        # SSELECT SkiBoards.skiboard_id, brand, model, year, name, slug, category, size 
        # FROM SkiBoards INNER JOIN Sizes ON SkiBoards.skiboard_id = Sizes.skiboard_id 
        # WHERE category = 'Splitboard' AND  shape IN ('Directional', 'Directional Twin') AND  waist_width > '255';
        # ....................................................


    if not empty:
        return f"{query};"
    else:
        return ""
    

# V A L I D A T E   Q U E R Y                  F U N C T I O N   
# ------------------------------------------------------------
# Type Check / XSS Check
# ------------------------------------------------------------
def validate_param(key, param):
    try:
        if str(key) in ['year']:
            if isinstance(param['val'], list):
                for i, p in enumerate(param['val']):
                    param['val'][i] = int(p)
                return param['val']

            return int(param['val'])
        elif str(key) in ['stiffness', 'length', 'nose_width', 'waist_width', 'tail_width', 'effective_edge']:
            if isinstance(param['val'], list):
                for i, p in enumerate(param['val']):
                    param['val'][i] = float(p)
                return param['val']
            
            return float(param['val'])
        else:
            if isinstance(param['val'], list):
                for i, p in enumerate(param['val']):
                    param['val'][i] = str(p)
                return param['val']
            
            return str(param['val'])
            
    except Exception as e:
        logging.error(f"Param failed validation: {param} - ERROR - {e}")
        return False
    
    '''
    valid_param_types = {
        'brand': type("Burton"),
        'model': type("Hometown Hero"),
        'year': type(2020),
        'family': type("Family Tree"),
        'stiffness': type(6.0),
        'shape': type("Directional"),
        'flex_profile': type("Directional"),
        'camber_profile': type("Directional Camber"),
        'inserts': type("channel"),
        'category': type("Snowboard"),
        'length': type(160.0),
        'nose_width': type(307.7),
        'waist_width': type(258.0),
        'tail_width': type(295.7),
        'effective_edge': type(1217.0)
    }'''


# M A T C H   P A R A M                        F U N C T I O N
# ------------------------------------------------------------
def match_param(param):
    # Calculate best similarity score for each unit name
    match_scores = {}
    for unit in default_size_units['aliases']:
        match_scores[unit] = 0
        for option in default_size_units['aliases'][unit]:
            similarity = SequenceMatcher(None, param.replace('_', ' '), option).ratio()
            #logging.info("param: {} - comparedto: {} - score: {}".format(param, option, similarity))
            if similarity > match_scores[unit]:
                match_scores[unit] = similarity
            
    matched = max(match_scores, key=match_scores.get)
    confidence = match_scores[max(match_scores)]
    #logging.info("Parameter Matching for: {} - best match: {}\n{}".format(param, matched, match_scores))

    return matched, confidence


# E X T R A C T   R E S U L T S                F U N C T I O N
# ------------------------------------------------------------
# This only works for extracting complete result sets
# is it worth fixing before migrating to SQLAlchemy?
# ------------------------------------------------------------
def extract_results(response):
    results = []
    for r in response:
        logging.info(f"Extracting skiboard from result: \n{r}")
        # Map DB Result to User Object
        try:
            result = SkiBoard(
                skiboard_id=r[0], 
                url=r[1], 
                brand=r[2], 
                model=r[3], 
                year=r[4], 
                category=r[7],
                family=r[8],
                description=r[9],
                stiffness=r[10],
                shape=r[11],
                flex_profile=r[12],
                camber_profile=r[13],
                camber_details=r[14],
                core=r[15],
                core_profiling=r[16],
                fibreglass=r[17],
                laminates=r[18],
                resin=r[19],
                base=r[20],
                edges=r[21],
                edge_tech=r[22],
                topsheet=r[23],
                sidewall=r[24],
                inserts=r[25],
                asym=r[26],
                weight=r[27],
                womens=r[28],
                youth=r[29]
            )

            for key, unit in default_skiboard_units.items():
                if unit['list']:
                    if not result[key] or result[key] != '[]':
                        result[key] = []
                    else:
                        result[key] = result[key].strip('[').strip(']').replace(', ', ',').split(',')
        
                

            logging.info(f"Results: \n{result.__dict__}")
            results.append(result)
        except Exception as e:
            logging.error(f"Unable to extract result from response: {r} / / / {e}")

    return results

# ------------------------------------------------------------
# / / / / / / / / / / / / / / /  \ \ \ \ \ \ \ \ \ \ \ \ \ \ \
# ============================================================
# S K I B O A R D                                    C L A S S
# ============================================================
# \ \ \ \ \ \ \ \ \ \ \ \ \ \ \  / / / / / / / / / / / / / / /
# ------------------------------------------------------------
class SkiBoard():


    # If a SkiBoard has an ID of 0 it has not been saved in the database
    def __init__(self, skiboard_id, brand, model, year, category, family=None, description=None, stiffness=None, shape=None, flex_profile=None, camber_profile=None, camber_details=[], core=None, core_profiling=None, fibreglass=None, laminates=[], resin=None, base=None, edges=None, edge_tech=None, topsheet=None, sidewall=None, inserts=None, asym=False, weight=0, womens=False, youth=False, url=None):
        self.id = skiboard_id
        self.brand = brand
        self.model = model
        self.year = year
        self.name = f"{str(brand).capitalize().replace(' ', '-')} {str(model).capitalize} {str(year)}"
        self.slug = f"{str(brand).lower()}-{str(model).lower()}-{str(year)}"
        self.category = category
        self.description = description
        self.stiffness = stiffness
        self.shape = shape
        self.family = family
        self.flex_profile = flex_profile
        self.camber_profile = camber_profile
        self.camber_details = camber_details
        self.core = core
        self.core_profiling = core_profiling
        self.fibreglass = fibreglass
        self.laminates = laminates
        self.resin = resin
        self.base = base
        self.edges = edges
        self.edge_tech = edge_tech
        self.topsheet = topsheet
        self.sidewall = sidewall
        self.inserts = inserts
        self.asym = asym
        self.weight = weight
        self.womens = womens
        self.youth = youth
        self.url = url

    # I S   D U P L I C A T E                  F U N C T I O N
    # --------------------------------------------------------
    def is_duplicate(self):
        db = setupdb()
        cursor = db.cursor()

        # Search for SkiBoards with 
        try:
            logging.info("Checking for Duplicate SkiBoards: {} {} ({})".format(self.brand, self.model, self.year))
            sql = """SELECT skiboard_id FROM SkiBoards WHERE brand = '{}' AND model = '{}' AND year = '{}'""".format(self.brand, self.model, self.year)
            cursor.execute(sql)
            result = cursor.fetchone()
            logging.info("Duplicate Found: {}".format(result))
        except Exception as e:
            logging.error(e)

        if result:
            return True

        return False

    # G E T   S K I B O A R D                  F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def get(cls, id=None, brand=None, model=None, year=None, slug=None):
        
        db = setupdb()
        cursor = db.cursor()

        if id:
            try:
                logging.info(f"Getting SkiBoard from ID: {id}")
                sql = f"""SELECT * FROM SkiBoards WHERE skiboard_id = '{id}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info(f"Result: {result}")
            except Exception as e:
                logging.error(e)
                return None
            
        elif brand and model and year:
            try:
                logging.info("Getting SkiBoard by B-M-Y: {} {} ({})".format(brand, model, year))
                sql = f"""SELECT * FROM SkiBoards WHERE brand = '{brand}' AND model = '{model}' AND year = '{year}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info(f"Result: {result}")
            except Exception as e:
                logging.error(e)
                return None
        elif slug:
            try:
                sql = f"""SELECT * FROM SkiBoards WHERE slug = '{slug}'"""
                cursor.execute(sql)
                result = cursor.fetchone()
            except Exception as e:
                logging.error(f"Could not get SkiBoard from Slug:\n{e}")
                return None
            
        if not result:
            return None
        
        skiboard = extract_results([result])[0]
        return skiboard


    # S A V E                                  F U N C T I O N
    # --------------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()


        if not self.stiffness:
            self.stiffness = 0

        if not self.weight:
            self.weight = 0

        if self.id and self.id != -1:
            logging.info("Updating existing skiboard")
            sql = f"""REPLACE INTO SkiBoards (skiboard_id, url, brand, model, year, name, slug, category, family, description, stiffness, shape, flex_profile, camber_profile, camber_details, core, core_profiling, fibreglass, laminates, resin, base, edges, edge_tech, topsheet, sidewall, inserts, asym, weight, womens, youth, updated) 
            values(
            '{str(self.id)}',
            '{str(self.url)}', 
            '{str(self.brand)}',  
            '{str(self.model)}', 
            '{str(self.year)}',
            '{str(self.brand)} {str(self.model)} {str(self.year)}',
            '{str(self.brand).lower()}-{str(self.model).lower()}-{str(self.year)}',
            '{str(self.category)}', 
            '{str(self.family)}', 
            '{str(self.description)}', 
            {float(self.stiffness)}, 
            '{str(self.shape)}', 
            '{str(self.flex_profile)}', 
            '{str(self.camber_profile)}',  
            '{str(self.camber_details)}', 
            '{str(self.core)}', 
            '{str(self.core_profiling)}', 
            '{str(self.fibreglass)}', 
            '{str(self.laminates)}', 
            '{str(self.resin)}', 
            '{str(self.base)}', 
            '{str(self.edges)}', 
            '{str(self.edge_tech)}', 
            '{str(self.topsheet)}', 
            '{str(self.sidewall)}', 
            '{str(self.inserts)}', 
            {bool(self.asym)}, 
            {float(self.weight)}, 
            {bool(self.womens)}, 
            {bool(self.youth)}, 
            '{datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")}' )"""
            
        else:
            logging.info("Creating new skiboard")
            sql = f"""INSERT INTO SkiBoards (url, brand, model, year, name, slug, category, family, description, stiffness, shape, flex_profile, camber_profile, camber_details, core, core_profiling, fibreglass, laminates, resin, base, edges, edge_tech, topsheet, sidewall, inserts, asym, weight, womens, youth, updated) 
            values(
            '{str(self.url)}', 
            '{str(self.brand)}',  
            '{str(self.model)}', 
            '{str(self.year)}',
            '{str(self.brand)} {str(self.model)} {str(self.year)}',
            '{str(self.brand).lower()}-{str(self.model).lower()}-{str(self.year)}',
            '{str(self.category)}', 
            '{str(self.family)}', 
            '{str(self.description)}', 
            {float(self.stiffness)}, 
            '{str(self.shape)}', 
            '{str(self.flex_profile)}', 
            '{str(self.camber_profile)}',  
            '{str(self.camber_details)}', 
            '{str(self.core)}', 
            '{str(self.core_profiling)}', 
            '{str(self.fibreglass)}', 
            '{str(self.laminates)}', 
            '{str(self.resin)}', 
            '{str(self.base)}', 
            '{str(self.edges)}', 
            '{str(self.edge_tech)}', 
            '{str(self.topsheet)}', 
            '{str(self.sidewall)}', 
            '{str(self.inserts)}', 
            {bool(self.asym)}, 
            {float(self.weight)}, 
            {bool(self.womens)}, 
            {bool(self.youth)}, 
            '{datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")}' )"""

        
        try:
            logging.info(f"About to execute SQL: {sql}")
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            logging.error(f"Could not save SkiBoard:\n{e}")
            return False

        logging.info(f"Saved SkiBoard:\nBrand: {self.brand}\nModel: {self.model} Year: ({self.year})")

        # ToDo...
        # Update ElasticSearch
        '''
        successes = 0
        logging.info("Uploading SkiBoard to ElasticSearch")
        es.update(
            id=self.id,
            index='SkiBoards',
            document=self.__dict__
        )   
        '''
        

        return True
    
    # S E A R C H                              F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def search_db(cls, query_string):
        
        db = setupdb()
        cursor = db.cursor()

        try:
            #logging.info("Searching for SkiBoard: {}".format(query_string))
            print(f"Searching for SkiBoard: {query_string}")
            sql = f"SELECT * FROM SkiBoards WHERE MATCH(name) AGAINST('{query_string}' IN NATURAL LANGUAGE MODE)"
            # sql = f"SELECT * FROM SkiBoards WHERE MATCH(name) AGAINST('{query_string}' WITH QUERY EXPANSION)"
            cursor.execute(sql)
            response = cursor.fetchall()
            logging.info("Response: {}".format(response))
            print(f"Response: {response}")
        except Exception as e:
            logging.error(e)
            return None
    
        results = extract_results(response)
        return results
    
    # S A V E   S I Z E   V A L U E S          F U N C T I O N
    # --------------------------------------------------------
    def save_values(self, values):
        #print(f"Importing...\n{str(skiboard['brand']).capitalize()} {str(skiboard['model']).capitalize()} {str(skiboard['year'])}\nValues:\n{values}")
        for x in range(len(values['size'])):
            try:
                sql = f"""REPLACE INTO sizes (
                    skiboard_id,
                    size,
                    nose_width,
                    waist_width,
                    tail_width,
                    sidecut,
                    setback,
                    effective_edge
                ) VALUES (
                    '{str(self['id'])}',
                    '{str(values['size'][x])}',
                    '{float(values['nose width'][x])}',
                    '{float(values['waist width'][x])}',
                    '{float(values['tail width'][x])}',
                    '{str(values['sidecut'][x])}',
                    '{float(values['setback'][x])}',
                    '{float(values['effective edge'][x])}'
                )"""

                db = setupdb()
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print(f"ERROR: size ({values['size'][x]})\n{e}\n")
                print(f"SQL:\n{sql}\n\n")
        
        return True
    
    # A D V A N C E D   S E A R C H            F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def advanced_search(cls, params):
        db = setupdb()
        cursor = db.cursor()

        # Build query from provided param in/equalities 
        try:
            query = build_advanced_search_query(params)
            logging.info(f"Advanced Search Query: {query}")
        except Exception as e:
            logging.error(f"Unable to generate SQL query: {e}")

        # Break function if query is empty
        # Query builder will return an empty query if no valid params are passed
        if not query:
            logging.info("Empty query, not executing")
            return [], None

        # Exceute query on database
        try:
            logging.info(f"Exceputing query on Databse: {query}")
            cursor.execute(query)
            response = cursor.fetchall()
        except Exception as e:
            logging.error(f"There was a problem executing query: {e}")

        results = []
        for r in response:
            #logging.info(f"Extracting skiboard from result: \n{r}")
            # Map DB Result to User Object
            try:
                result = SkiBoard(
                    skiboard_id=r[0], 
                    brand=r[1], 
                    model=r[2], 
                    year=r[3], 
                    name=r[4],
                    slug=r[5],
                    category=r[6]
                )
                
                size = r[7]

                #logging.info(f"Results: \n{result.__dict__}")
                results.append({'skiboard': result, 'size': size})
            except Exception as e:
                logging.error(f"Unable to extract result from response: {r}")

        logging.info("Advanced Search Complete")
        return results, query
    
    # C A L C U L A T E
    # C O M P A R I S O N S                    F U N C T I O N
    # --------------------------------------------------------
    def calc_comparisons():
        total_comparisons = 0
        logging.info("Session: {}".format(session))
        if 'compare' in session and session['compare']:
            for key in session['compare']:
                total_comparisons += len(session['compare'][key])

        return "[ {} ]".format(total_comparisons)
    
    # E X T R A C T   P A R A M S
    # F R O M   T E X T                        F U N C T I O N
    # --------------------------------------------------------
    def extract_params_from_text(raw_input):
        # Initialise empty dictionaries
        sizes = 0
        params = {}
        param_units = {}

        logging.info("Extracting params from raw input")

        # Itterate throguh each row
        for row in raw_input.split('\n'):
            split_row = row.split(" ")

            # Extract name from row
            row_name = " ".join(split_row[:-1])

            logging.info("Split row: {}".format(split_row))
            logging.info("Row name: {}".format(row_name))

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


    # F O R M A T   P A R A M S                F U N C T I O N
    # --------------------------------------------------------
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


    # D E S C R I B E                          F U N C T I O N
    # --------------------------------------------------------
    def describe():
        return {'profile_types': profile_types, 'default_size_units': default_size_units['aliases'], 'param_names': param_names}




    # --------------------------------------------------------
    # XX X X X X X X X X X X X X XX X X X X X X X X X X X X XX 

    #      I N C O M P E T E   F U N C T I O N A L I T Y
    #      ---------------------------------------------

    # XX X X X X X X X X X X X X XX X X X X X X X X X X X X XX
    # --------------------------------------------------------



    # Update ElasticSearch                     F U N C T I O N
    # --------------------------------------------------------
    def update_es(id, skiboard, es_index='skiboards'):

        if not skiboard:
            return False

        # Connect to ElasticSearch
        es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))
        idx_manager = IndicesClient(es_client)
        active_index = list(idx_manager.get(es_index).keys())[0]

        # Create or Update document
        if not es_client.exists(index=es_index, id=id):
            return es_client.index(index=active_index, id=id, body=skiboard.__dict__)

        return es_client.update(index=active_index, id=id, document=skiboard)
       
    
    # Search ElasticSearch                     F U N C T I O N
    # --------------------------------------------------------
    @classmethod
    def search_es(query, es_index='skiboards'):
         # Connect to ElasticSearch
        try:
            logging.info(f"ElasticSearch...\nES URL: {es_config['url']}\nBasic Auth: {es_config['key']} - {es_config['secret']}")
            es_client = Elasticsearch([es_config['url']], basic_auth=(es_config['key'], es_config['secret']))

            logging.info(list(es_client.indices.get_alias(index="*"))[0])
            active_index = list(es_client.indices.get_alias(index="*"))[0]
            
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
        except Exception as e:
            logging.error(f"WTF:\n{e}")

        logging.info("Querying elasticsearch index {}: \n{}".format(active_index, search_body))
        resp = es_client.search(index="skiboards-2024-02-21", body={"query": {"match_all": {}}})

        #resp = es_client.search(index='SkiBoards', body={"query": {"match_all": {}}})
        logging.info("ElasticSearch response: {}".format(resp))
        res = []
        try:
            for hit in resp['hits']['hits']:
                skiboard = SkiBoard(
                    skiboard_id = hit['_source']['skiboard_id'], 
                    url = hit['_source']['url'], 
                    brand = hit['_source']['brand'], 
                    model = hit['_source']['model'], 
                    year = hit['_source']['year'], 
                    name = hit['_source']['name'],
                    slug = hit['_source']['slug'],
                    category = hit['_source']['category'],
                    family = hit['_source']['family'],
                    description = hit['_source']['description'],
                    stiffness = hit['_source']['stiffness'],
                    flex_profile = hit['_source']['flex_profile'],
                    camber_profile = hit['_source']['camber_profile'],
                    camber_details = hit['_source']['camber_details'],
                    core = hit['_source']['core'],
                    core_profiling = hit['_source']['core_profile'],
                    fibreglass = hit['_source']['fibreglass'],
                    laminates = hit['_source']['laminates'],
                    resin = hit['_source']['resin'],
                    base = hit['_source']['base'],
                    edge_tech = hit['_source']['edge_tech'],
                    topsheet = hit['_source']['topsheet'],
                    sidewall = hit['_source']['sidewall'],
                    inserts = hit['_source']['inserts'],
                    asym = hit['_source']['asym'],
                    weight = hit['_source']['weight'],
                    womens = hit['_source']['womens'],
                    youth = hit['_source']['youth']
                )

                res.append(skiboard)
        except Exception as e:
            logging.error("Error extracting hits from ElasticSearch: {}".format(e))
            
        logging.info("ElasticSearch:\nQuery: {}\nResponse: {}".format(query, res))
        
        return res

    


    
