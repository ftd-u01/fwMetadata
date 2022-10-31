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

    sessions = sub.sessions()
    
    for ses in sessions:
        acq = ses.acquisitions()[0].reload()

        acq_found_dicom = False
        sop = None
        for f in acq.files:
            if f.type != 'dicom':
                continue
            file_info = f.info
            try:
                sop = f.info['SOPInstanceUID']
            except KeyError:
                all_info[ses.id] = [ses.subject.label, ses.label, 'NA']
            continue 
        
        if sop is not None:
            tokens = sop.split('.')
            serial = tokens[8]
            all_info[ses.id] = [ses.subject.label, ses.label, serial]


df = pd.DataFrame.from_dict(all_info, orient='index').reset_index()
df.columns=['SessionID', 'SubjectLabel', 'SessionLabel', 'DeviceSerialNumber']

# Export dataframe to csv
filename = f'HCPDeviceSerials.csv'
df.to_csv(filename,index=False)
