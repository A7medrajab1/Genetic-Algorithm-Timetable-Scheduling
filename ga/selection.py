"""
Selection Module

Implements tournament selection for the GA.
"""

import random


def tournament_selection(population, fitness_scores, tournament_size=3):
    """
    Select one individual using tournament selection.
    
    Process:
        1. Randomly pick `tournament_size` individuals from the population.
        2. Return the one with the LOWEST fitness (minimization problem).
    
    Args:
        population (list): List of chromosomes.
        fitness_scores (list[float]): Parallel list of fitness values.
        tournament_size (int): Number of contestants per tournament.
    
    Returns:
        list[int]: The winning chromosome (a copy).
    """
    # Select random indices
    contestants = random.sample(range(len(population)), tournament_size)
    
    # Find the contestant with the best (lowest) fitness
    best_idx = min(contestants, key=lambda i: fitness_scores[i])
    
    return list(population[best_idx])  # Return a copy