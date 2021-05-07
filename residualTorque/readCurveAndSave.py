import os
import numpy as np
import sympy
import pandas as pd
import matplotlib.pyplot as plt
import serial
import time
from datetime import datetime

save_path = './csv/'
time_format = '%Y-%m-%d_%H-%M-%S'
br = 115200


def solve_diff(x_data, y_data):
    if len(x_data) != len(y_data):
        print('length is not equal.')
        return None
    y_data_d = []
    for i in range(1, len(x_data)):
        dx = x_data[i] - x_data[i - 1]
        dy = y_data[i] - y_data[i - 1]
        if dx == 0:
            y_data_d.append(0.0)
        else:
            y_data_d.append(dy / dx)
    y_data_d.insert(0, y_data_d[0])
    return y_data_d


def recv_and_draw(com):
    print(os.path.basename(__file__))
    print('Baudrate: {}'.format(br))
    with serial.Serial(com, baudrate=br, timeout=0.1) as ser:
        if ser.is_open:
            print('{} opened'.format(com))

            torqueData = []
            angleData = []
            lastAngle = 0
            count = 0
            fail_count = 0

            # while True:
            #     raw_data = ser.readline().decode(encoding='utf-8')
            #     index = raw_data.find('start')
            #     if index != -1:
            #         print('start.')
            #         break

            while True:
                # format: torque:100.2, angle:010.3
                ser.write(b'ok')
                raw_data = ser.readline().decode(encoding='utf-8')
                print('raw data:{}'.format(raw_data))
                if raw_data != '':
                    index = raw_data.find('torque')
                    index2 = raw_data.find('angle')
                    if index != -1:
                        torque = float(raw_data[index + 7:index + 12])
                        angle = float(raw_data[index2 + 6:index2 + 11])
                        print('resolve: T={}, A={}, cnt={}'.format(torque, angle, count))
                        if angle > lastAngle:
                            torqueData.append(torque)
                            angleData.append(angle)
                            lastAngle = angle
                            count += 1
                    elif raw_data.find('stop') != -1:
                        print('stop.')
                        break
                    time.sleep(0.01)
                else:
                    fail_count += 1
                    if fail_count >= 20:
                        print('timeout.')
                        break
        else:
            print('Failed to open {}'.format(com))

    if len(torqueData) > 0:
        print('torqueData len={}'.format(len(torqueData)))
        print('angleData len={}'.format(len(angleData)))

        diffData = solve_diff(angleData, torqueData)
        df = pd.DataFrame({'angle': angleData, 'torque': torqueData, 'diff': diffData})
        save_path = './curves/' + str(datetime.now().strftime(time_format)) + '.csv'
        df.to_csv(save_path)
        print('curve saved.')

        fig, ax = plt.subplots()
        ax.set_xlabel('Angle')
        ax.set_ylabel('Torque')
        ax.plot(angleData, torqueData, '-r', label='T-A')
        plt.legend()
        plt.grid()
        # plt.show()
        plt.ion()
        plt.pause(5)
        plt.close()
    else:
        print('no curve.')


if __name__ == "__main__":
    recv_and_draw('COM4')