import os.path
import logging
import json
import pytz
from datetime import datetime
from operator import itemgetter
from difflib import SequenceMatcher

from flask import session


# Infrastructure Imports
# --------------------------------------------------
from firebase_admin import firestore
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient

__author__ = 'liamkenny'


class SkiBoard():

    # --------------------------------------------------
    # Get Brands                         F U N C T I O N
    # --------------------------------------------------
    def get_brands():
        db = firestore.client()
        brands = {}
        docs = db.collection('Brands').stream()
        for doc in docs:
            brands[doc.id] = doc.to_dict()
            
        return brands
        
        

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