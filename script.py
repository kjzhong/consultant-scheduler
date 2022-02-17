import pandas as pd
import numpy as np
import itertools

# Given an excel file with all of the lead_consultant availabilities and consultant availabilities, the goal of this code is to find schedules that work.
# Note that ideally we'd like to optimise groups for variety (), but I don't have access to that data

# Importing files and saving as df


def process_data(df):
    df = df.replace([np.nan, "?"], 0)
    df = df.replace("OK", 1)
    df = df.astype(int)

    return df


# Read the data
lead_consultant_df = pd.read_excel(
    "./data/lead_consultant.xls", header=1, index_col=0, skiprows=1, skipfooter=1
)

consultant_df = pd.read_excel(
    "./data/consultant.xls", header=0, index_col=0, skipfooter=1
)

# Process the data
lead_consultant_df = process_data(lead_consultant_df)
consultant_df = process_data(consultant_df)

# create dictionary with consultant availabilities
consultant_avail = consultant_df.to_dict("index")
lead_consultant_avail = lead_consultant_df.to_dict("index")


def reverse_availabilities(availabilities):
    # reverse dictionaries
    # consultant: [list of availabilities]

    for avail in availabilities:
        availabilities[avail] = [
            x for x in availabilities[avail].keys() if availabilities[avail][x] != 0
        ]

    return availabilities


consultant_avail = reverse_availabilities(consultant_avail)
lead_consultant_avail = reverse_availabilities(lead_consultant_avail)

# create  2 fake consultants for a mvp.
consultant_avail[49] = list(consultant_df)
consultant_avail[50] = list(consultant_df)

# The lead_consultant list is bigger than the consultant list. Subset accordingly
for lead_consultant in lead_consultant_avail:
    lead_consultant_avail[lead_consultant] = [
        j for j in lead_consultant_avail[lead_consultant] if j in list(consultant_df)
    ]


# Make a function to find the number of days a person is available AFTER the selected class (cause going to greedyfill in sorted order)


def avail_after(person, daytime):
    """
    Finds the number of classes the person can make if they
    aren't selected for this particular class

    person should be a list of days (['M13', 'T09', 'W13']) sorted
    by day and time of the day.

    time should be a string that is one of the days.

    This function needs to order the days and times.
    """

    def timesplit(s):
        """Splits a time in format M13 to day and hour (M,13)"""
        head = s.rstrip("0123456789")
        tail = int(s[len(head) :])
        return head, tail

    day, time = timesplit(daytime)

    weekday_index = {"M": 1, "T": 2, "W": 3, "TH": 4, "F": 5, "S": 6}

    not_same_day = len(
        [i for i in person if weekday_index[timesplit(i)[0]] > weekday_index[day]]
    )

    same_day = len(
        [
            i
            for i in person
            if weekday_index[timesplit(i)[0]] == weekday_index[day]
            and timesplit(i)[1] > time
        ]
    )
    return same_day + not_same_day


# Now we have to make a list of possible combinations of timeslots
max_schedule = [i for i in itertools.combinations(list(consultant_df), 5)]

# With a given schedule of classes, assign lead consultants to each one.
# For each class, find out how many more classes of the 5 chosen each lead_consultant can still go to, and select the one with the least. So this is ignoring this class, and the classes in assignments.
# This needs to only iterate through the lead consultants who have not been assigned already.


def validate(schedule, lead_consultant_avail):
    """Validates a set of five days.
    If valid, returns the assignment as a dictionary
    If invalid, returns None"""
    assignments = {}
    for i in schedule:
        d = {}

        # assign classes for each lead consultant
        for lead_consultant in lead_consultant_avail:

            # only work through lc without classes already
            if lead_consultant not in assignments.values():
                # ignore already assigned classes
                ignore = set(i).union(set(assignments.keys()))

                # find valid schedules for the current lead consultant
                happy = set(lead_consultant_avail[lead_consultant]).intersection(
                    schedule
                )

                # calculate the classes the lead consultant can take
                d[lead_consultant] = happy - ignore

        if d:
            assignments[i] = min(d, key=d.get)
        else:
            return None
    return assignments


# Now to start greedyfilling consultants


def fillclass(schedule, consultant_avail):
    # Going to need to flatten the classes (will be list of cons)
    flatten = lambda l: [item for sublist in l for item in sublist]
    assignments = {}
    for i in schedule:
        d = {}
        for consultant in consultant_avail:
            if consultant in flatten(assignments.values()):
                pass
            else:
                # values we have to ignore
                ignore = set(i).union(set(assignments.keys()))
                # intersect consultant availabilities with schedule
                happy = set(consultant_avail[consultant]).intersection(schedule)
                d[consultant] = happy - ignore
        if len(d) >= 10:
            # first make a list of the 10 consultants we want to take
            # this is done by finding the smallest and popping from d 10x
            l = []
            for _ in range(10):
                l.append(min(d, key=d.get))
                del d[min(d, key=d.get)]
            assignments[i] = l
        else:
            return None
    return assignments


fillclass(max_schedule[0], consultant_avail)

validate(max_schedule[0], lead_consultant_avail)

final_schedules = []

final_schedules = [
    schedule for schedule in max_schedule if fillclass(schedule, consultant_avail)
]

# all of these are valid schedules
print(final_schedules)
