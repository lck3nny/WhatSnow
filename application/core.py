import json
import logging
import pymysql


# Database Setup
# --------------------------------------------------
def setupdb():
    f = open('./config/localdb_config.json')
    dbconfig = json.loads(f.read())
    db = pymysql.connect(host=dbconfig['localhost'], user=dbconfig['username'], password=dbconfig['password'], database=dbconfig['database'])
    f.close()
    return db
