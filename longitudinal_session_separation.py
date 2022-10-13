import flywheel
import os
import sys
import pandas as pd
import numpy as np
import argparse

from datetime import timedelta
from datetime import date

fw = flywheel.Client()
project = fw.lookup('pennftdcenter/HCPMultiCenter')

all_subjects = None

if (len(sys.argv) < 2):
    print('Querying all subjects')
    all_subjects = project.subjects()
else:
    try:
        subject_path = 'pennftdcenter/HCPMultiCenter/{}'.format(sys.argv[1])
        all_subjects = [ fw.lookup(subject_path) ]
    except flywheel.rest.ApiException as e:
        print('Could not find subject at {}'.format(subject_path))
        exit(1)

all_info = dict()

for sub in all_subjects:

    study_dates = list()

    sub_id = sub.id
    sub_label = sub.label
    sessions = sub.sessions()

    if (len(sessions) < 2):
        continue

    for ses in sessions:
        study_dates.append(ses.timestamp)

    study_dates.sort()

    mr2_time_delta = (study_dates[1] - study_dates[0])

    all_info[sub_id] = [sub_label, 0, round(mr2_time_delta.days / 30)]

    if len(study_dates) > 2:
        mr3_time_delta = study_dates[2] - study_dates[0]
        all_info[sub_id].append(round(mr3_time_delta.days / 30))
    else:
        all_info[sub_id].append('NA')

df = pd.DataFrame.from_dict(all_info, orient='index').reset_index()
df.columns=['SubjectID', 'SubjectLabel', 'MR1_MonthsSinceBaseline', 'MR2_MonthsSinceBaseline', 'MR3_MonthsSinceBaseline']

# Export dataframe to csv
filename = f'HCPLongitudinalTimeCourse.csv'
df.to_csv(filename,index=False)
