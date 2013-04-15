from pymongo import MongoClient, Connection

def connect(db_name):
    """
    Connects to mongo and returns the results database and the connection
    """
    #TODO: get from properties, clean this up
    connection = Connection('ip', port)
    db = connection[db_name]
    db.authenticate("username", "password")
    return db, connection

def disconnect(c):
    """
    Disconnects the given connection
    """
    c.disconnect()
