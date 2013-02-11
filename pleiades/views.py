from django.core.servers.basehttp import FileWrapper
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django import forms
import os, tempfile, zipfile, glob, subprocess, time, urllib
import pleiades_db as pleiades
import pleiades_progress as charts
import pleiades_settings

JAR_CHOICES = (('Default', 'Default Jar File (' + pleiades_settings.cilib_snapshot_version + ')'), ('Custom','Custom Jar File'))

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class UploadForm(forms.Form):
    job_name = forms.CharField(max_length=100, required=True)
    input_file = forms.FileField(required=True)
    jar_options = forms.ChoiceField(widget=forms.RadioSelect(attrs={'onclick':'if (this.value == "Default"){document.getElementById("id_custom_jar_file").disabled=1} else {document.getElementById("id_custom_jar_file").disabled=0}'}),
                                    choices=JAR_CHOICES, required=True)
    custom_jar_file = forms.FileField(required=False)

    def clean_custom_jar_file(self):
       data = self.cleaned_data['custom_jar_file']

       if not 'jar_options' in self.cleaned_data:
           return data

       option = self.cleaned_data['jar_options']

       if option == 'Custom' and data == None:
          raise forms.ValidationError('Please specify a custom jar file or select one of the provided jar files.')

       return data

class ViewAsForm(forms.Form):
    view_as = forms.CharField(max_length=100, required=False)

def index(request):
    if 'username' in request.session:
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

    header = "Log In"

    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if pleiades.validateUser(request, user, password) == True:
                request.session['username'] = user
                request.session.set_expiry(86400)

                if pleiades.is_admin(request, user) == 1:
                    request.session['is_admin'] = True
                else:
                    request.session['is_admin'] = False

                return HttpResponseRedirect("/pleiades/")
            else:
                header = "Invalid Username or Password"

    else:
        form = LoginForm()   

    template = loader.get_template('pleiades/form.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'form': form,
        'submit': 'Login',
        'header': header,
        'action': '/pleiades/login/',
        'username': '',
    })

    return HttpResponse(template.render(c))

def logout(request):
    if 'username' in request.session:
        del request.session['username']
        
    return HttpResponseRedirect('/pleiades/')

def upload(request):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    header = 'Upload Job'

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            jar_option = form.cleaned_data['jar_options']

            upload_path = settings.USER_DIRS + '/' + user + '_uploads'
    
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
    
            input_path = upload_path + '/' + form.cleaned_data['job_name'] + '.xml'
            jar_path = upload_path + '/' + form.cleaned_data['job_name'] + '.jar'
    
            handle_uploaded_file(request.FILES['input_file'], input_path)

            if jar_option == 'Custom':
                handle_uploaded_file(request.FILES['custom_jar_file'], jar_path)
            elif jar_option == 'Default':
                urllib.urlretrieve(pleiades_settings.cilib_snapshot_url, jar_path)
    
            output = subprocess.Popen(['java', '-jar', './Pleiades-0.1.jar', '-u', user, '-i', input_path, '-j', jar_path], stdout=subprocess.PIPE).communicate()[0];
            output = output.replace(">", "<br/>")
    
            clean_upload_dir(upload_path)
            return upload_output(request, output)
    else:
        form = UploadForm()    
    
    template = loader.get_template('pleiades/form.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'form': form,
        'submit': 'Upload Job',
        'header': header,
        'action': '/pleiades/upload/',
    })

    return HttpResponse(template.render(c))

def clean_upload_dir(path):
    for f in os.listdir(path):
        os.remove(path + '/' + f)

def upload_output(request, output):
    template = loader.get_template('pleiades/output.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'output': output,
        'header': 'Upload Complete',
    })

    return HttpResponse(template.render(c))

def handle_uploaded_file(f, name):
    print "writing file"
    with open(name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    print "done"

def progress(request):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    view_as = user

    if request.method == 'POST':
        form = ViewAsForm(request.POST)
        
        if form.is_valid():
            view_as = form.cleaned_data['view_as']
        
    else:
        form = ViewAsForm()

    user_charts = charts.getUserCharts(view_as)
    
    template = loader.get_template('pleiades/progress.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'username': request.session['username'],
        'charts': user_charts,
        'form': form,
        'is_admin': request.session['is_admin'],
    })
    return HttpResponse(template.render(c))

def results(request, path):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user_dir = (path + '/')[1:(path + '/')[1:].find('/') + 1]
        user = request.session['username']

        if (cmp(path, "") == 0) or not (cmp(user_dir, user) == 0):
            return HttpResponseRedirect('/pleiades/results/' + user)

    template = loader.get_template('pleiades/results.html')
    css = settings.MEDIA_ROOT
    dirs = []
    files = []
    current_path = settings.CICLOPS_RESULTS_DIR + path
    current_path = os.path.join(current_path, '*')

    for current_file in glob.glob(current_path):
        if os.path.isdir(current_file):
            dirs.append(current_file[current_file.rfind('/') + 1:])
        else:
            files.append(current_file[current_file.rfind('/') + 1:])

    c = RequestContext(request, {
        'current': 'Pleiades',
        'dirs': dirs,
        'files': files,
        'path': path,
        'back': path[:path.rfind('/')],
        'current_dir': path[path.rfind('/'):],
        'css': css,
        'username': user
    })

    return HttpResponse(template.render(c))

def download_results(request, path):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')

    else:
        user_dir = (path + '/')[1:(path + '/')[1:].find('/') + 1]
        user = request.session['username']

        if (cmp(path, "") == 0) or not (cmp(user_dir, user) == 0):
            return HttpResponseRedirect('/pleiades/results/' + user)

    """                                                                         
    Create a ZIP file on disk and transmit it in chunks of 8KB,                 
    without loading the whole file into memory. A similar approach can          
    be used for large dynamic PDF files.                                        
    """

    files = []
    current_path = settings.CICLOPS_RESULTS_DIR + path
    current_path = os.path.join(current_path, '*')
    
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)
    
    for current_file in glob.glob(current_path):
        if os.path.isfile(current_file):
            archive.write(current_file, current_file[current_file.rfind('/') + 1:])

    archive.close()

    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')

    response['Content-Disposition'] = 'attachment; filename=' + path[path.rfind('/') + 1:] + '.zip'
    response['Content-Length'] = temp.tell()
    temp.seek(0)
    
    return response

