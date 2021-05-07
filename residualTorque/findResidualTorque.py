# -*- coding: utf-8 -*-
# @Time    : 2021/2/22
# @Author  : nasihs
# @File    : find_residual_torque.py

"""
提高数据发送速率 100Hz->1kHz
接收曲线时只绘制T-A图
"""

import os
import math
import pandas as pd
import matplotlib.pyplot as plt
import serial
import time
from datetime import datetime


folder_to_save = './curves_3-5/'
time_format = '%Y-%m-%d_%H-%M-%S'
br = 115200


def solve_diff(x_data, y_data):  # 计算差分
    if len(x_data) != len(y_data):
        print('length is not equal.')
        return None
    y_data_d = []
    for i in range(1, len(x_data)):
        dx = x_data[i] - x_data[i - 1]
        dy = y_data[i] - y_data[i - 1]
        if dx == 0:
            dx = 0.01
        y_data_d.append(dy / dx)
    y_data_d.insert(0, y_data_d[0])
    return y_data_d


def leastSq(x, y):
    meanX = sum(x) / len(x)   # 求x的平均值
    meanY = sum(y) / len(y)   # 求y的平均值
    xSum = 0.0
    ySum = 0.0

    for i in range(len(x)):
        xSum += (x[i] - meanX) * (y[i] - meanY)
        ySum += (x[i] - meanX) ** 2
        if ySum == 0:
            ySum = 0.1
    k = xSum / ySum
    b = meanY - k * meanX
    return k, b   # 返回拟合的两个参数值


def solve_leastSq(x_data, y_data):
    """
    计算最小二乘
    """
    if len(x_data) != len(y_data):
        print('length is not equal.')
        return None
    y_data_lsq = []

    for i in range(0, len(x_data) - 2):
        x_data_tmp = x_data[i:i+3]
        y_data_tmp = y_data[i:i+3]
        # print(x_data_tmp, i)
        k, b = leastSq(x_data_tmp, y_data_tmp)
        y_data_lsq.append(k)
    y_data_lsq.insert(0, y_data_lsq[0])
    y_data_lsq.insert(0, y_data_lsq[0])
    # y_data_lsq.insert(0, y_data_lsq[0])
    return y_data_lsq


def find_residual_torque_point_mean(x_list=[], y_list=[], path='', window=3, show_curve=True):
    if not x_list == []:
        x_data = x_list
        y_data = y_list
    elif path != '':
        data = pd.read_csv(path)
        x_data = data['angle'].tolist()
        y_data = data['torque'].tolist()
    else:
        print('please input a curve.')

    k_diffMax = 0
    k_mean_data = []
    k_mean_diff = []
    k_mean_diff2 = []
    k_diffMax_index = -1
    k_former_sum = 0
    k_latter_sum = 0

    for i in range(4, len(x_data) - 4):
        for j in range(3):
            k_former_sum = 0
            k_latter_sum = 0  # 清零
            tmpX_former = x_data[i-4+j:i]
            tmpY_former = y_data[i-4+j:i]
            k_former, b_former = leastSq(tmpX_former, tmpY_former)
            k_former_sum += k_former * math.pow(4-j, 2)

            tmpX_latter = x_data[i+1:i+5-j]
            tmpY_latter = y_data[i+1:i+5-j]
            k_latter, b_latter = leastSq(tmpX_latter, tmpY_latter)
            k_latter_sum += k_latter * math.pow(4-j, 2)
            # print('k former:{}, k latter:{}, {}'.format(k_former, k_latter, j))
            # print('former sum:{}, latter sum:{}'.format(k_former_sum, k_latter_sum))

        k_former_mean = k_former_sum / 29.0
        k_latter_mean = k_latter_sum / 29.0
        # print('former_mean:{}, latter_mean{}, i:{}'.format(k_former_mean, k_latter_mean, i))

        k_mean_data.append(k_former_mean)
        # tmp_k_diff = k_former_mean - k_latter_mean
        tmp_k_diff = (k_former_mean - k_latter_mean)
        if tmp_k_diff > k_diffMax:
            k_diffMax = tmp_k_diff
            k_diffMax_index = i
            print('k_former_mean:{}, k_latter_mean:{}, diff:{}'.format(k_former_mean, k_latter_mean, k_diffMax))

    if len(k_mean_data) > 0:
        for i in range(4):
            k_mean_data.insert(0, k_mean_data[0])
        for i in range(4):
            k_mean_data.append(k_mean_data[-1])

    print('len of k_data={}'.format(len(k_mean_data)))
    if k_diffMax_index == -1:
        print('@@@ searching failed.')
        return 0, 0, k_mean_data
    else:
        print('@@@ searching completed. k_diffMax_index:{}'.format(k_diffMax_index))
        return x_data[k_diffMax_index], y_data[k_diffMax_index], k_mean_data


