import pandas as pd
import struct
import socket
import threading

TORQUE_GAIN = 0.01
ANGLE_GAIN = 0.1
# SERVER_IP = '127.0.0.1'
SERVER_IP = '192.168.1.18'
SERVER_PORT = 8686
SUBSCRIBE_CURVE = '00207408001         \0'
SUBSCRIBE_SUCCESS = '002600040010        740800\0'


def decodeCurve(rawBytes):
    psetNum = int(rawBytes[6:9])
    torqueCoefficient = int(rawBytes[27:41])
    angleCoefficient = int(rawBytes[43:57])
    pointNum = int(rawBytes[59:63])
    print('PSetNum:{}, TorqueCoe:{}, AngleCoe:{}, PointNum:{}'.format(psetNum,
                                                                      torqueCoefficient,
                                                                      angleCoefficient,
                                                                      pointNum))
    rawCurvebytes = rawBytes[71:]
    cookedBytes = bytearray()
    writeOffset = 0
    i = 0
    while i < len(rawCurvebytes):
        print('i:{}'.format(i), end=' ')

        tmpInt = struct.unpack_from('B', rawCurvebytes, i)[0]
        if tmpInt != 0xFF:
            cookedBytes.append(tmpInt)
            writeOffset += 1
            i += 1
            continue

        if i + 1 == len(rawCurvebytes):
            cookedBytes.append(struct.unpack_from('B', rawCurvebytes, i)[0])
            writeOffset += 1
            break

        tmpInt = struct.unpack_from('B', rawCurvebytes, i+1)[0]
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
        b = struct.unpack_from('<I', output, j+2)[0]
        torque.append(a*TORQUE_GAIN)
        angle.append((b*ANGLE_GAIN))

    print('Resolved pointNum:{}'.format(len(torque)))
    print('Torque:{}\nAngle:{}\n'.format(torque, angle))
    return torque, angle


def resolveHead(head):
    print('Head Received.')
    dataLen = int(head[0:4]) - 20
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
        print('Start.')
        while True:
            headBytes = self.socket.recv(20)
            curveDataLen = resolveHead(headBytes)
            curveDataBytes = self.socket.recv(curveDataLen)
            decodeCurve(curveDataBytes)


def curveDataDecoding(rawData):
    torque = []
    angle = []

    cookedData = bytearray()
    writeOffset = 0
    i = 0
    while i < len(rawData):
        print('i:{}'.format(i), end=' ')
        if rawData[i] != 'FF':
            cookedData.append(int(rawData[i], 16))
            writeOffset += 1
            i += 1
            continue

        if i+1 == len(rawData):
            cookedData.append(int(rawData[i], 16))
            writeOffset += 1
            break

        if rawData[i+1] == 'FF':
            cookedData.append(0xFF)
            writeOffset += 1
            i += 2
        elif rawData[i+1] == 'FE':
            cookedData.append(0x00)
            writeOffset += 1
            i += 2
        else:
            print('0xFF不能单独出现.')
            break

    print('')
    print(cookedData)
    print('writeOffset:{}'.format(writeOffset))
    if writeOffset % 6 != 0:
        print('convert failed.')

    output = bytearray()
    for i in range(writeOffset):
        tmp = struct.unpack_from('B', cookedData, i)[0]
        if tmp == 0x00:
            output.append(0xFF)
        else:
            output.append(tmp - 1)

    for j in range(0, writeOffset, 6):
        # tmp = cookedData[j:j+6]
        a = struct.unpack_from('<H', output, j)[0]
        b = struct.unpack_from('<I', output, j+2)[0]
        torque.append(a*TORQUE_GAIN)
        angle.append((b*ANGLE_GAIN))

    print('pointNum:{}'.format(len(torque)))
    return torque, angle


def main():
    with open("./testCurve7.txt", "r") as f:
        rawData = f.read().split(' ')
        print(rawData)
        torqueData, angleData = curveDataDecoding(rawData)

    print(torqueData)
    print(angleData)


def test3():
    output = bytearray()
    output.append(0x01)
    output.append(0x01)
    output.append(0x00)
    output.append(0x00)
    output.append(0x00)
    output.append(0x01)
    a = struct.unpack_from('>H', output, 0)[0]
    b = struct.unpack_from('>I', output, 0+2)[0]
    print('a:{}, b:{}'.format(a, b))


def main2():
    client1 = OpCurveClient(SERVER_IP, SERVER_PORT)
    client1.subscribe()
    client1.recv()


if __name__ == '__main__':
    # decodeCurve(b'01010200503')
    main2()
    # s = '0507111'
    b = b'07207010801r\x01\x01\x01\x01\x01{\x01\x01'
    #print(int(b[0:4]))
    # source = b'74FF'
    # print(len(source))
    # print('source:{}'.format(source))
    # test = source.decode()
    # print('test:{}'.format(test))
    # result = bytes.fromhex(test)
    # print(len(result))
    # print(result)
    # print(struct.unpack_from('B', result, 0))
    # print(struct.unpack_from('B', test, 0))
    # array = bytearray()
    # array.append(0x0F)
    # print(array)
    # print(struct.unpack_from('B', array, 0))
    # test3()
    # main()
    # print(b'00207408001         ')
    # s1 = b'0xFF'
    # s2 = b'FF'
    # s3 = 255
    # print('end.s')
