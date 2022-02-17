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

# print(consultant_df)
c_avail = consultant_df.to_dict("index")

for consultant in c_avail:
    c_avail[consultant] = [
        j for j in c_avail[consultant].keys() if c_avail[consultant][j] != 0
    ]


# Make 2 fake consultants for a mvp.
c_avail[49] = list(consultant_df)
c_avail[50] = list(consultant_df)

lc_avail = lead_consultant_df.to_dict("index")

for lead_consultant in lc_avail:
    lc_avail[lead_consultant] = [
        j for j in lc_avail[lead_consultant].keys() if lc_avail[lead_consultant][j] != 0
    ]

# The lead_consultant list is bigger than the consultant list. Subset accordingly
for lead_consultant in lc_avail:
    lc_avail[lead_consultant] = [
        j for j in lc_avail[lead_consultant] if j in list(consultant_df)
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
        """Splits a time in format M13 to head and tail (M,13)"""
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


# ## First Implementation:
# * Fill by how many availabilities a student has after the day of the class, same logic for lead_consultant
#
# ## Proposed Implementaion:
# * Fill by how many availabilities a student has of the REMAINING classes that have already been chosen. Same logic for lead_consultant. This is important as you already know the remaining classes.

# Now we have to make a list of valid schedules

max_schedule = [i for i in itertools.combinations(list(consultant_df), 5)]


# With a given schedule of classes, assign lead consultants to each one.
#
# For each class, find out how many more classes of the 5 chosen each lead_consultant can still go to, and select the one with the least. So this is ignoring this class, and the classes in assignments.
#
# This needs to only iterate through the lead consultants who have not been assigned already.


def validate(schedule):
    """Validates a set of five days.
    If valid, returns the assignment as a dictionary
    If invalid, returns 0"""
    assignments = {}
    for i in schedule:
        d = {}
        for lead_consultant in lc_avail:
            if lead_consultant in assignments.values():
                pass
            else:
                # values we have to ignore
                ignore = set(i).union(set(assignments.keys()))
                # intersect lead_consultant availabilities with schedule
                happy = set(lc_avail[lead_consultant]).intersection(schedule)
                d[lead_consultant] = happy - ignore
        if d:
            assignments[i] = min(d, key=d.get)
        else:
            return 0
    return assignments


# Now to start greedyfilling consultants


def fillclass(schedule):
    # Going to need to flatten the classes (will be list of cons)
    flatten = lambda l: [item for sublist in l for item in sublist]
    assignments = {}
    for i in schedule:
        d = {}
        for consultant in c_avail:
            if consultant in flatten(assignments.values()):
                pass
            else:
                # values we have to ignore
                ignore = set(i).union(set(assignments.keys()))
                # intersect consultant availabilities with schedule
                happy = set(c_avail[consultant]).intersection(schedule)
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
            return 0
    return assignments


fillclass(max_schedule[0])

validate(max_schedule[0])

for i in max_schedule:
    if not fillclass(i):
        print(f"{i} doesn't work")
