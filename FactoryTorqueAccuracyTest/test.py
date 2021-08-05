import pandas as pd
import time
import os
import re
import xlwings as xw

ROOT_DIR = './'
ACCURACY_DIR = './accuracy'
CERTIFICATE_DIR = './certifications'

certificate_no = 2106001
date = '10-06-2021'
product_code = '01040001'
model = 'Torque Wrench 400 WLAN'
serial_number = '01040202333'

CER_NO = 'A1'
PRINTED_ON = 'A2'
PRODUCT_CODE = 'C1'
MODEL = 'C2'
CAPACITY = 'C3'
SERIAL_NO = 'C4'

# wb = xw.Book()
# sheet = wb.sheets[0]
# df = pd.read_excel('./accuracy/01040202001+2021-06-10-095445.xlsx', index_col = 0)
# sheet.range('A1').value = df
# print(sheet.range('A1').value)
# wb.save()
# wb.close()

print('hello' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
capacity = 400
print(f'010{capacity}001'.format(capacity=capacity/10))
print('Torque Wrench {} WLAN'.format(capacity))
print(str(time.strftime("%d-%m-%Y", time.localtime())))
# workbook = xw.Book(ROOT_DIR + 'template.xlsx')
# sheet = workbook.sheets[0]
# print('Certificate No:{0}\nProduct Code:{1}'.format(int(sheet.range(CER_NO).value), sheet.range(PRODUCT_CODE).value))
# sheet.range(SERIAL_NO).value = serial_number
# workbook.save()
# workbook.close()

