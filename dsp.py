import os, os.path
import numpy as np
import pandas as pd

dataPath = os.getcwd() + '/data/'

caseCount = len(os.listdir(dataPath))

data = []

for filename in os.listdir(dataPath):
    print(filename)
    f = open(os.path.join(dataPath, filename), encoding='utf-8')
    data.append([filename.replace('.txt', ''), f.read()])

verdict_df = pd.DataFrame(data, columns=['Case ID', 'Case Text'])

cases_df = pd.read_csv('./cases.csv', usecols = ['GerechtelijkProductType', 'Case ID', 'Proceduresoorten', 'Publicatiedatum', 'Rechtsgebieden', 'Tekstfragment', 'Titel', 'Uitspraakdatum', 'UitspraakdatumType'])

merged_df = cases_df.join(verdict_df.set_index('Case ID'), on='Case ID', how='left')


print(merged_df)


