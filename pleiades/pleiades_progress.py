from django.conf import settings
import os, os.path
import pleiades_db as pleiades

def getUserCharts(user):
    charts = []

    sims = pleiades.getUserResultObjects(user)
    jobs = []

    for sim in sims:
        inJobs = False
        for job in jobs:
            if cmp(sim['jobName'], job['name']) == 0:
                inJobs = True
                continue

        if inJobs == False:
            completed_path = settings.CICLOPS_RESULTS_DIR + "/" + user + "/" + sim['jobName'] + '/' + sim['outputPath'][:sim['outputPath'].find('/')] + '/'

            if os.path.exists(completed_path):
                completed = len([name for name in os.listdir(completed_path) if os.path.isfile(completed_path + name)])
            else:
                completed = 0

            print completed_path + " : " + str(completed)

            jobs.append({'name': sim['jobName'],
                         'pending': 0,
                         'running': 1,
                         'completed': completed})

        else:
            for job in jobs:
                if cmp(sim['jobName'], job['name']) == 0:
                    job['running'] += 1

    if len(jobs) > 0:
        for job in jobs:
           pending = str(job['pending'])
           running = str(job['running'])
           completed = str(job['completed'])
           pie = {"rows":[{"c":[{"v":"Pending Simulations"},{"f": pending + " Simulations","v":int(pending)}]},
                          {"c":[{"v":"Running Simulations"},{"f": running + " Simulations","v":int(running)}]},
                          {"c":[{"v":"Completed Simulations"},{"f":completed + " Simulations","v":int(completed)}]}],
                  "cols":[{"type":"string","id":"name","label":"name"},
                          {"type":"number","id":"number1__sum","label":"number1__sum"}],
                  "title": str(job['name'])}

           charts.append(pie)

    return charts
