#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2021/8/16 14:10
# @Author  : nasihs
# @Site    : 
# @File    : test.py
# @Software: PyCharm

import matplotlib.pyplot as plt


# str1 = '00207408001         \0'
# print(str1)
# bytes1 = str1.encode(encoding= 'utf-8')
# bytes1_str = str(bytes1)
# bytes2 = bytes.fromhex('31 32 33 20 00')
# print(bytes1)
# print(bytes1_str)
# print(bytes2)
# print(str(bytes2))

bytes1 = bytes.fromhex('31 32 33 20 00')
bytes1_str = str(bytes1)
print('bytes1:{0}, bytes1[0]:{0[1]}\nbytes_str:{1}, bytes_str[0]:{1[1]}'.format(bytes1, bytes1_str))
print(bytes1.decode('utf-8'))