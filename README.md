# Consultant scheduler
This is a script to create a schedule matching classes with consultants (or interviewers with interviewees) given an input of schedules.

# Installation
```bash
python3 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python3 script.py
```

# Why does this exist?
UMCG is a student-run society at UNSW aimed at developing consultant-relevant skills for its members. It does this through student-led classes where we provide structured workshops, case studies, and exercises for students to learn about the creative and analytical skills and problem solving relevant to a management consultant.

One pain point I found in my time working with and managing some of these classes was choosing suitable times for classes, as well as matching lead consultants to students at times that worked for everyone. At the time, this was done manually by one of our student leaders 3 times a year. It was reported this took almost half a day each time. 

This program takes the availabilities of the students and lead consultants and returns a list of classes including class times, lead consultants, and students, automating the process. This is currently done greedily and seems to be enough for this project.

This has also been used to schedule interviews, which has a similar problem of matching leaders with potential consultants.
