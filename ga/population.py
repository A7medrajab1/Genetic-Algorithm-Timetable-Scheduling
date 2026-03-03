"""
Population Module

Handles creation and management of a population of chromosomes.
"""

from ga.chromosome import create_random_chromosome


def initialize_population(event_ids, population_size):
    """
    Create an initial population of random chromosomes.
    
    Args:
        event_ids (list[int]): All event IDs.
        population_size (int): Number of individuals in the population.
    
    Returns:
        list[list[int]]: A list of chromosomes (permutations).
    """
    population = []
    for _ in range(population_size):
        population.append(create_random_chromosome(event_ids))
    return population