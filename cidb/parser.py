import re, sys

def tokenize(expr):
    tokens = [i for i in re.split(' *([!:()&|]|\w+\$?\w*) *', expr) if i]
    output = []
    ap = False
    for i in tokens:
        if i == ':':
            output[-1] = output[-1] + i
            ap = True
        elif ap:
            output[-1] = output[-1] + i
            ap = False
        else:
            output.append(i)
    return output


def parseQuery(expr):
    tokens = tokenize(expr)
    s = []
    q = []

    prec = {':': 4, '!': 3, '&': 2, '|': 1, '(': 0}
    right = {'!': 1}
    def getprec(op):
        return prec.get(op, -1)

    for token in tokens:
        if ':' in token:
            q.append(token)
        elif token == '(':
            s.append(token)
        elif token == ')':
            while s[-1] != '(':
                t = s.pop()
                q.append(t)
            if s.pop() != '(':
                raise Exception, 'No matching ('
        elif getprec(token) > 0:
            pr = getprec(token)
            if token in right:
                while s and pr < getprec(s[-1]):
                    q.append(s.pop())
            else:
                while s and pr <= getprec(s[-1]):
                   q.append(s.pop())
            s.append(token)
        else:
            raise Exception, 'Unknown token: "%s"' % token

    s.reverse()
    return q + s


def getKeys(keyToSearch, hasNot, collection):
    l = []

    for c in collection.find({ 'term' : keyToSearch }):
        for key in c['keys']:
            if not key in l:
                if not hasNot or (hasNot and (keyToSearch + '.@type') in key):
                    l.append(key)

    return l


def buildQuery(query, collection):
    q = parseQuery(query)
    def parse(s):
        try: return float(s)
        except: return { '$regex' : '^' + str(s).replace('$', '\\$') + '$', '$options' : 'i' }

    def obj(k, v, n):
        return { k : { '$ne' : v } } if n else { k : v }

    s = []
    for i in range(len(q)):
        token = q[i]
        hasNot = i < len(q) - 1 and q[i+1] == '!'

        if ':' in token:
            split = token.split(':')
            key = split[0]
            v = split[1]
            keyList = [ str(k) for k in getKeys(key, hasNot, collection) ]

            if keyList:
                l = [obj(k, parse(v), hasNot) for k in keyList]
                if len(l) == 1:
                    s.append(l[0])
                else:
                    s.append({ '$and' if hasNot else '$or' : l })
            else:
                s.append(obj(key, parse(v), hasNot))
        else:
            if token == '&':
                s.append({'$and' : [s.pop(), s.pop()] })
            elif token == '|':
                s.append({ '$or' : [s.pop(), s.pop()] })

    return s.pop()

