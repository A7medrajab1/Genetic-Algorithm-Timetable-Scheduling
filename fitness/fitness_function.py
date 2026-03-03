"""
Fitness Function Module (v3)

Fitness = UNPLACED_PENALTY
        + alpha * StudentGapPenalty         (S1a)
        + delta * SingleEventDayPenalty     (S1b)
        + gamma * SpreadingPenalty          (S4)
        + beta  * LecturerPreferencePenalty (S5)

LOWER fitness = BETTER timetable.
"""

from constraints.soft_constraints import (
    calculate_student_gap_penalty,
    calculate_single_event_day_penalty,
    calculate_spreading_penalty,
    calculate_lecturer_preference_penalty,
)


class FitnessEvaluator:
    """
    Evaluates the quality of a decoded timetable.
    
    Parameters:
        alpha (float): Weight for student gap penalty (S1a).
        delta (float): Weight for single-event-day penalty (S1b).
        gamma (float): Weight for event spreading penalty (S4).
        beta (float): Weight for lecturer preference penalty (S5).
        unplaced_penalty (float): Penalty per unplaced event.
    """
    
    def __init__(self, timeslots_dict, events_dict, lecturers_dict,
                 alpha=10.0, delta=7.0, gamma=8.0, beta=5.0,
                 unplaced_penalty=100000.0):
        self.timeslots_dict = timeslots_dict
        self.events_dict = events_dict
        self.lecturers_dict = lecturers_dict
        self.alpha = alpha
        self.delta = delta
        self.gamma = gamma
        self.beta = beta
        self.unplaced_penalty = unplaced_penalty
    
    def evaluate(self, timetable, unplaced_events):
        """
        Compute the fitness score of a decoded timetable.
        
        Returns:
            dict: Detailed breakdown of fitness components.
        """
        # Catastrophic penalty for unplaced events
        unplaced_count = len(unplaced_events)
        unplaced_total = unplaced_count * self.unplaced_penalty
        
        # S1a: Student gap penalty
        student_gaps_raw = calculate_student_gap_penalty(
            timetable, self.timeslots_dict, self.events_dict
        )
        student_gap_penalty = self.alpha * student_gaps_raw
        
        # S1b: Single-event-day penalty
        single_days_raw = calculate_single_event_day_penalty(
            timetable, self.timeslots_dict, self.events_dict
        )
        single_day_penalty = self.delta * single_days_raw
        
        # S4: Spreading penalty
        spreading_raw = calculate_spreading_penalty(
            timetable, self.timeslots_dict, self.events_dict
        )
        spreading_penalty = self.gamma * spreading_raw
        
        # S5: Lecturer preference penalty
        lecturer_violations_raw = calculate_lecturer_preference_penalty(
            timetable, self.timeslots_dict, self.events_dict,
            self.lecturers_dict
        )
        lecturer_pref_penalty = self.beta * lecturer_violations_raw
        
        # Total fitness (minimize)
        fitness = (unplaced_total + student_gap_penalty +
                   single_day_penalty + spreading_penalty +
                   lecturer_pref_penalty)
        
        return {
            'fitness': fitness,
            'unplaced_count': unplaced_count,
            'unplaced_penalty_total': unplaced_total,
            'student_gap_penalty': student_gap_penalty,
            'single_day_penalty': single_day_penalty,
            'spreading_penalty': spreading_penalty,
            'lecturer_pref_penalty': lecturer_pref_penalty,
            'student_gaps_raw': student_gaps_raw,
            'single_days_raw': single_days_raw,
            'spreading_raw': spreading_raw,
            'lecturer_violations_raw': lecturer_violations_raw,
        }