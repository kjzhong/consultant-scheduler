#!/usr/bin/env python
# coding: utf-8

# Given an excel file with all of the LC availabilities and consultant availabilities, the goal of this code is to find schedules that work.
# 
# Note that ideally we'd like to optimise groups for variety, but I don't have access to that data

# In[1]:


import pandas as pd
import numpy as np
import itertools


# Importing files and saving as df

# In[2]:


lc_df = pd.read_excel("./data/lc.xls", 
                   header = 1, 
                   index_col = 0, 
                   skiprows = 1,
                   skipfooter = 1)
lc_df = lc_df.replace([np.nan, '?'], 0)
lc_df = lc_df.replace('OK', 1)

lc_df = lc_df.astype(int)

c_df = pd.read_excel("./data/c.xls",
                 header = 0,
                 index_col = 0,
                 skipfooter = 1)
c_df = c_df.replace("OK", 1)
c_df = c_df.fillna(0)

c_df = c_df.astype(int)

c_avail = c_df.to_dict('index')
for c in c_avail:
    c_avail[c] = [j for j in c_avail[c].keys() if c_avail[c][j] != 0]


# #####  There are 48 consultants. For a MVP, I wll make 2 fake consultants.

# In[3]:


c_avail[49] = list(c_df)
c_avail[50] = list(c_df)


# In[4]:


# c_df["M13"].value_counts()


# In[5]:


# lc_5_avail = lc_df.iloc[-1]
# type(lc_5_avail)


# Save the LC dataframe as a dictionary (to start to greedyfill)

# In[6]:


lc_avail = lc_df.to_dict('index')

for lc in lc_avail:
    lc_avail[lc] = [j for j in lc_avail[lc].keys() if lc_avail[lc][j] != 0]
#     x[i] = [j for j in x.keys() if x[i][j] != 0]


# The LC list is bigger than the C list. Subset accordingly
for lc in lc_avail:
    lc_avail[lc] = [j for j in lc_avail[lc] if j in list(c_df)]


# Make a function to find the number of days a person is available AFTER the selected class (cause going to greedyfill in sorted order)

# In[7]:


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
        '''Splits a time in format M13 to head and tail (M,13)'''
        head = s.rstrip('0123456789')
        tail = int(s[len(head):])
        return head,tail
    
    day, time = timesplit(daytime)
    
    weekday_index = {'M' : 1,
                    'T': 2,
                    'W': 3,
                    'TH' : 4,
                    'F' : 5,
                    'S' : 6}
    not_same_day = len([i for i in person if weekday_index[timesplit(i)[0]] > weekday_index[day]])
    same_day = len([i for i in person if weekday_index[timesplit(i)[0]] == weekday_index[day] and timesplit(i)[1] > time])
    return same_day + not_same_day


# ## First Implementation:
# * Fill by how many availabilities a student has after the day of the class, same logic for LC
# 
# ## Proposed Implementaion:
# * Fill by how many availabilities a student has of the REMAINING classes that have already been chosen. Same logic for LC. This is important as you already know the remaining classes.

# Now we have to make a list of valid schedules

# In[8]:


max_schedule = [i for i in itertools.combinations(list(c_df), 5)]


# With a given schedule of classes, assign lead consultants to each one.
# 
# For each class, find out how many more classes of the 5 chosen each LC can still go to, and select the one with the least. So this is ignoring this class, and the classes in assignments.
# 
# This needs to only iterate through the lead consultants who have not been assigned already.

# In[9]:


def validate(schedule):
    """Validates a set of five days.
    If valid, returns the assignment as a dictionary
    If invalid, returns 0"""
    assignments = {}
    for i in schedule:
        d = {}
        for lc in lc_avail:
            if lc in assignments.values():
                pass
            else:
                # values we have to ignore
                ignore = set(i).union(set(assignments.keys()))
                # intersect LC availabilities with schedule
                happy = set(lc_avail[lc]).intersection(schedule)
                d[lc] = happy - ignore
        if d:
            assignments[i] = min(d, key = d.get)
        else:
            return 0
    return assignments


# In[10]:


# Snippet to validate all possible schedules. They ALL work wtf

# for i in max_schedule:
#     print(validate(i))


# Now to start greedyfilling consultants

# In[11]:


def fillclass(schedule):
    # Going to need to flatten the classes (will be list of cons)
    flatten = lambda l: [item for sublist in l for item in sublist]
    assignments = {}
    for i in schedule:
        d = {}
        for c in c_avail:
            if c in flatten(assignments.values()):
                pass
            else:
                # values we have to ignore
                ignore = set(i).union(set(assignments.keys()))
                # intersect C availabilities with schedule
                happy = set(c_avail[c]).intersection(schedule)
                d[c] = happy - ignore
        if len(d) >= 10:
            # first make a list of the 10 consultants we want to take
            # this is done by finding the smallest and popping from d 10x
            l = []
            for j in range(10):
                l.append(min(d, key = d.get))
                del d[min(d, key = d.get)]
            assignments[i] = l
        else:
            return 0
    return assignments


# In[12]:


# All classes can be greedyfilled too wtf lol


# In[13]:


fillclass(max_schedule[0])


# In[14]:


validate(max_schedule[0])


# In[16]:


for i in max_schedule:
    if not fillclass(i):
        print(f"{i} doesn't work")