def getKey(dic, value):
    return [k for k, v in dic.items() if v == value]


def calWeightedK(x, y):
    k_sum = 0
    for i in range(3):
        tmpX = x[0:i+2]
        tmpY = y[0:i+2]
        tmpK, b = leastSq(tmpX, tmpY)
        k_sum += (tmpK * math.pow(i+2, 2))
    return k_sum / 29.0


def calWeightedKList(x_data, y_data):
    k_list = []
    for i in range(len(x_data)-3):
        x = x_data[i:i+4]
        y = y_data[i:i+4]
        k_list.append(calWeightedK(x, y))

    k_list.insert(0, k_list[0])
    k_list.insert(0, k_list[0])
    k_list.append(k_list[-1])
    return k_list


def calMoveAverageK(x, y):
    k = (y[-1] - y[0]) / (x[-1] - x[0])
    return k


def findResidualTorque(x_list=[], y_list=[], path=''):
    if not x_list == []:
        x_data = x_list
        y_data = y_list
    elif path != '':
        data = pd.read_csv(path)
        x_data = data['angle'].tolist()
        y_data = data['torque'].tolist()
    else:
        print('please input a curve.')

    kMax = 0
    kMin = 100

    # kLast = calWeightedK(x_data[0:4], y_data[0:4])
    kLast = calMoveAverageK(x_data[0:4], y_data[0:4])

    kDiff = 0
    k_mean_data = []

    K_ZERO = 4.0
    K_ZERO_LEFT = -100.0
    K_MAX = 1000.0
    K_MIN = 15.0
    K_DIFF = 1.0
    SOFT_ANGLE = 4.0
    MAX_ANGLE = 30.0
    SOFT_THRESHOLD = 3.0
    HARD_THRESHOLD = 0.8  # 找到分离点后 硬连接应在1°以内找到残余扭矩点， 若找不到则把分离点作为残余扭矩点
    BREAK_THRESHOLD = 0.5

    fsm_state = 0
    find_success = False
    joint_type = 0
    start_angle = x_data[0]
    print('start angle:{}'.format(start_angle))
    type_map = {'HARD': 0, 'SOFT': 1, 'SOFTER': 2, 'Ultra_SOFT': 3}
    state = {'START': 0, 'IN_HARD': 1, 'IN_SOFT': 2, 'OUT_HARD_1': 3, 'OUT_HARD_2': 4, 'END': 5}
    break_index = 0
    residual_index = 0
    soft2hard_cnt = 0

    nFlag = 0

    for i in range(1, len(x_data)-3):
        tmp_x = x_data[i:i+4]
        tmp_y = y_data[i:i+4]

        # kCurrent = calWeightedK(tmp_x, tmp_y)
        kCurrent = calMoveAverageK(tmp_x, tmp_y)

        k_mean_data.append(kCurrent)
        cur_angle = x_data[i] - start_angle
        kDiff = kCurrent - kLast
        print('curK:{}, curKDiff:{}, absAngle:{}, dAngle:{}'.format(kCurrent, kDiff, x_data[i], cur_angle))
        print(getKey(state, fsm_state))
        if fsm_state == state['START']:  # START
            if K_MIN <= kCurrent <= K_MAX:
                fsm_state = state['IN_HARD']
            elif K_ZERO <= kCurrent < K_MIN:
                fsm_state = state['IN_SOFT']
            else:
                find_success = False
                fsm_state = state['END']
                print('k > K_MAX.')
        elif fsm_state == state['IN_HARD']:  # IN_HARD
            if kCurrent > kMax:
                kMax = kCurrent
            elif kCurrent < kMin:
                kMin = kCurrent

            if cur_angle > MAX_ANGLE:
                find_success = False
                fsm_state = state['END']
                print('Angle overflow.')
            elif kCurrent < K_MIN:
                fsm_state = state['OUT_HARD_1']
            elif kCurrent < K_ZERO_LEFT or kCurrent > K_MAX:
                find_success = False
                fsm_state = state['END']
                print('k < K_ZERO_LEFT.')
        elif fsm_state == state['OUT_HARD_1']:  # OUT_HARD_1
            if cur_angle > SOFT_ANGLE:  # 软连接
                residual_index = break_index = i
                find_success = True
                joint_type = type_map['SOFT']
                fsm_state = state['END']
                print('Break & Residual found.')
            elif kCurrent <= K_ZERO and cur_angle > BREAK_THRESHOLD:  # 增加角度判定，过小则重找
                break_index = i
                breakAngle = cur_angle
                fsm_state = state['OUT_HARD_2']
                if kCurrent < 0:
                    nFlag = 1
                print('Break point found.')
            elif kCurrent > K_MAX:
                find_success = False
                fsm_state = state['END']
                print('k > K_MAX.')
        elif fsm_state == state['OUT_HARD_2']:  # OUT_HARD_2
            # print(cur_angle)
            if nFlag == 0:
                if kCurrent < 0.0:
                    nFlag = 1
            if cur_angle > MAX_ANGLE and nFlag == 1:
                find_success = False
                fsm_state = state['END']
                print('Angle overflow.')
            elif cur_angle - breakAngle > HARD_THRESHOLD and nFlag == 0:
                # 找到分离点后，一定角度内没有找到残余扭矩且无极小值特征（下降再上升）
                # 对于./curves_3-5_new\curves_3-52021-03-05_19-11-25418_new.csv新增的条件
                residual_index = break_index
                find_success = True
                joint_type = type_map['SOFTER']
                fsm_state = state['END']
                print('Residual found.')
            elif kCurrent > K_ZERO and nFlag == 1:
                # elif kLast <= -K_ZERO and kCurrent > K_ZERO and nFlag == 1:  # and kDiff >= K_DIFF:  # 硬连接
                residual_index = i
                print('Residual point found.')
                find_success = True
                joint_type = type_map['HARD']
                fsm_state = state['END']
            elif cur_angle > SOFT_ANGLE and nFlag == 0:  # 软连接
                residual_index = break_index
                find_success = True
                joint_type = type_map['SOFTER']
                fsm_state = state['END']
                print('Break & Residual found.')
        elif fsm_state == state['IN_SOFT']:  # IN_SOFT
            if cur_angle > SOFT_ANGLE:  # 更软的连接
                residual_index = break_index = i
                find_success = True
                joint_type = type_map['Ultra_SOFT']
                fsm_state = state['END']
                print('Break & Residual found.(ultra soft')
            elif K_MIN <= kCurrent <= K_MAX:
                soft2hard_cnt += 1
                if soft2hard_cnt >= 1 and kLast < K_MIN:
                    soft2hard_cnt = 1
                if soft2hard_cnt >= SOFT_THRESHOLD:
                    fsm_state = state['IN_HARD']
            elif kCurrent < K_ZERO_LEFT:
                find_success = False
                fsm_state = state['END']
                print('k < -K_ZERO.')
        elif fsm_state == state['END']:
            if find_success:
                # 需要加上判断  若残余扭矩大于break点 则判定失败
                print('type:{}, break point:{}, residual point:{}'.format(
                    getKey(type_map, joint_type), y_data[break_index], y_data[residual_index]))
            else:
                print('failed.')
            break
        kLast = kCurrent

    print('max k:{}, min k:{}\n=========================='.format(kMax, kMin))
    return find_success, (x_data[break_index], y_data[break_index]), (x_data[residual_index], y_data[residual_index])


