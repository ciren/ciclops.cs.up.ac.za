import MySQLdb as sql
import pymongo as mongo
import hashlib, re

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
        
    except sql.Error, e:
        print e

    finally:
        if con:
            con.close()

    if valid == True:
        return True

    return False

def is_admin(request, user):
    con = None

    try:
        #insert pleiades database details here
        con = sql.connect('ip', 'user', 
            'password', 'database')
            
        cur = con.cursor()
        cur.execute("select admin from users where username = '" + user + "'")

        admin = cur.fetchone()

        admin = admin[0]

	if not admin:
            admin = 0

    except sql.Error, e:
        print e

    finally:
        if con:
            con.close()

    if admin == 1:
        return True

    return False

def getUserResultObjects(user):
    connection = mongo.Connection("ip", 27017)
    mongoDB = mongo.database.Database(connection, "Pleiades")

    mongoDB.authenticate("user", "password")

    return mongoDB.results.find({"owner": user})

def getUserSimulations(user):
    connection = mongo.Connection("ip", 27017)
    mongoDB = mongo.database.Database(connection, "Pleiades")

    mongoDB.authenticate("user", "password")

    if mongoDB.jobs.find({"owner": user}).count() > 0:
	user_entry = mongoDB.jobs.find_one({"owner": user})
	return user_entry['simulations']
    else:
	return []

def getRunningSimulationsCount(simulationID):
    connection = mongo.Connection("ip", 27017)
    mongoDB = mongo.database.Database(connection, "Pleiades")

    mongoDB.authenticate("user", "password")

    jobID = simulationID[:simulationID.rfind("_")]
    regex = jobID + ".*"

    running_samples = mongoDB.running.find({"task_id": re.compile(regex, re.IGNORECASE)})
    running_sims = []
    
    for sample in running_samples:
	sim_id = sample["task_id"][:sample["task_id"].rfind("_")]
	if not sim_id in running_sims:
	    running_sims.append(sim_id)

    return len(running_sims)

def getRunningSamplesCount(simulationID):
    connection = mongo.Connection("ip", 27017)
    mongoDB = mongo.database.Database(connection, "Pleiades")

    mongoDB.authenticate("user", "password")

    regex = simulationID + ".*"

    print regex

    running_samples = mongoDB.running.find({"task_id": re.compile(regex, re.IGNORECASE)}).count()

    return running_samples

def getAllUsers():
    con = None

    try:
        #insert pleiades database details here
        con = sql.connect('ip', 'user', 
            'password', 'database')
            
        cur = con.cursor()
        cur.execute("select * from users")

        users = cur.fetchall()

    except sql.Error, e:
        print e

    finally:
        if con:
            con.close()

    return users

