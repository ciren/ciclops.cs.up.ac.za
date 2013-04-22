from django.core.servers.basehttp import FileWrapper
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django import forms
import os, tempfile, zipfile, glob, subprocess, time, urllib
import pleiades_db as pleiades
import pleiades_progress as charts
import pleiades_settings

class ViewAsForm(forms.Form):
    view_as = forms.CharField(max_length=100, required=False)

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

    user_jobs = getUserJobs(view_as)
    #user_charts = charts.getUserCharts(view_as)
    
    template = loader.get_template('pleiades/progress.html')

    c = RequestContext(request, {
        'current': 'Pleiades',
        'username': request.session['username'],
	'view_as': view_as,
        'jobs': user_jobs,
        'form': form,
        'is_admin': request.session['is_admin'],
    })

    return HttpResponse(template.render(c))

def getUserJobs(view_as):
    sims = pleiades.getUserResultObjects(view_as)
    simulations = pleiades.getUserSimulations(view_as)
    jobs = []

    for sim in sims:
	print "here"
        inJobs = False
        for job in jobs:
            if cmp(sim['jobName'], job['name']) == 0:
		print "here too"
                inJobs = True
                continue

	if inJobs == False:
	    completed_path = settings.CICLOPS_RESULTS_DIR + "/" + view_as + "/" + sim['jobName'] + '/' + sim['outputPath'][:sim['outputPath'].rfind('/')] + '/'

	    if os.path.exists(completed_path):
		completed = len([name for name in os.listdir(completed_path) if os.path.isfile(completed_path + name)])
	    else:
		completed = 0

	    new_job = {'name': sim['jobName'],
		    'id': sim['id'],
		    'incomplete': 0,
		    'completed': completed,
		    'progress': 4}

	    for s in simulations:
		if cmp(s['jobName'], new_job['name']) == 0:
		    if  s['unfinishedTasks'] == s['samples']:
			new_job['incomplete'] += 1

	    new_job['incomplete'] += pleiades.getRunningSimulationsCount(new_job['id'])

	    complete = int(new_job['completed'])
	    total = int(new_job['incomplete']) + complete
	    if total == 0:
		progress = 666
	    else:
	    	progress = round(100 * float(complete) / float(total), 1)

	    new_job['progress'] = progress

	    jobs.append(new_job)

    return sorted(jobs, key=lambda x:x['name'].lower())
    

def chart(request, view_as, jobName):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    charts = []

    results = pleiades.getUserResultObjects(view_as)
    simulations = pleiades.getUserSimulations(view_as)
    jobs = []

    for sim in results:
        inJobs = False
	if cmp(sim['jobName'], jobName) == 0:
		for job in jobs:
		    if cmp(sim['jobName'], job['name']) == 0:
		        inJobs = True
		        continue

		if inJobs == False:
		    completed_path = settings.CICLOPS_RESULTS_DIR + "/" + view_as + "/" + sim['jobName'] + '/' + sim['outputPath'][:sim['outputPath'].rfind('/')] + '/'

		    if os.path.exists(completed_path):
		        completed = len([name for name in os.listdir(completed_path) if os.path.isfile(completed_path + name)])
		    else:
		        completed = 0

		    new_job = {'name': sim['jobName'],
				 'id': sim['id'],
		                 'pending': 0,
		                 'running': 0,
		                 'completed': completed}

		    for s in simulations:
			if cmp(s['jobName'], new_job['name']) == 0:
			    if  s['unfinishedTasks'] == s['samples']:
				new_job['pending'] += 1

		    new_job['running'] = pleiades.getRunningSimulationsCount(new_job['id'])

		    jobs.append(new_job)

    if len(jobs) > 0:
        for job in jobs:
           pending = str(job['pending'])
           running = str(job['running'])
           completed = str(job['completed'])
           pie = {"rows":[{"c":[{"v":"Completed Simulations"},{"f":completed + " Simulations","v":int(completed)}]},
                          {"c":[{"v":"Running Simulations"},{"f": running + " Simulations","v":int(running)}]},
                          {"c":[{"v":"Pending Simulations"},{"f": pending + " Simulations","v":int(pending)}]}],
                  "cols":[{"type":"string","id":"name","label":"name"},
                          {"type":"number","id":"number1__sum","label":"number1__sum"}],
                  "title": str(job['name'])}

           charts.append(pie)

    template = loader.get_template('pleiades/chart.html')

    c = RequestContext(request, {
        'charts': charts,
	'id': jobName
    })

    return HttpResponse(template.render(c))

def samples(request, view_as, jobName):
    if not 'username' in request.session:
        return HttpResponseRedirect('/pleiades/login/')
    else:
        user = request.session['username']

    charts = []
    rows = []

    results = pleiades.getUserResultObjects(view_as)
    completed_path = ""

    for sim in results:
	if cmp(sim['jobName'], jobName) == 0:
	    completed_path = settings.CICLOPS_RESULTS_DIR + "/" + view_as + "/" + sim['jobName'] + '/' + sim['outputPath']

	    sid = sim['id']
	    name = sim['outputFileName']
	    completed = len(sim['results'])
	    running = pleiades.getRunningSamplesCount(sid)
	    pending = sim['samples'] - (completed + running)
	    completed = str(round(float(completed) / (float(pending) + float(running) + float(completed)) * 100, 1)) + "%"

	    rows.append({"c":[{"v":str(name)},{"v":pending},{"v":running},{"v":completed}]})

    completed_path = completed_path[:completed_path.rfind('/')] + '/'
    
    if os.path.exists(completed_path):
        for name in os.listdir(completed_path):
	    rows.append({"c":[{"v":str(name)},{"v":0},{"v":0},{"v":"100%"}]})

    table = {"rows":rows,
              "cols":[{"type":"string","id":"name","label":"File Name"},
                      {"type":"string","id":"pending","label":"Pending Samples"},
	              {"type":"string","id":"running","label":"Running Samples"},
	              {"type":"string","id":"progress","label":"Completed Samples"}]
            }

    charts.append(table)

    template = loader.get_template('pleiades/table.html')

    c = RequestContext(request, {
        'charts': charts,
	'id': jobName
    })

    return HttpResponse(template.render(c))
