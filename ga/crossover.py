"""
Crossover Module

Implements Order Crossover (OX) — the standard crossover operator
for permutation-based chromosomes.

OX preserves the relative order of elements, which is critical
for permutation encodings where duplicates are not allowed.
"""

import random


def order_crossover(parent1, parent2):
    """
    Perform Order Crossover (OX) on two parent chromosomes.
    
    Algorithm:
        1. Select two random crossover points.
        2. Copy the segment between the points from parent1 to child1.
        3. Fill the remaining positions with genes from parent2,
           in the order they appear, skipping genes already in the child.
        4. Repeat symmetrically for child2.
    
    Args:
        parent1 (list[int]): First parent chromosome.
        parent2 (list[int]): Second parent chromosome.
    
    Returns:
        tuple: (child1, child2) — two offspring chromosomes.
    """
    size = len(parent1)
    
    # Select two crossover points
    point1, point2 = sorted(random.sample(range(size), 2))
    
    # --- Build Child 1 ---
    child1 = [None] * size
    # Copy segment from parent1
    child1[point1:point2 + 1] = parent1[point1:point2 + 1]
    
    # Genes already in child1
    child1_genes = set(child1[point1:point2 + 1])
    
    # Fill remaining positions from parent2, starting after point2
    fill_position = (point2 + 1) % size
    for i in range(size):
        gene = parent2[(point2 + 1 + i) % size]
        if gene not in child1_genes:
            child1[fill_position] = gene
            fill_position = (fill_position + 1) % size
    
    # --- Build Child 2 (symmetric) ---
    child2 = [None] * size
    child2[point1:point2 + 1] = parent2[point1:point2 + 1]
    
    child2_genes = set(child2[point1:point2 + 1])
    
    fill_position = (point2 + 1) % size
    for i in range(size):
        gene = parent1[(point2 + 1 + i) % size]
        if gene not in child2_genes:
            child2[fill_position] = gene
            fill_position = (fill_position + 1) % size
    
    return child1, child2