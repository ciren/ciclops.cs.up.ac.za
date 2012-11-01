from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django import forms
import os, glob, hashlib
import MySQLdb as db

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

def validateUser(request, user, password):
    print 'connecting'
    con = None
    valid = False

    try:
        #insert database details here
        con = db.connect('', '', 
            '', '')
            
        cur = con.cursor()
        cur.execute("select password from users where username = '" + user + "'")

        db_password = cur.fetchone()

	if not db_password:
            print "no such user"
            valid = False

        else:
            db_password = "".join(db_password) 
        
            print "db: " + db_password
            print "pass: " + password
            print "hash: " + hashlib.sha256(password).hexdigest()
            #verify SHA256 hash
            if cmp(db_password, hashlib.sha256(password).hexdigest()) == 0:
                print "true"
                valid = True
            else:
                print "not true"
                valid = False
        
    except db.Error, e:
        print e

    finally:
        if con:
            con.close()

    if valid == True:
        print "returning true"
        return True

    print "returning false"
    return False

def index(request):
    if 'username' in request.session:
        print "here"
        user = request.session['username']
    else:
        user = ''

    template = loader.get_template('pleiades/index.html')
    c = RequestContext(request, {
        'current': 'Pleiades',
        'username': user,
    })
    return HttpResponse(template.render(c))

def login(request):
    if 'username' in request.session:
        return HttpResponseRedirect('/pleiades/')

    if request.method == 'POST': # If the form has been submitted...
        form = LoginForm(request.POST) # A form bound to the POST data
        
        if form.is_valid(): # All validation rules pass
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if validateUser(request, user, password) == True:
                request.session['username'] = user
                request.session.set_expiry(300)
                return HttpResponseRedirect('/pleiades/')

    form = LoginForm() # An unbound form    
    template = loader.get_template('pleiades/login.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'form': form,
        'username': '',
    })

    return HttpResponse(template.render(c))

def logout(request):
    if 'username' in request.session:
        del request.session['username']
        
    return HttpResponseRedirect('/pleiades/')

def upload(request):
    template = loader.get_template('pleiades/upload.html')
    c = RequestContext(request, {
        'current': 'Pleiades',
        'username': request.session['username']
    })
    return HttpResponse(template.render(c))

def results(request, path):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    template = loader.get_template('pleiades/results.html')
    css = settings.MEDIA_ROOT
    dirs = []
    files = []
    current_path = settings.CICLOPS_RESULTS_DIR + user + path

    print(path)

    for current_file in glob.glob(os.path.join(current_path, '*')):
        if os.path.isdir(current_file):
            dirs.append(current_file[current_file.rfind('/') + 1:])
        else:
            files.append(current_file[current_file.rfind('/') + 1:])

    c = RequestContext(request, {
        'dirs': dirs,
        'files': files,
        'path': path,
        'back': path[:path.rfind('/')],
        'current_dir': path[path.rfind('/'):],
        'css': css,
        'username': user
    })

    return HttpResponse(template.render(c))

