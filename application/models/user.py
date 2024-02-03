import pytz
import json
import logging
from datetime import datetime
from firebase_admin import firestore 
from operator import itemgetter

from application.core import setupdb


__author__ = 'liamkenny'

# ==================================================
# U S E R                                  C L A S S
# ==================================================
class User():

    # If a User has an ID of 0 it has not been saved in the database
    def __init__(self, userid, fname, lname, email, ski=0, snowboard=0, stance=None, permissions=[], region=None, photo=None):
        self.id = userid
        self.fname = fname
        self.lname = lname
        self.email = email
        self.ski = ski
        self.snowboard = snowboard
        self.stance = stance
        self.permissions = permissions
        self.region = region
        self.photo = photo


    # --------------------------------------------------
    # Save User                          F U N C T I O N
    # --------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()

        try:
            sql = """REPLACE INTO 'Users' (user_id, fname, lname, email, ski, snowboard, stance, region, permissions, created, updated, photo)
                values ({}, {}, {}, {}, {}, {}, {}, {}))
            """.format(self.id, self.fname, self.lname, self.email, 
                    self.ski, self.snowboard, self.stance, self.region, '~'.join(self.permissions), 
                    datetime.now(pytz.timezone('Canada/Pacific')), datetime.now(pytz.timezone('Canada/Pacific')),
                    self.photo)
            cursor.execute(sql)
            db.commit()
            #self.id = cursor.execute("SELECT last_insert_rowid() FROM songs").fetchone()[0]
            
        except Exception as e:
            logging.error("Could not save user:\n{}".format(e))   
            return False

        logging.info("Saved User:\n{} {} ~ {}\nPermissions: {}\nSki: {} Snowboard: ({})\n{}Region: {}"
                    .format(self.fname, self.lname, self.email, ', '.join(self.permissions), self.ski, self.snowboard, self.stance, self.region))
    
        return True


    # --------------------------------------------------
    # Get User                           F U N C T I O N
    # --------------------------------------------------
    @classmethod
    def get(cls, id=None, email=None):

        db = setupdb()
        cursor = db.cursor()

        # Get user by ID
        if id:
            try:
                logging.info("Getting user from ID: {}".format(id))
                sql = """SELECT * FROM Users WHERE user_id = '{}'""".format(id)
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))
            
            except Exception as e:
                logging.error(e)
                return None

        # Get user by email
        elif email:
            try:
                logging.info("Getting user from EMAIL: {}".format(email))
                sql = """SELECT * FROM Users WHERE email = '{}'""".format(email)
                cursor.execute(sql)
                result = cursor.fetchone()
                logging.info("Result: {}".format(result))

            except Exception as e:
                logging.error(e)
                return None

        if not result:
            logging.error("No User Found")
            return None
        
        # Map DB Result to User Object
        user = User(
            userid=result[0], 
            fname=result[1], 
            lname=result[2], 
            email=result[3], 
            ski=result[4], 
            snowboard=result[5],
            stance=result[6],
            region=result[7],
            permissions=result[8],
            photo=result[9],
        )
        
        if user.permissions:
            user.permissions = user.permissions.split('~')
        else:
            user.permissions = []

        return user
    

    # --------------------------------------------------
    # Is Admin User                      F U N C T I O N
    # --------------------------------------------------
    def is_admin(self):
        if not 'admin' in self.permissions:
            return False
        
        return True
        
    # madeit


