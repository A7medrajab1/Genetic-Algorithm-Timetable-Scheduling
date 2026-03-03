"""
Genetic Algorithm Engine (v3)

Changes from v2:
- Triple mutation (swap + inversion + scramble)
- Adaptive mutation rates (increase when stagnating)
- Population restart when stuck too long
- Better diversity tracking
"""

import random
from ga.population import initialize_population
from ga.selection import tournament_selection
from ga.crossover import order_crossover
from ga.mutation import mutate


class GeneticAlgorithm:
    """
    GA engine for solving UCTP via permutation-based indirect representation.
    
    Features:
    - Elitism (preserve best solutions)
    - Tournament selection
    - Order crossover (OX) for permutations
    - Triple mutation (swap + inversion + scramble)
    - Adaptive mutation (increases when stagnating)
    - Partial population restart (injects diversity when stuck)
    """
    
    def __init__(self, schedule_builder, fitness_evaluator, event_ids,
                 population_size=150, generations=500,
                 crossover_rate=0.85,
                 swap_mutation_rate=0.15,
                 inversion_mutation_rate=0.08,
                 scramble_mutation_rate=0.05,
                 tournament_size=4, elitism_count=3):
        self.builder = schedule_builder
        self.evaluator = fitness_evaluator
        self.event_ids = event_ids
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.base_swap_rate = swap_mutation_rate
        self.base_inversion_rate = inversion_mutation_rate
        self.base_scramble_rate = scramble_mutation_rate
        self.tournament_size = tournament_size
        self.elitism_count = elitism_count
    
    def _evaluate_population(self, population):
        """Decode and evaluate every chromosome."""
        results = []
        for chromosome in population:
            timetable, unplaced = self.builder.build(chromosome)
            result = self.evaluator.evaluate(timetable, unplaced)
            result['timetable'] = timetable
            result['unplaced'] = unplaced
            result['chromosome'] = chromosome
            results.append(result)
        return results
    
    def _get_adaptive_rates(self, stagnation_counter):
        """
        Increase mutation rates when the GA is stagnating.
        
        The longer we stagnate, the more aggressive the mutation.
        This helps escape local optima.
        
        Args:
            stagnation_counter: Number of generations without improvement.
        
        Returns:
            tuple: (swap_rate, inversion_rate, scramble_rate)
        """
        if stagnation_counter < 30:
            # Normal rates
            return (self.base_swap_rate,
                    self.base_inversion_rate,
                    self.base_scramble_rate)
        elif stagnation_counter < 80:
            # Medium boost
            return (self.base_swap_rate * 2.0,
                    self.base_inversion_rate * 2.0,
                    self.base_scramble_rate * 3.0)
        else:
            # Heavy boost — desperate exploration
            return (min(self.base_swap_rate * 3.0, 0.50),
                    min(self.base_inversion_rate * 3.0, 0.30),
                    min(self.base_scramble_rate * 5.0, 0.30))
    
    def run(self):
        """Execute the GA with adaptive mutation and restarts."""
        print(f"{'='*70}")
        print(f"  GA for UCTP — Starting Evolution")
        print(f"  Population: {self.population_size} | "
              f"Generations: {self.generations}")
        print(f"  Crossover Rate: {self.crossover_rate}")
        print(f"  Base Mutation: swap={self.base_swap_rate} "
              f"inv={self.base_inversion_rate} "
              f"scr={self.base_scramble_rate}")
        print(f"  Events to schedule: {len(self.event_ids)}")
        print(f"{'='*70}")
        
        # Header
        print(f"  {'Gen':>4s} | {'Best':>8s} | {'Avg':>8s} | "
              f"{'Unpl':>4s} | {'Gaps':>4s} | {'Sprd':>4s} | "
              f"{'LPrf':>4s} | {'MutRate':>7s}")
        print(f"  {'-'*4}-+-{'-'*8}-+-{'-'*8}-+-"
              f"{'-'*4}-+-{'-'*4}-+-{'-'*4}-+-"
              f"{'-'*4}-+-{'-'*7}")
        
        # Initialize population
        population = initialize_population(
            self.event_ids, self.population_size
        )
        
        global_best = None
        stagnation_counter = 0
        restart_count = 0
        
        for gen in range(self.generations):
            # Evaluate
            results = self._evaluate_population(population)
            fitness_scores = [r['fitness'] for r in results]
            
            # Find generation best
            gen_best_idx = min(range(len(results)),
                               key=lambda i: results[i]['fitness'])
            gen_best = results[gen_best_idx]
            
            # Update global best
            if (global_best is None or
                    gen_best['fitness'] < global_best['fitness']):
                global_best = dict(gen_best)
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            
            # Get adaptive mutation rates
            swap_r, inv_r, scr_r = self._get_adaptive_rates(
                stagnation_counter
            )
            
            # Logging
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            if gen % 20 == 0 or gen == self.generations - 1:
                print(
                    f"  {gen:>4d} | "
                    f"{gen_best['fitness']:>8.1f} | "
                    f"{avg_fitness:>8.1f} | "
                    f"{gen_best['unplaced_count']:>4d} | "
                    f"{gen_best['student_gaps_raw']:>4d} | "
                    f"{gen_best['spreading_raw']:>4d} | "
                    f"{gen_best['lecturer_violations_raw']:>4d} | "
                    f"{swap_r:>5.2f}x"
                )
            
            # PARTIAL RESTART: If stuck for 120+ generations,
            # replace 40% of population with fresh random chromosomes
            if stagnation_counter > 0 and stagnation_counter % 120 == 0:
                restart_count += 1
                num_replace = int(self.population_size * 0.4)
                
                # Keep the elites
                sorted_indices = sorted(
                    range(len(results)),
                    key=lambda i: results[i]['fitness']
                )
                
                # Preserve top individuals
                survivors = []
                for i in range(self.population_size - num_replace):
                    survivors.append(
                        list(population[sorted_indices[i]])
                    )
                
                # Inject fresh random chromosomes
                fresh = initialize_population(
                    self.event_ids, num_replace
                )
                population = survivors + fresh
                
                if gen % 20 == 0 or True:
                    print(f"  *** RESTART #{restart_count}: "
                          f"Replaced {num_replace} individuals "
                          f"(stagnation={stagnation_counter})")
                continue
            
            # Create next generation
            sorted_indices = sorted(
                range(len(results)),
                key=lambda i: results[i]['fitness']
            )
            
            new_population = []
            
            # Elitism
            for i in range(self.elitism_count):
                elite = list(population[sorted_indices[i]])
                new_population.append(elite)
            
            # Fill the rest
            while len(new_population) < self.population_size:
                parent1 = tournament_selection(
                    population, fitness_scores, self.tournament_size
                )
                parent2 = tournament_selection(
                    population, fitness_scores, self.tournament_size
                )
                
                if random.random() < self.crossover_rate:
                    child1, child2 = order_crossover(parent1, parent2)
                else:
                    child1, child2 = list(parent1), list(parent2)
                
                # Adaptive mutation
                child1 = mutate(child1, swap_r, inv_r, scr_r)
                child2 = mutate(child2, swap_r, inv_r, scr_r)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            population = new_population
        
        print(f"{'='*70}")
        print(f"  Evolution Complete!")
        print(f"  Best Fitness:              {global_best['fitness']:.1f}")
        print(f"  Unplaced Events:           {global_best['unplaced_count']}")
        print(f"  Student Gaps (raw):        "
              f"{global_best['student_gaps_raw']}")
        print(f"  Spreading Penalty (raw):   "
              f"{global_best['spreading_raw']}")
        print(f"  Lecturer Pref Violations:  "
              f"{global_best['lecturer_violations_raw']}")
        print(f"  Total Restarts:            {restart_count}")
        print(f"  Final Stagnation:          {stagnation_counter}")
        print(f"{'='*70}")
        
        return global_best