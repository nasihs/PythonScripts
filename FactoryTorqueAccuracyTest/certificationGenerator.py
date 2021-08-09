"""
This is a script which is used to generate the factory accuracy certification.
此脚本用于生成扭矩扳手标定证书
使用方法：
1.
"""

import time
import os
import re
import xlwings as xw
import pandas as pd

SW_VERSION = '0.1.5'
DATE = '11-06-21'
ROOT_DIR = './'
TEMPLATE_DIR = './template.xlsx'
ACCURACY_DIR = './accuracy/'
CERTIFICATE_DIR = '\\certifications\\'

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
    def __init__(self, cer_no=2106001):
        self.file = None
        self.path = os.getcwd()
        self.date = None
        self.wb = None
        self.sheet = None
        self.dict = value_dict
        self.certificate_no = None
        self.curCertificateNo = None
        self.excels = None
        self.num_to_generate = None

        self.accuracy_path = None
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
        print('扭矩扳手出厂检测证书生成工具 ver:{}'.format(SW_VERSION))

    # 获取扭矩检测结果文件夹及证书起始编号
    def get_some_args(self):
        # self.accuracy_path = r'C:\Users\nasihs\Documents\PythonScripts\FactoryTorqueAccuracyTest\accuracy'
        # self.certificate_no = 2108001
        # self.date = date
        while not self.accuracy_path:
            print('请将扭矩精度检测结果文件夹拖放至此, 并按下回车确认:', end='')
            tmp_input = input()
            print('输入路径为:{}'.format(tmp_input))
            if os.path.exists(tmp_input):
                self.accuracy_path = tmp_input
            else:
                print('路径输入有误，请重新输入.')

        while not self.certificate_no:
            print('请输入起始证书编号:', end=' ')
            tmp_input = input()
            if len(tmp_input) == 7:
                print('起始证书编号为:{}'.format(tmp_input))
                self.certificate_no = int(tmp_input)
            else:
                print('证书编号输入有误，请重新输入.')

        while not self.date:
            print('请输入证书打印年月(例: 21年08月 -> 2108):'.format(date), end='')
            tmp_input = input()
            if len(tmp_input) == 4:
                if int(tmp_input[0:2]) in range(20, 60) and int(tmp_input[2:]) in range(1, 13):
                    self.date = tmp_input
                else:
                    print('日期输入有误.')
            else:
                print('请输入正确格式的年月.')

    # 读取扭矩检测结果文件夹
    def get_excel_list(self):
        print('读取扭矩检测结果...')
        try:
            self.excels = os.listdir(self.accuracy_path)
            # self.excels = os.listdir(self.path + ACCURACY_DIR)
            self.num_to_generate = len(self.excels)
            print('读取成功:\'{}\''.format(self.accuracy_path))
            return True
        except:
            self.num_to_generate = 0
            print('读取路径失败:\'{}\''.format(self.accuracy_path))
            return False

    def load_template(self, file_name):
        try:
            # self.file = 'template.xlsx'
            self.file = os.path.normpath(self.path + '\\' + 'template.xlsx')
            self.wb = xw.Book(self.file)
            self.sheet = self.wb.sheets[0]
            print('读取模板成功:\'{}\''.format(self.file))
            return True
        except:
            print('读取模板失败 文件不存在:\'{}\''.format(self.file))
            return False

    def load_accuracy_data(self, file):
        self.accuracy_df = pd.read_excel(file, index_col=0)
        print('load accuracy data.')

    def update_sheet(self, number):
        self.certificate_sheet.range(CER_NO).value = str(number)  # str(self.certificate_no + cnt)
        self.certificate_sheet.range(PRINTED_ON).value = self.date  # str(time.strftime("%d-%m-%Y", time.localtime()))
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
        app = xw.App(visible=False, add_book=False)  # 隐藏excel界面

        self.get_excel_list()
        if self.num_to_generate == 0:
            print('文件夹为空:\'{}\''.format(self.accuracy_path))
            return False

        if not os.path.exists(self.path + CERTIFICATE_DIR):
            print('证书路径不存在，创建文件夹\'{}\''.format(CERTIFICATE_DIR))
            os.mkdir(self.path + CERTIFICATE_DIR)

        print('准备生成证书, 共计数量:{}'.format(self.num_to_generate))
        for i in range(self.num_to_generate):
            file_name = self.excels[i]
            print(file_name)
            self.serial = pattern.match(file_name).group(0)
            self.capacity = int(pattern2.match(file_name).group(2)) * 10
            print('Count:{}, Serial No:{}, capacity:{}'.format(i, self.serial, self.capacity))

            self.load_accuracy_data(self.accuracy_path + '\\' + file_name)
            self.certificate_wb = xw.Book(self.path + '\\' + 'template.xlsx')
            self.certificate_sheet = self.certificate_wb.sheets[0]
            tmp_cer_no = self.certificate_no + i
            self.update_sheet(tmp_cer_no)
            self.certificate_wb.save(self.path + CERTIFICATE_DIR + str(tmp_cer_no) + '.xlsx')
            self.certificate_wb.close()
            print('Count {} finished.'.format(i))

        app.kill()
        print('生成证书完成, 位于: {}'.format(self.path + '\\certifications'))
        return True


if __name__ == '__main__':
    certificate = Certificate()
    certificate.get_some_args()
    if certificate.load_template('template.xlsx'):
        print('load template ok')
        certificate.generate()
        input('按下回车键退出.')
    else:
        print('load template failed, exist')
        input('按下回车键退出.')

