"""
Fitness Function Module

Evaluates a decoded timetable and returns a single numeric fitness score.

Fitness = UNPLACED_PENALTY + α * StudentGapPenalty + β * LecturerPreferencePenalty

Where:
    - UNPLACED_PENALTY = 100000 per unplaced event (catastrophic)
    - α (alpha) = weight for student gap penalty (S1a)
    - β (beta)  = weight for lecturer preference penalty (S5)

LOWER fitness is BETTER (minimization problem).
"""

from constraints.soft_constraints import (
    calculate_student_gap_penalty,
    calculate_lecturer_preference_penalty,
)


class FitnessEvaluator:
    """
    Evaluates the quality of a decoded timetable.
    
    Attributes:
        timeslots_dict (dict): timeslot_id -> Timeslot object.
        events_dict (dict): event_id -> Event object.
        lecturers_dict (dict): lecturer_id -> Lecturer object.
        alpha (float): Weight for student gap penalty (S1a).
        beta (float): Weight for lecturer preference penalty (S5).
        unplaced_penalty (float): Penalty per unplaced event.
    """
    
    def __init__(self, timeslots_dict, events_dict, lecturers_dict,
                 alpha=10.0, beta=5.0, unplaced_penalty=100000.0):
        self.timeslots_dict = timeslots_dict
        self.events_dict = events_dict
        self.lecturers_dict = lecturers_dict
        self.alpha = alpha
        self.beta = beta
        self.unplaced_penalty = unplaced_penalty
    
    def evaluate(self, timetable, unplaced_events):
        """
        Compute the fitness score of a decoded timetable.
        
        Args:
            timetable (dict): event_id -> (timeslot_id, room_id).
            unplaced_events (list): List of event_ids not placed.
        
        Returns:
            dict: {
                'fitness': float (total score, lower is better),
                'unplaced_count': int,
                'unplaced_penalty_total': float,
                'student_gap_penalty': float,
                'lecturer_pref_penalty': float,
                'student_gaps_raw': int,
                'lecturer_violations_raw': int,
            }
        """
        # Catastrophic penalty for unplaced events
        unplaced_count = len(unplaced_events)
        unplaced_total = unplaced_count * self.unplaced_penalty
        
        # S1a: Student gap penalty
        student_gaps_raw = calculate_student_gap_penalty(
            timetable, self.timeslots_dict, self.events_dict
        )
        student_gap_penalty = self.alpha * student_gaps_raw
        
        # S5: Lecturer preference penalty
        lecturer_violations_raw = calculate_lecturer_preference_penalty(
            timetable, self.timeslots_dict, self.events_dict, self.lecturers_dict
        )
        lecturer_pref_penalty = self.beta * lecturer_violations_raw
        
        # Total fitness (minimize)
        fitness = unplaced_total + student_gap_penalty + lecturer_pref_penalty
        
        return {
            'fitness': fitness,
            'unplaced_count': unplaced_count,
            'unplaced_penalty_total': unplaced_total,
            'student_gap_penalty': student_gap_penalty,
            'lecturer_pref_penalty': lecturer_pref_penalty,
            'student_gaps_raw': student_gaps_raw,
            'lecturer_violations_raw': lecturer_violations_raw,
        }