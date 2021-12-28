#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2021/12/24 14:03
# @Author  : nasihs
# @Site    : 
# @File    : CurveHandler.py
# @Software: PyCharm

import os
import pandas as pd
import matplotlib.pyplot as plt

CURVE_PATH = r'C:\Users\nasihs\Desktop\Res_test\SN-01002213001-curves-2021-12-25\s'


class CurveHandler:
    def __init__(self):
        self.curves = []
        self.curveNum = 0
        self.curvePath = None
        self.curveName = []

    def read_csv(self, path):
        return

    def read_xlsx(self, path):
        self.curvePath = path
        files = os.listdir(path)
        for file in files:
            self.curveNum += 1
            print("file name: {}".format(file))
            data = pd.read_excel(os.path.join(path, file))
            torque = data.iloc[1:, 0]
            angle = data.iloc[1:, 1]
            self.curves.append((torque, angle))
            self.curveName.append(file[13:16])

        return

    def draw(self):
        fig, ax = plt.subplots()
        ax.set_xlabel('Angle')
        ax.set_ylabel('Torque')
        i = 0
        for curve in self.curves:
            # print(y)
            # print(x)
            ax.plot(curve[0], curve[1], label=self.curveName[i])
            i += 1

        plt.title('15Nm H6 steel spacer')
        plt.legend()
        plt.grid()
        plt.show()
        return

    def fun(self):
        for curve in self.curves:
            # print(curve[1])
            offset = curve[1][1]

            for i in range(1, len(curve[1])):
                curve[1][i] -= offset


if __name__ == '__main__':
    ch = CurveHandler()
    ch.read_xlsx(CURVE_PATH)
    # ch.fun()
    ch.draw()