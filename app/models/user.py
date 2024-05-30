import pytz
import json
import logging
from datetime import datetime
from firebase_admin import firestore 
from operator import itemgetter

# A P P L I C A T I O N                          I M P O R T S
# ------------------------------------------------------------
from app.core import setupdb


__author__ = 'liamkenny'

# ------------------------------------------------------------
# / / / / / / / / / / / / / / /  \ \ \ \ \ \ \ \ \ \ \ \ \ \ \
# ============================================================
# U S E R                                            C L A S S
# ============================================================
# \ \ \ \ \ \ \ \ \ \ \ \ \ \ \  / / / / / / / / / / / / / / /
# ------------------------------------------------------------
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


    # S A V E                                  F U N C T I O N
    # --------------------------------------------------------
    def save(self):
        db = setupdb()
        cursor = db.cursor()

        try:
            now = datetime.now(pytz.timezone('Canada/Pacific')).strftime("%Y/%m/%d %H:%M:%S")
            permissions = None
            if self.permissions:
                permissions = '~'.join(self.permissions)
            sql = f"""REPLACE INTO Users (user_id, fname, lname, email, ski, snowboard, stance, region, permissions, updated, photo) 
                    values (
                        '{str(self.id)}', 
                        '{str(self.fname)}', 
                        '{str(self.lname)}', 
                        '{str(self.email)}', 
                        {self.ski}, 
                        {self.snowboard}, 
                        '{self.stance}', 
                        '{str(self.region)}', 
                        '{str(permissions)}', 
                        '{now}', 
                        '{str(self.photo)}'
                    )"""
            logging.info(f"SQL: {sql}")
            cursor.execute(sql)
            db.commit()
            #self.id = cursor.execute("SELECT last_insert_rowid() FROM songs").fetchone()[0]
            
        except Exception as e:
            logging.error("Could not save user:\n{}".format(e))   
            return False

        logging.info("Saved User:\n{} {} ~ {}\nPermissions: {}\nSki: {} Snowboard: ({})\n{}Region: {}"
                    .format(self.fname, self.lname, self.email, ', '.join(self.permissions), self.ski, self.snowboard, self.stance, self.region))
    
        return True


    # G E T   U S E R                          F U N C T I O N
    # --------------------------------------------------------
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
    

    # I S   A D M I N                          F U N C T I O N
    # --------------------------------------------------------
    def is_admin(self):
        if not 'admin' in self.permissions:
            return False
        
        return True

