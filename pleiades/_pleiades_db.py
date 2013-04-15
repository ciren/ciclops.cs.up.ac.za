import MySQLdb as sql
import hashlib, re

from CiClops_web.mongo import connect, disconnect

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
    mongoDB, connection = connect("Pleiades")
    result = mongoDB.results.find({"owner": user})
    disconnect(connection)

    return result

def getUserSimulations(user):
    mongoDB, connection = connect("Pleiades")

    if mongoDB.jobs.find({"owner": user}).count() > 0:
        user_entry = mongoDB.jobs.find_one({"owner": user})
        result = user_entry['simulations']
    else:
        result = []

    disconnect(connection)

def getRunningSimulationsCount(simulationID):
    mongoDB, connection = connect("Pleiades")

    jobID = simulationID[:simulationID.rfind("_")]
    regex = jobID + ".*"

    running_samples = mongoDB.running.find({"task_id": re.compile(regex, re.IGNORECASE)})
    running_sims = []

    for sample in running_samples:
        sim_id = sample["task_id"][:sample["task_id"].rfind("_")]
        if not sim_id in running_sims:
            running_sims.append(sim_id)

    disconnect(connection)

    return len(running_sims)

def getRunningSamplesCount(simulationID):
    mongoDB, connection = connect("Pleiades")

    regex = simulationID + ".*"

    print regex

    running_samples = mongoDB.running.find({"task_id": re.compile(regex, re.IGNORECASE)}).count()

    disconnect(connection)

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

