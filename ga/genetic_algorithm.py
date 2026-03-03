"""
Genetic Algorithm Engine

Orchestrates the full GA loop:
    1. Initialize population
    2. Evaluate (decode + fitness)
    3. Select parents
    4. Crossover
    5. Mutate
    6. Replace (with elitism)
    7. Repeat for N generations
"""

import random
from ga.population import initialize_population
from ga.selection import tournament_selection
from ga.crossover import order_crossover
from ga.mutation import swap_mutation


class GeneticAlgorithm:
    """
    GA engine for solving UCTP via permutation-based indirect representation.
    
    Parameters:
        schedule_builder: ScheduleBuilder instance (the decoder).
        fitness_evaluator: FitnessEvaluator instance.
        event_ids (list[int]): All event IDs.
        population_size (int): Number of individuals per generation.
        generations (int): Number of generations to run.
        crossover_rate (float): Probability of crossover occurring.
        mutation_rate (float): Probability of mutation per individual.
        tournament_size (int): Size of tournament for selection.
        elitism_count (int): Number of best individuals preserved each gen.
    """
    
    def __init__(self, schedule_builder, fitness_evaluator, event_ids,
                 population_size=100, generations=300,
                 crossover_rate=0.8, mutation_rate=0.05,
                 tournament_size=3, elitism_count=2):
        self.builder = schedule_builder
        self.evaluator = fitness_evaluator
        self.event_ids = event_ids
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
    
    def _evaluate_population(self, population):
        """
        Decode and evaluate every chromosome in the population.
        
        Returns:
            list[dict]: List of fitness result dicts (parallel to population).
        """
        results = []
        for chromosome in population:
            timetable, unplaced = self.builder.build(chromosome)
            result = self.evaluator.evaluate(timetable, unplaced)
            result['timetable'] = timetable
            result['unplaced'] = unplaced
            result['chromosome'] = chromosome
            results.append(result)
        return results
    
    def run(self):
        """
        Execute the GA.
        
        Returns:
            dict: The best result found across all generations, containing:
                  'fitness', 'timetable', 'chromosome', penalty breakdowns, etc.
        """
        print(f"{'='*60}")
        print(f"  GA for UCTP — Starting Evolution")
        print(f"  Population: {self.population_size} | "
              f"Generations: {self.generations}")
        print(f"  Crossover Rate: {self.crossover_rate} | "
              f"Mutation Rate: {self.mutation_rate}")
        print(f"  Events to schedule: {len(self.event_ids)}")
        print(f"{'='*60}")
        
        # Step 1: Initialize population
        population = initialize_population(self.event_ids, self.population_size)
        
        # Track the global best across all generations
        global_best = None
        
        for gen in range(self.generations):
            # Step 2: Evaluate
            results = self._evaluate_population(population)
            fitness_scores = [r['fitness'] for r in results]
            
            # Find generation best
            gen_best_idx = min(range(len(results)),
                               key=lambda i: results[i]['fitness'])
            gen_best = results[gen_best_idx]
            
            # Update global best
            if global_best is None or gen_best['fitness'] < global_best['fitness']:
                global_best = dict(gen_best)  # copy
            
            # Logging
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            if gen % 25 == 0 or gen == self.generations - 1:
                print(
                    f"  Gen {gen:>4d} | "
                    f"Best: {gen_best['fitness']:>10.1f} | "
                    f"Avg: {avg_fitness:>10.1f} | "
                    f"Unplaced: {gen_best['unplaced_count']} | "
                    f"Gaps: {gen_best['student_gaps_raw']} | "
                    f"LecPref: {gen_best['lecturer_violations_raw']}"
                )
            
            # Step 3-6: Create next generation
            # Sort by fitness for elitism
            sorted_indices = sorted(range(len(results)),
                                    key=lambda i: results[i]['fitness'])
            
            new_population = []
            
            # Elitism: carry forward the best individuals unchanged
            for i in range(self.elitism_count):
                elite = list(population[sorted_indices[i]])
                new_population.append(elite)
            
            # Fill the rest of the population
            while len(new_population) < self.population_size:
                # Selection
                parent1 = tournament_selection(
                    population, fitness_scores, self.tournament_size
                )
                parent2 = tournament_selection(
                    population, fitness_scores, self.tournament_size
                )
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child1, child2 = order_crossover(parent1, parent2)
                else:
                    child1, child2 = list(parent1), list(parent2)
                
                # Mutation
                child1 = swap_mutation(child1, self.mutation_rate)
                child2 = swap_mutation(child2, self.mutation_rate)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            population = new_population
        
        print(f"{'='*60}")
        print(f"  Evolution Complete!")
        print(f"  Best Fitness: {global_best['fitness']:.1f}")
        print(f"  Unplaced Events: {global_best['unplaced_count']}")
        print(f"  Student Gaps: {global_best['student_gaps_raw']}")
        print(f"  Lecturer Pref Violations: "
              f"{global_best['lecturer_violations_raw']}")
        print(f"{'='*60}")
        
        return global_best