def recv_and_save(ser):
    torque_data = []
    angle_data = []
    lastAngle = 0
    count = 0
    fail_count = 0

    print('ready.')
    while True:
        ser.write(b'a')
        raw_data = ser.readline().decode(encoding='utf-8')
        # print(raw_data)
        if raw_data != '':
            print('start.')
            index = raw_data.find('torque')
            index2 = raw_data.find('angle')
            if index != -1 and index2 != -1:
                start_angle = float(raw_data[index2 + 6:index2 + 11])
            break
        time.sleep(0.1)

    while True:  # i in range(200):
        # format: torque:100.2, angle:10.3
        ser.write(b'ok')
        raw_data = ser.readline().decode(encoding='utf-8')
        # print('raw data:{}'.format(raw_data))
        if raw_data != '':
            index = raw_data.find('torque')
            index2 = raw_data.find('angle')
            if index != -1 and index2 != -1:
                try:
                    torque = float(raw_data[index + 7:index + 12])
                    angle = float(raw_data[index2 + 6:index2 + 11])
                    print('resolve: T={}, A={}, cnt={}'.format(torque, angle, count))
                except:
                    pass
                cur_angle = angle - start_angle
                if cur_angle > lastAngle+0.01:
                    torque_data.append(torque)
                    angle_data.append(cur_angle)
                    lastAngle = cur_angle
                    count += 1
            elif raw_data.find('stop') != -1:
                print('stop.')
                break
            time.sleep(0.001)
        else:
            fail_count += 1
            if fail_count >= 10:
                print('timeout.')
                break

    df = pd.DataFrame({'angle': angle_data, 'torque': torque_data})
    save_dir = folder_to_save + str(datetime.now().strftime(time_format)) + '.csv'
    if not os.path.exists(folder_to_save):
        os.mkdir(folder_to_save)
    df.to_csv(save_dir)
    print('curve saved. filename:{}'.format(save_dir))
    return angle_data, torque_data


