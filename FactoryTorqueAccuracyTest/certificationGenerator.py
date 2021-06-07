"""
This is a script which is used to generate the factory accuracy certification.
"""

import pandas as pd
import time
import xlwings as xw

DIR = './certifications'

# dataframe = pd.read_excel('./test.xlsx')
dataframe = pd.DataFrame([[1, 2], [4, 5], [7, 8]],
     index=[7, 8, 9], columns=['max_speed', 'shield'])
print(dataframe)

print(dataframe)

