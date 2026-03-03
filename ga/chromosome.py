"""
Chromosome Module

A chromosome is a permutation of event IDs.
This module handles creation of random chromosomes.
"""

import random


def create_random_chromosome(event_ids):
    """
    Create a random permutation of event IDs.
    
    Args:
        event_ids (list[int]): List of all event IDs in the problem.
    
    Returns:
        list[int]: A randomly shuffled copy of event_ids.
    """
    chromosome = list(event_ids)
    random.shuffle(chromosome)
    return chromosome