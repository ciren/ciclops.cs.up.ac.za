from models import Result
from parser import buildQuery
from CiClops_web.mongo import connect, disconnect

from bson.objectid import ObjectId

import os, re
from subprocess import Popen, PIPE


def mkquery(req):
    """
    Creates a search string from the form data
    """
    query = 'measurements:measurementsuite' #all entries have this
    form = [k for k,v in req.items() if re.search(r'^form-.+-key$', k)]
    el = [(req[i], req[i[:i.rfind('-') + 1] + 'value']) for i in form if i[:i.rfind('-') + 1] + 'value' in req ]

    return ' & '.join([query] + [k + ':' + v for k,v in el])


def jsonhtml(j, f=True):
    """
    Creates an indented HTML list from the JSON data from mongo
    """
    out = ''
    if type(j) is dict:
        out += '\n<ul>'

        for o in sorted(j):
            b = '<li rel="disabled">' if not f else '<li>'
            out += b + str(o).capitalize() + jsonhtml(j[o], False) + '</li>'

        out += '</ul>'

    elif type(j) is list:
        for o in sorted(j):
            out += jsonhtml(o, False)

    else:
        out += '<b>: ' + str(j).capitalize() + '</b>'

    return out


def retrieve(query):
    """
    Takes the search string, converts it to a mongo query and returns the results
    """
    def entry(i): 
        return { 
          i[u'_id']: {
            'Results: ' : '<a href="/cidb/download/' + str(i[u'_id']) + '/">Download</a>',
            'Simulation' : i[u'data'] #TODO: add load code
          }
        }

    db, con = connect('results')
    results =  db.entries.find(buildQuery(query, db.tags))
    disconnect(con)

    return [ entry(i) for i in results ]


def retrieve_from_id(oid):
    """
    Gets a single result for a given id
    """
    db, con = connect('results')
    result =  db.entries.find_one( { '_id' : ObjectId(oid) } )
    disconnect(con)

    return result


