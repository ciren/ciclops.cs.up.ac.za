from django.template import Context, loader
from django.http import HttpResponse
from django.conf import settings
import os, glob

def index(request):
    template = loader.get_template('index.html')
    c = Context({
        "current": "CiClops",
    })
    return HttpResponse(template.render(c))

