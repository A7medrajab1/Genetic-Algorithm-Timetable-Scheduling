"""
Mutation Module (v3)

Three mutation operators for stronger exploration:
    1. Swap Mutation: Swap two random genes
    2. Inversion Mutation: Reverse a random subsequence
    3. Scramble Mutation: Shuffle a random subsequence

Adaptive mutation: rate increases when GA stagnates.
"""

import random


def swap_mutation(chromosome, mutation_rate=0.15):
    """Swap two randomly selected genes."""
    if random.random() < mutation_rate:
        size = len(chromosome)
        i, j = random.sample(range(size), 2)
        chromosome[i], chromosome[j] = chromosome[j], chromosome[i]
    return chromosome


def inversion_mutation(chromosome, mutation_rate=0.08):
    """Reverse a random subsequence."""
    if random.random() < mutation_rate:
        size = len(chromosome)
        i, j = sorted(random.sample(range(size), 2))
        chromosome[i:j+1] = reversed(chromosome[i:j+1])
    return chromosome


def scramble_mutation(chromosome, mutation_rate=0.05):
    """
    Shuffle a random subsequence.
    
    Stronger than inversion — completely randomizes a section.
    Good for escaping local optima.
    
    Example:
        [A, B, |C, D, E, F|, G] → [A, B, |E, C, F, D|, G]
    """
    if random.random() < mutation_rate:
        size = len(chromosome)
        i, j = sorted(random.sample(range(size), 2))
        section = chromosome[i:j+1]
        random.shuffle(section)
        chromosome[i:j+1] = section
    return chromosome


def mutate(chromosome, swap_rate=0.15, inversion_rate=0.08,
           scramble_rate=0.05):
    """
    Apply all three mutation operators sequentially.
    
    Args:
        chromosome: The chromosome to mutate.
        swap_rate: Probability of swap mutation.
        inversion_rate: Probability of inversion mutation.
        scramble_rate: Probability of scramble mutation.
    
    Returns:
        The (possibly mutated) chromosome.
    """
    chromosome = swap_mutation(chromosome, swap_rate)
    chromosome = inversion_mutation(chromosome, inversion_rate)
    chromosome = scramble_mutation(chromosome, scramble_rate)
    return chromosome