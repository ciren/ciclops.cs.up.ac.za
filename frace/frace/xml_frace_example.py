from frace import *
from parameters import *

# The order here coresponds to the tuning parameters below
parameter_bounds = [
(0.01,0.99),
(0.0,4.0),
(0.0,4.0)
]

algorithm = """<algorithm id="pso" class="pso.PSO">
    <initialisationStrategy class="algorithm.initialisation.ClonedPopulationInitialisationStrategy">
        <entityType class="pso.particle.StandardParticle">
            <velocityProvider class="pso.velocityprovider.StandardVelocityProvider">
                <inertiaWeight class="tuning.TuningControlParameter" index="0"/>
                <cognitiveAcceleration class="tuning.TuningControlParameter" index="1"/>
                <socialAcceleration class="tuning.TuningControlParameter" index="2"/>
            </velocityProvider>
        </entityType>
    </initialisationStrategy>
    <addStoppingCondition class="stoppingcondition.MeasuredStoppingCondition" target="100"/>
</algorithm>"""

problems = [
'''<problem id="f1" class="problem.FunctionOptimisationProblem" domain="R(-100:100)^10">
    <function class="functions.continuous.unconstrained.Spherical"/>
</problem>''',

'''<problem id="f2" class="problem.FunctionOptimisationProblem" domain="R(-100:100)^10">
    <function class="functions.continuous.unconstrained.Rosenbrock"/>
</problem>''',

'''<problem id="f3" class="problem.FunctionOptimisationProblem" domain="R(0:600)^10">
    <function class="functions.continuous.unconstrained.Griewank"/>
</problem>''',

'''<problem id="f4" class="problem.FunctionOptimisationProblem" domain="R(-32:32)^10">
    <function class="functions.continuous.unconstrained.Ackley"/>
</problem>''',

'''<problem id="f5" class="problem.FunctionOptimisationProblem" domain="R(-5:5)^10">
    <function class="functions.continuous.unconstrained.Rastrigin"/>
</problem>'''
]

measurement = '<addMeasurement class="measurement.single.Fitness"/>'

ifrace_settings = IFraceSettings(is_iterative=True, interval=10, regenerator=regen_minmax_sobol(32))
frace_settings = FRaceSettings(generator=initial_sobol(parameter_bounds, 32), min_probs=5, min_solutions=2, alpha=0.05, iterations=100)
user_settings = UserSettings('user_name', 'job_name')
location_settings = LocationSettings('/home/filipe/tmp', '/home/filipe/tmp')
simulation = SimulationSettings(algorithm, problems, measurement, samples=30)
runner(user_settings, simulation, frace_settings, ifrace_settings, location_settings)

