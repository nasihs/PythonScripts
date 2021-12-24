import struct
import socket
import matplotlib.pyplot as plt
import numpy as np
import threading

TORQUE_GAIN = 0.01
ANGLE_GAIN = 0.1
# SERVER_IP = '127.0.0.1'
SERVER_IP = '192.168.50.62'
SERVER_PORT = 8686
SUBSCRIBE_CURVE = '00207408001         \0'
SUBSCRIBE_SUCCESS = '002600050010        7408\x00'


def drawCurve(angle_data, torque_data):
    if len(torque_data) > 0 and len(angle_data) > 0:
        fig, ax = plt.subplots()
        ax.set_xlabel('time')
        ax.set_ylabel('test')
        time = np.arange(0, len(torque_data) * 4, 4)
        ax.plot(time, torque_data, '-r', label='T-time')
        ax.plot(time, angle_data, '-b', label='A-time')

        plt.legend()
        plt.grid()
        plt.show()


def decodeCurve(rawBytes):
    psetNum = int(rawBytes[6:9])
    torqueCoefficient = int(rawBytes[27:41])
    angleCoefficient = int(rawBytes[43:57])
    pointNum = int(rawBytes[59:63])
    NbTelegrams = int(rawBytes[65:67])
    IdTelegrams = int(rawBytes[69:71])
    print('PSetNum:{}, TorqueCoe:{}, AngleCoe:{}, PointNum:{}, {}/{}'.format(psetNum,
                                                                             torqueCoefficient,
                                                                             angleCoefficient,
                                                                             pointNum,
                                                                             IdTelegrams,
                                                                             NbTelegrams))
    rawCurvebytes = rawBytes[71:]
    cookedBytes = bytearray()
    writeOffset = 0
    i = 0
    while i < len(rawCurvebytes) - 1:
        print('i:{}'.format(i), end=' ')

        tmpInt = struct.unpack_from('B', rawCurvebytes, i)[0]
        if tmpInt != 0xFF:
            cookedBytes.append(tmpInt)
            writeOffset += 1
            i += 1
            continue

        if i + 1 == len(rawCurvebytes) - 1:
            cookedBytes.append(struct.unpack_from('B', rawCurvebytes, i)[0])
            writeOffset += 1
            break

        tmpInt = struct.unpack_from('B', rawCurvebytes, i + 1)[0]
        if tmpInt == 0xFF:
            cookedBytes.append(0xFF)
            writeOffset += 1
            i += 2
        elif tmpInt == 0xFE:
            cookedBytes.append(0x00)
            writeOffset += 1
            i += 2
        else:
            print('0xFF不能单独出现.Index:{}'.format(i))
            break

    print('')
    print(cookedBytes)
    print('writeOffset:{}'.format(writeOffset))
    if writeOffset % 6 != 0:
        print('convert failed.')

    output = bytearray()
    for i in range(writeOffset):
        tmp = struct.unpack_from('B', cookedBytes, i)[0]
        if tmp == 0x00:
            output.append(0xFF)
        else:
            output.append(tmp - 1)

    torque = []
    angle = []
    for j in range(0, writeOffset, 6):
        # tmp = cookedData[j:j+6]
        a = struct.unpack_from('<H', output, j)[0]
        b = struct.unpack_from('<I', output, j + 2)[0]
        torque.append(a * TORQUE_GAIN)
        angle.append((b * ANGLE_GAIN))

    print('Resolved pointNum:{}'.format(len(torque)))
    print('Torque:{}\nAngle:{}\n'.format(torque, angle))
    return torque, angle


def resolveHead(head):
    print('Head Received.')
    try:
        dataLen = int(head[0:4]) - 20
    except:
        print("Fail to resolve head.{}\n".format(head))
        return 0

    # dataLen = struct.unpack_from('<I', head, 0)
    print('{}\nCurveDataLen:{}'.format(head, dataLen))

    return dataLen


class OpCurveClient:
    def __init__(self, serverIp, serverPort):
        self.address = (serverIp, serverPort)
        self.rawBytes = bytearray()
        print('Connecting to server: {}:{}'.format(serverIp, serverPort))
        self.socket = socket.create_connection(self.address)
        if self.socket:
            print('Connected.')
        else:
            print('Connection timeout.')

    def subscribe(self):
        self.socket.send(SUBSCRIBE_CURVE.encode('utf-8'))
        receivedBytes = self.socket.recv(256)
        print('Received:{}'.format(receivedBytes))
        if receivedBytes.decode('utf-8') == SUBSCRIBE_SUCCESS:
            print('Subscribed.')
        else:
            print('Subscription failed')

    def recv(self):
        print('Ready to receive.')
        while True:
            headBytes = self.socket.recv(20)
            curveDataLen = resolveHead(headBytes)
            curveDataBytes = self.socket.recv(curveDataLen + 1)
            torqueData, angleData = decodeCurve(curveDataBytes)
            drawCurve(angleData, torqueData)


def main():
    client1 = OpCurveClient(SERVER_IP, SERVER_PORT)
    client1.subscribe()
    client1.recv()


if __name__ == '__main__':
    main()
