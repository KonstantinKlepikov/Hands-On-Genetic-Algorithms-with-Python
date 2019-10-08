from deap import base
from deap import creator
from deap import tools

import random
import numpy

import matplotlib.pyplot as plt

import zoo_tuning_4
import elitism

# boundaries for all parameters:
MAX_DEPTH_BOUND_LOW, MAX_DEPTH_BOUND_UP = 0, 10
CRITERION_BOUND_LOW, CRITERION_BOUND_UP = 0, 1
SPLITTER_BOUND_LOW, SPLITTER_BOUND_UP = 0, 1

# Genetic Algorithm constants:
POPULATION_SIZE = 50
P_CROSSOVER = 0.9  # probability for crossover
P_MUTATION = 0.2   # probability for mutating an individual
MAX_GENERATIONS = 30
HALL_OF_FAME_SIZE = 5
CROWDING_FACTOR = 20.0  # crowding factor for crossover and mutation

# set the random seed:
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# create the Zoo test class:
zoo = zoo_tuning_4.ZooTuning(RANDOM_SEED)

toolbox = base.Toolbox()

# define a single objective, maximizing fitness strategy:
creator.create("FitnessMax", base.Fitness, weights=(1.0,))

# create the Individual class based on list:
creator.create("Individual", list, fitness=creator.FitnessMax)

# define the attributes individually:
toolbox.register("attrMaxDepth", random.randint, MAX_DEPTH_BOUND_LOW, MAX_DEPTH_BOUND_UP)
toolbox.register("attrCriterion", random.randint, CRITERION_BOUND_LOW, CRITERION_BOUND_UP)
toolbox.register("attrSplitter", random.randint, SPLITTER_BOUND_LOW, SPLITTER_BOUND_UP)

# create the individual operator to fill up an Individual instance:
toolbox.register("individualCreator", tools.initCycle, creator.Individual,
                 (toolbox.attrMaxDepth, toolbox.attrCriterion, toolbox.attrSplitter), n=1)

# create the population operator to generate a list of individuals:
toolbox.register("populationCreator", tools.initRepeat, list, toolbox.individualCreator)


# fitness calculation
def zooClassificationAccuracy(individual):
    return zoo.getAccuracyScore(individual),


toolbox.register("evaluate", zooClassificationAccuracy)

# genetic operators:mutFlipBit

# genetic operators:
toolbox.register("select", tools.selTournament, tournsize=2)
toolbox.register("mate", tools.cxSimulatedBinaryBounded, low=[MAX_DEPTH_BOUND_LOW, CRITERION_BOUND_LOW, SPLITTER_BOUND_LOW], up=[MAX_DEPTH_BOUND_UP, CRITERION_BOUND_UP, SPLITTER_BOUND_UP], eta=CROWDING_FACTOR)
toolbox.register("mutate", tools.mutPolynomialBounded, low=[MAX_DEPTH_BOUND_LOW, CRITERION_BOUND_LOW, SPLITTER_BOUND_LOW], up=[MAX_DEPTH_BOUND_UP, CRITERION_BOUND_UP, SPLITTER_BOUND_UP], eta=CROWDING_FACTOR, indpb=1.0/len(zoo))


# Genetic Algorithm flow:
def main():

    # create initial population (generation 0):
    population = toolbox.populationCreator(n=POPULATION_SIZE)

    # prepare the statistics object:
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", numpy.max)
    stats.register("avg", numpy.mean)

    # define the hall-of-fame object:
    hof = tools.HallOfFame(HALL_OF_FAME_SIZE)

    # perform the Genetic Algorithm flow with hof feature added:
    population, logbook = elitism.eaSimpleWithElitism(population, toolbox, cxpb=P_CROSSOVER, mutpb=P_MUTATION,
                                                      ngen=MAX_GENERATIONS, stats=stats, halloffame=hof, verbose=True)

    # print best solution found:
    print("- Best solutions are:")
    for i in range(HALL_OF_FAME_SIZE):
        print(i, ": ", hof.items[i], ", fitness = ", hof.items[i].fitness.values[0])

    # extract statistics:
    maxFitnessValues, meanFitnessValues = logbook.select("max", "avg")

    # plot statistics:
    plt.plot(maxFitnessValues, color='red')
    plt.plot(meanFitnessValues, color='green')
    plt.xlabel('Generation')
    plt.ylabel('Max / Average Fitness')
    plt.title('Max and Average fitness vs. Generation')
    plt.show()


if __name__ == "__main__":
    main()