def draw_and_annotate(angle_data, torque_data, lsq_data, k_mean_data, cord_x, cord_y):
    if len(torque_data) > 0 and len(angle_data) > 0:
        fig, ax = plt.subplots()
        ax.set_xlabel('Angle')
        ax.set_ylabel('Torque')
        ax.plot(angle_data, torque_data, '-ro', label='T-A')

        if lsq_data:
            ax.plot(angle_data, lsq_data, '-g', label='lsq')
        if k_mean_data:
            ax.plot(angle_data, k_mean_data, '-b', label='k_mean')

        plt.legend()
        plt.grid()
        plt.show()
        print('finish.\n==============')
    else:
        print('no curve.')
        print('finish.\n==============')


def draw_and_find(path):
    print(path)
    data = pd.read_csv(path)
    angleData = data['angle'].tolist()  # 转换为python列表
    torqueData = data['torque'].tolist()
    diffMax = 0
    fig1, ax1 = plt.subplots()
    ax1.set_xlabel('Angle')
    ax1.set_ylabel('Torque')

    # diffData = solve_diff(angleData, torqueData)
    # lsqData = solve_leastSq(angleData, torqueData)
    weightedData = calWeightedKList(angleData, torqueData)
    success, breakPoint, residualPoint = findResidualTorque(angleData, torqueData)
    # xi, yi, kList = find_residual_torque_point_mean(angleData, torqueData)

    ax1.plot(angleData, torqueData, '-ro', label='T-A')
    # ax1.plot(angleData, diffData, '-b', label='dT/dA - A')
    ax1.plot(angleData, weightedData, '-b', label='weighted k')
    # ax1.plot(angleData, k_mean_data, '-y', label='k_mean')

    plt.plot(residualPoint[0], residualPoint[1], '-g', marker='x', markersize=12)  # 残余扭矩黄色
    plt.plot(breakPoint[0], breakPoint[1], '-b', marker='1', markersize=12)  # 分离点蓝色
    plt.title(path + '         residual:' + str(residualPoint[1]))
    plt.legend()
    plt.grid()
    plt.show()


def deal_data(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            fullName = os.path.join(directory, file)
            print(fullName)
            data = pd.read_csv(fullName)
            x = data['angle'].tolist()
            y = data['torque'].tolist()
            if len(x) < 10:
                continue
            x_new = []
            y_new = []
            for i in range(len(x)-1):
                print(i)
                if i == 0:
                    x_new.append(x[0])
                    y_new.append(y[0])
                if i >= 1:
                    if x[i] > x_new[-1]:
                        x_new.append(x[i])
                        y_new.append(y[i])
            data_new = pd.DataFrame({'angle': x_new, 'torque': y_new})
            save_dir = str(datetime.now().strftime(time_format)) + '{}_new.csv'.format(i)
            if not os.path.exists(directory):
                os.mkdir(directory)
            data_new.to_csv(save_dir)
            print('curve saved. filename:{}'.format(save_dir))
    print('Done.')


def draw_all_csv(directory):
    if not os.path.exists(directory):
        print('directory does not exist.')
        return
    for root, dirs, files in os.walk(directory):
        for file in files:
            fullName = os.path.join(directory, file)
            draw_and_find(fullName)
    print('Done.')


def main(port):
    with serial.Serial(port, baudrate=br, timeout=0.1) as s:
        if s.is_open:
            print('{} opened, baudrate:{}, timeout:{}'.format(port, br, 0.1))
            for i in range(1, 10):
                print('tightening count:{}'.format(i))
                angleData, torqueData = recv_and_save(s)
                resX, resY, k_list = find_residual_torque_point_mean(angleData, torqueData)
                draw_and_annotate(angleData, torqueData, k_list, resX, resY)
        else:
            print('Failed to open {}'.format(port))


if __name__ == '__main__':
    # draw_and_find('./../curve22.csv')
    # draw_and_find('./curves_3-5_new\curves_3-52021-03-05_19-11-25217_new.csv')
    # draw_and_find('./curves_3-5_new\curves_3-52021-03-05_19-11-25367_new.csv')
    # draw_all_csv('./curves_2-23')
    draw_all_csv('./curves_3-5_new')
    # draw_all_csv('./curves_2020-2-22')

    # main('COM4')

    # deal_data('./curves_3-5')



