from django import forms
from django.core.paginator import Paginator
from django.core.servers.basehttp import FileWrapper
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

import tempfile, zipfile
from helpers import *

#TODO: download all, other conditions (<. >, <=, ...), check if logged in
#TODO: db properties + auth, process properties


class SearchFilter(forms.Form):
    key = forms.CharField(required=True)
    value = forms.CharField(required=True)

    def clean_key(self):
        if not self.cleaned_data['key'].strip():
            raise forms.ValidationError('This field is required')
        return self.cleaned_data


def search(request):
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    SearchFormSet = formset_factory(SearchFilter, formset=RequiredFormSet)

    if not request.method == 'POST':
        return response(SearchFormSet(), {}, request)

    el = dict([(k,v) for k,v in request.POST.items() if k.startswith('form-') and v])
    form = SearchFormSet(el)

    if not form.is_valid():
        return response(form, {}, request)

    return response(form, el, request)


def response(filters, el, req):
    query = mkquery(el)
    print "Query: " + query
    ids = retrieve(query)

    # Pagination setup
    current = int(req.POST.get('page', 1))
    count = int(req.POST.get('navCount', 10))

    p = Paginator(ids, count)
    if 'prev' in req.REQUEST:
        current = max(current - 1, 1)
    elif 'next' in req.REQUEST:
        current = min(current + 1, p.num_pages)
    elif 'nav' in req.REQUEST:
        current = int(req.POST.get('navPage', 1))

    try:
        page = p.page(current)
    except:
        page = p.page(1)

    page.object_list = [ jsonhtml(i) for i in page.object_list ]

    c = RequestContext(req, {
        'current': 'CIdb',
        'filters': filters,
        'ids': page,
        'pp': count
    })

    return render_to_response('cidb/search.html', c)


def download(request, oid):
    temp = tempfile.TemporaryFile()
    archive = zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED)

    result = retrieve_from_id(oid)
    archive.writestr(str(oid) + '.txt', result[u'results'])

    archive.close()

    wrapper = FileWrapper(temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment;filename=' + str(oid) + '.zip'
    response['Content-Length'] = temp.tell()
    temp.seek(0)

    return response
