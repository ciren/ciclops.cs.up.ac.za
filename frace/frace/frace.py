import os.path
import time
import shutil
import copy
import glob

from  itertools import product, groupby

from numpy import array

import scipy
from scipy.stats import chi2, t
from scipy.stats.mstats import rankdata

from xml_runner import *
from utils import *
from parameters import *

# Helper classes to hold settings: maybe only need one class?
class IFraceSettings(object):
    def __init__(self, is_iterative=False, interval=10, regenerator=regen_minmax_sobol(100)):
        self.is_iterative = is_iterative
        self.interval = interval
        self.regenerator = regenerator


class FRaceSettings(object):
    def __init__(self, generator, min_probs=1, min_solutions=2, alpha=0.05, iterations=100):
        self.min_probs = min_probs
        self.min_solutions = min_solutions
        self.alpha = alpha
        self.iterations = iterations
        self.generator = generator


class SimulationSettings(object):
    def __init__(self, algorithm, problems, measure, samples):
        self.algorithm = algorithm
        self.problems = problems
        self.measurement = measure
        self.samples = samples


class UserSettings(object):
    def __init__(self, user, job):
        self.user = user
        self.job = job


class LocationSettings(object):
    def __init__(self, base_location, results_location):
        self.base_location = base_location
        self.results_location = results_location


# Statistical functions
def friedman(results, alpha=0.05):
    '''
    Performs the Friedman test on the given results determining if there is a difference between configurations

    results: list of list of numbers representing results for parameters for a number of problems
    alpha: 1 - confidence of outcome
    '''

    ranks = rankdata(array(results), axis=1)
    (k,n) = ranks.shape
    T = (n-1)*sum((sum(ranks) - k*(n+1)/2.)**2) / sum(sum(ranks ** 2 - (n+1)*(n+1) / 4.))
    return T, chi2.ppf(1-alpha, n-1)


def post_hoc(results, alpha, stat):
    '''
    Performs a post-hoc test on the given results to determine the index configurations which are not 
    statistically worse than the best configuration

    results: list of list of numbers representing results for parameters for a number of problems
    alpha: 1 - confidence of outcome
    stat: statistic obtained from friedman test
    '''

    ranks = rankdata(array(results), axis=1)
    (k,n) = ranks.shape
    rank_sum = list(sum(ranks))
    best = min(rank_sum)
    rhs = ((2*k*(1-stat/(k*(n-1)))*sum(sum(ranks**2 - (n+1)*(n+1) / 4.)))/((k-1)*(n-1)))**0.5 * t.ppf(1-alpha/2, n-1)
    return [rank_sum.index(i) for i in rank_sum if abs(best - i) < rhs]


def generate_results(user_settings, location_settings):
    '''
    Function to generate a results table and a list of parameters given from a directory
    It is assumed that there are an equal number results for each parameter
    '''

    def by_iter(x):
        return int(os.path.basename(x).split('_')[0])

    def file_mean(x, obj=1):
        return obj * scipy.mean([float(i) for i in open(x, 'r').readlines()[-1].split(' ')[1:]])

    results = []
    pars = []
    path = os.path.join(location_settings.results_location, user_settings.user, user_settings.job)
    files = sorted(os.listdir(path), key=by_iter)

    groups = groupby(files, by_iter)
    for k in groups:
        ps = sorted([v for v in k[1]])

        if not pars:
            pars = [ p[p.find('_')+1:].replace('.txt', '') for p in ps ]

        results.append([file_mean(os.path.join(path, p), 1 if 'min' in p else -1) for p in ps])

    return results, pars


def iteration(pars, user_settings, simulation_settings, frace_settings, iteration, location_settings):
    run_script(generate_script(pars, iteration, simulation_settings, user_settings, location_settings))

    while not all(os.path.exists(p) for p in parameter_filenames(user_settings, iteration, pars, location_settings)):
        # wait for results
        time.sleep(60000)

    results, pars = generate_results(user_settings, location_settings)

    if len(results) >= frace_settings.min_probs and len(pars) > 1:
        print 'Consulting Milton'
        f_stat, p_val = friedman(results, frace_settings.alpha)

        if f_stat > p_val:
            print 'Difference detected'
            indexes = set(post_hoc(results, frace_settings.alpha, f_stat))

            if indexes:
                if len(indexes) >= frace_settings.min_solutions:
                    print '== Reducing by index'
                    print 'Keeping:', indexes
                    pars = [pars[i] for i in indexes]
                    print 'Parameter count:', len(pars)
                    print '=='
                else:
                    # if not enough surviving configs, get best min_solutions
                    print '== Reducing by min_solutions'
                    pars = sort_pars(results, pars)[:frace_settings.min_solutions]
                    print 'Parameter count:', len(pars)
                    print '=='
            else:
                print 'Could not find difference'

    return pars


def runner(user_settings, simulation_settings, frace_settings, ifrace_settings, location_settings):

    path = os.path.join(location_settings.base_location, user_settings.user, user_settings.job)

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        shutil.rmtree(path)

    print '** Generating parameters'
    pars = [p for p in frace_settings.generator()]

    print '** Preparing output file'
    result_filename = os.path.join(location_settings.base_location, user_settings.user, 'frace_' + user_settings.job + '.txt')

    results_file = open(result_filename, 'w+')
    results_file.write('0 ' + ' '.join([par_to_result(p) for p in pars]) + '\n')

    i = 1
    while i <= frace_settings.iterations:

        print '\nStarting iteration', i

        # regenerate parameters if needed
        if ifrace_settings.is_iterative and i % ifrace_settings.interval == 0:
            print 'Regenerating parameters...'
            pars = ifrace_settings.regenerator(pars)
            # delete all result files for this frace run since they're not used anymore
            shutil.rmtree(os.path.join(location_settings.results_location, user_settings.user, user_settings.job))
            os.makedirs(os.path.join(location_settings.results_location, user_settings.user, user_settings.job))

        # get list of current result files
        toRemove = copy.deepcopy(pars)

        # frace iteration
        print '-- Iteration'
        pars = iteration(pars, user_settings, simulation_settings, frace_settings, i, location_settings)

        # delete unused results
        print '-- Deleting removed parameters'
        toRemove = [ p for p in toRemove if not p in pars ]
        for p in toRemove:
            for j in glob.glob(os.path.join(location_settings.results_location, user_settings.user, user_settings.job, '*' + p + '*')):
                os.remove(j)
        print '       Removed', len(toRemove), 'parameters'

        # sort parameters
        print '-- Sorting parameters'
        pars = sort_pars(*generate_results(user_settings, location_settings))

        # write pars to result file
        results_file.write(str(i) + ' ' + ' '.join([par_to_result(p) for p in pars]) + '\n')

        i += 1

        # this is so we don't waste time tuning when there is no chance of reducing the no. of parameters
        if ifrace_settings.is_iterative and len(pars) == frace_settings.min_solutions:
            print '-- Recalculating iteration'
            i = min(frace_settings.iterations, (ifrace_settings.interval + 1) * i / ifrace_settings.interval)
            print i

        print '-- Remaining parameter count: ', len(pars)
        print 'Ending iteration\n'

    results_file.close()

    # clear results folder, TODO: not sure if this is needed for ciclops
    shutil.rmtree(os.path.join(results_location, user_settings.user, user_settings.job))

    print '** Done'
    return result_filename

