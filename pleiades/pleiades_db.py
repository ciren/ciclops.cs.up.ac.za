import MySQLdb as sql
import pymongo as mongo
import hashlib

def validateUser(request, user, password):
    con = None
    valid = False

    try:
        #insert pleiades database details here
        con = sql.connect('ip', 'user', 
            'password', 'database')
            
        cur = con.cursor()
        cur.execute("select password from users where username = '" + user + "'")

        db_password = cur.fetchone()

	if not db_password:
            valid = False

        else:
            db_password = "".join(db_password) 

            #verify SHA256 hash
            if cmp(db_password, hashlib.sha256(password).hexdigest()) == 0:
                valid = True
            else:
                valid = False
        
    except db.Error, e:
        print e

    finally:
        if con:
            con.close()

    if valid == True:
        return True

    return False

def getUserResultObjects(user):
    connection = mongo.Connection("ip", 27017)
    mongoDB = mongo.database.Database(connection, "database")

    mongoDB.authenticate("user", "password")

    return mongoDB.simulations.find({"owner": user})

