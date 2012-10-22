from django.template import Context, loader
from django.http import HttpResponse
from django.conf import settings
import os, glob

def index(request):
    template = loader.get_template('pleiades/index.html')
    c = Context({
        'current': 'Pleiades',
    })
    return HttpResponse(template.render(c))

def login(request):
    template = loader.get_template('pleiades/login.html')
    c = Context({
        'current': 'Pleiades',
    })
    return HttpResponse(template.render(c))

def upload(request):
    template = loader.get_template('pleiades/upload.html')
    c = Context({
        'current': 'Pleiades',
    })
    return HttpResponse(template.render(c))

def user(request, name):
    return HttpResponse("This is " + name + "'s page! :)")

def results(request, name, path):
    template = loader.get_template('pleiades/results.html')
    css = settings.MEDIA_ROOT
    dirs = []
    files = []
    current_path = settings.CICLOPS_RESULTS_DIR + name + path

    print(path)

    for current_file in glob.glob(os.path.join(current_path, '*')):
        if os.path.isdir(current_file):
            dirs.append(current_file[current_file.rfind('/') + 1:])
        else:
            files.append(current_file[current_file.rfind('/') + 1:])

    c = Context({
        'dirs': dirs,
        'files': files,
        'user': name,
        'path': path,
        'back': path[:path.rfind('/')],
        'current_dir': path[path.rfind('/'):],
        'css': css,
    })

    return HttpResponse(template.render(c))

