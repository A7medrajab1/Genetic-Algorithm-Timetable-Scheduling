"""
Soft Constraint Evaluation Module (v2)

Implements three soft constraints:
    S1a — Minimize Student Gaps
    S4  — Promote Event Spreading (penalize overloaded days)
    S5  — Lecturer Time Preferences
"""

from collections import defaultdict
import math


def calculate_student_gap_penalty(timetable, timeslots_dict, events_dict):
    """
    S1a: Minimize idle gaps in each student group's daily schedule.
    
    For each student group, for each day:
        1. Find all periods where they have events.
        2. Count the idle (empty) periods between first and last event.
    
    Returns:
        int: Total gap count across all student groups and all days.
    """
    group_day_periods = defaultdict(lambda: defaultdict(list))
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[timeslot_id]
        
        for group_id in event.student_group_ids:
            group_day_periods[group_id][timeslot.day].append(timeslot.period)
    
    total_gaps = 0
    
    for group_id, days in group_day_periods.items():
        for day, periods in days.items():
            if len(periods) <= 1:
                continue
            
            sorted_periods = sorted(periods)
            span = sorted_periods[-1] - sorted_periods[0] + 1
            gaps = span - len(sorted_periods)
            total_gaps += gaps
    
    return total_gaps


def calculate_spreading_penalty(timetable, timeslots_dict, events_dict):
    """
    S4: Penalize uneven distribution of events across days for each 
    student group.
    
    For each student group:
        Count events per day. Penalize any day that has more than
        a "fair share" (total_events / num_active_days, rounded up).
    
    This discourages cramming all events into 1-2 days.
    
    Returns:
        int: Total spreading penalty.
    """
    group_day_counts = defaultdict(lambda: defaultdict(int))
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        timeslot = timeslots_dict[timeslot_id]
        
        for group_id in event.student_group_ids:
            group_day_counts[group_id][timeslot.day] += 1
    
    total_penalty = 0
    
    for group_id, day_counts in group_day_counts.items():
        if not day_counts:
            continue
        
        total_events = sum(day_counts.values())
        
        # Dynamic number of days in the week
        all_days = set(ts.day for ts in timeslots_dict.values())
        num_days = len(all_days)
        
        ideal_per_day = math.ceil(total_events / num_days)
        
        for day, count in day_counts.items():
            if count > ideal_per_day:
                excess = count - ideal_per_day
                total_penalty += excess
    
    return total_penalty


def calculate_lecturer_preference_penalty(timetable, timeslots_dict,
                                           events_dict, lecturers_dict):
    """
    S5: Penalize events scheduled outside lecturer's preferred timeslots.
    
    Returns:
        int: Total count of lecturer preference violations.
    """
    total_violations = 0
    
    for event_id, (timeslot_id, room_id) in timetable.items():
        event = events_dict[event_id]
        lecturer = lecturers_dict.get(event.lecturer_id)
        
        if lecturer is None:
            continue
        
        if not lecturer.prefers(timeslot_id):
            total_violations += 1
    
    return total_violations