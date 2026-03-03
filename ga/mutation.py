"""
Mutation Module

Implements swap mutation for permutation-based chromosomes.
"""

import random


def swap_mutation(chromosome, mutation_rate=0.05):
    """
    Perform swap mutation on a chromosome.
    
    With probability `mutation_rate`, two randomly selected genes
    are swapped. This preserves the permutation property (no duplicates).
    
    Args:
        chromosome (list[int]): The chromosome to mutate.
        mutation_rate (float): Probability of mutation occurring.
    
    Returns:
        list[int]: The (possibly mutated) chromosome.
    """
    if random.random() < mutation_rate:
        size = len(chromosome)
        i, j = random.sample(range(size), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
    
    return chromosome