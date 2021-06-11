"""
This is a script which is used to generate the factory accuracy certification.
"""
# encoding: utf-8
import time
import os
import re
import xlwings as xw
import pandas as pd

DATE = '11-06-21'
ROOT_DIR = './'
TEMPLATE_DIR = './template.xlsx'
ACCURACY_DIR = './accuracy/'
CERTIFICATE_DIR = './certifications/'

certificate_no = 2106001
date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
product_code = '01040001'
model = 'Torque Wrench 400 WLAN'
serial_number = '01040202333'

CER_NO = 'A1'
PRINTED_ON = 'A2'
PRODUCT_CODE = 'C1'
MODEL = 'C2'
CAPACITY = 'C3'
SERIAL_NO = 'C4'
ACCURACY_DATA = 'B94'
TXT1 = 'B30'
TXT2 = 'B39'

value_dict = {'certificateNo': 2106001, 'date': '10-06-2021', 'productCode': '01040001', 'capacity': 'Torque Wrench 400 WLAN'}
pattern = re.compile(r'[0-9]+')
pattern2 = re.compile(r'([0-9]{2})([0-9]{3})(.*)')


class Certificate(object):
    def __init__(self, cer_no = 2106001):
        self.file = None
        self.wb = None
        self.sheet = None
        self.dict = value_dict
        self.certificate_no = 2106001  # input('请输入证书序列号:')
        self.curCertificateNo = None
        self.excels = None
        self.num_to_generate = None

        self.accuracy_wb = None
        self.accuracy_sheet = None
        self.tmp_accuracy_data = None
        self.certificate_wb = None
        self.certificate_sheet = None

        self.accuracy_df = None
        self.serial = None
        self.capacity = 0
        self.txt1 = None
        self.txt2 = None

    def get_excel_list(self):
        try:
            self.excels = os.listdir(ACCURACY_DIR)
            self.num_to_generate = len(self.excels)
            print(self.excels)
            # os.mkdir(CERTIFICATE_DIR)
            print('读取成功:\'{}\''.format(ACCURACY_DIR))
            return True
        except:
            print('读取路径失败:\'{}\''.format(ACCURACY_DIR))
            return False

    def load_template(self, file_name):
        try:
            self.file = ROOT_DIR + file_name
            self.wb = xw.Book(file_name)
            self.sheet = self.workbook.sheets[0]
            print('读取模板成功:\'{}\''.format(self.file))
            return True
        except:
            print('路径不存在:\'{}\''.format(self.file))
            self.wb.close()
            return False

    def load_accuracy_data(self, file):
        self.accuracy_df = pd.read_excel(file, index_col=0)
        print('load accuracy data.')
        # print(self.accuracy_df)
        # self.tmp_accuracy_data
        # self.accuracy_wb = xw.Book(file)
        # self.accuracy_sheet = self.accuracy_wb.sheets[0]
        # self.tmp_accuracy_data = self.accuracy_sheet.range()

    # def update_dict(self, cnt, capacity, ):
    #     self.dict['certificateNo'] = self.curCertificateNo + cnt
    #     self.dict['date'] = str(time.strftime("%d-%m-%Y", time.localtime()))
    #     self.dict['productCode'] = f'010{capacity}001'.format(capacity=capacity)
    #     self.dict['capacity'] = 'Torque Wrench {} WLAN'.format(capacity)
    #     return

    def update_sheet(self, cnt):
        self.certificate_sheet.range(CER_NO).value = self.certificate_no + cnt
        self.certificate_sheet.range(PRINTED_ON).value = date  # str(time.strftime("%d-%m-%Y", time.localtime()))
        self.certificate_sheet.range(PRODUCT_CODE).value = '010{}001'.format(int(self.capacity/10))
        self.certificate_sheet.range(MODEL).value = 'Torque Wrench {} WLAN'.format(self.capacity)
        self.certificate_sheet.range(CAPACITY).value = '{} N·m'.format(self.capacity)
        self.certificate_sheet.range(SERIAL_NO).value = self.serial
        self.certificate_sheet.range(ACCURACY_DATA).value = self.accuracy_df
        self.certificate_sheet.range('D16').api.NumberFormat = "dd-mm-yy"
        self.certificate_sheet.range('B63').api.NumberFormat = "dd-mm-yy"
        self.certificate_sheet.range('D82').api.NumberFormat = "dd-mm-yy"
        self.certificate_sheet.range('B63').api.NumberFormat = "dd-mm-yy"

        print('new sheet updated.')

    def generate(self):
        app = xw.App(visible=False)

        self.get_excel_list()
        if self.num_to_generate == 0:
            print('文件夹为空:\'{}\''.format(ACCURACY_DIR))
            return False

        print('准备生成证书, 共{}:'.format(self.num_to_generate))
        for i in range(self.num_to_generate):
            file_name = self.excels[i]
            print(file_name)
            self.serial = pattern.match(file_name).group(0)
            self.capacity = int(pattern2.match(file_name).group(2)) * 10
            print('Count:{}, Serial No:{}, capacity:{}'.format(i, self.serial, self.capacity))

            self.load_accuracy_data(ACCURACY_DIR + file_name)
            self.certificate_wb = xw.Book(TEMPLATE_DIR)
            # self.certificate_wb.sheets[0] = self.sheet
            self.certificate_sheet = self.certificate_wb.sheets[0]
            self.update_sheet(i)
            self.certificate_wb.save(CERTIFICATE_DIR + str(self.certificate_no+i))
            self.certificate_wb.close()
            print('Count {} finished.'.format(i))
            # self.update_dict(i, capacity)

        app.kill()
        print('生成证书完成.')
        return True


if __name__ == '__main__':
    certificate = Certificate()
    certificate.load_template(TEMPLATE_DIR)
    certificate.generate()
    # certificate.load_accuracy_data('./accuracy/01040202001+2021-06-10-095445.xlsx')

# dataframe = pd.read_excel('./test.xlsx')
# dataframe = pd.DataFrame([[1, 2], [4, 5], [7, 8]],
#      index=[7, 8, 9], columns=['max_speed', 'shield'])
# print(dataframe)
#
# print(dataframe)

