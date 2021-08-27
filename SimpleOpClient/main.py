#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# @Time    : 2021/8/25 10:14
# @Author  : nasihs
# @Site    : 
# @File    : main.py
# @Software: PyCharm

import socket
import time
import threading
import keyboard

SERVER_IP = '192.168.1.40'
SERVER_PORT = 8686
MID0060 = bytes.fromhex('30 30 32 30 30 30 36 30 30 30 31 30 20 20 20 20 30 31 20 20 00')
MID7408 = '00207408001         \0'.encode('utf-8')
MID0005 = '002600050010        7408\x00'.encode('utf-8')
MID0019 = bytes.fromhex('30 30 32 35 30 30 31 39 30 30 31 30 20 20 20 20 30 31 20 20 30 30 32 30 31 00')
MID0042 = bytes.fromhex('30 30 32 30 30 30 34 32 30 30 31 30 20 20 20 20 30 31 20 20 00')
MID0043 = bytes.fromhex('30 30 32 30 30 30 34 33 30 30 31 30 20 20 20 20 30 31 20 20 00')
MID9999 = bytes.fromhex('30 30 32 30 39 39 39 39 30 30 31 20 20 20 20 20 20 20 20 20 00')
REPLY_TIMEOUT = 3


class OpClient:
    def __init__(self, ip, port):
        self.address = (ip, port)
        self.socket = None
        self.connected = False
        self.state = {'0060': False, '7408': False, '0019': False,'0042': False, '0043': False, '0061': False}
        self.thread1 = None
        self.thread2 = None
        self.thread3 = None
        self.heart_send = 0
        self.heart_recv = 0

    def connect(self):
        # self.socket = socket.create_connection(self.address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to server {}...'.format(self.address))
        try:
            self.socket.connect(self.address)
        except TimeoutError:
            print('Fail to connect to {}'.format(self.address))
            self.socket.close()
            return False

        self.connected = True
        print('Success to connect to {}.'.format(self.address))
        return True

    def subscribe(self, mid_number):
        if not self.connected:
            print('Not connected, please connect to server first.')
            return

        if mid_number == '0060':
            self.socket.send(MID0060)
            print('Send:{}'.format(MID0060))
            received_bytes = self.socket.recv(256)
            print('Recv:{}'.format(received_bytes))
            if received_bytes[4:8] == b'0005':
                print('success to subscribe {}.'.format(mid_number))
            else:
                print(received_bytes[4:8])
        elif mid_number == '7408':
            self.socket.send(MID7408)
            print('Send:{}'.format(MID7408))
            received_bytes = self.socket.recv(256)
            print('Recv:{}'.format(received_bytes))
            if received_bytes[4:8] == '0005':
                print('success to subscribe {}.'.format(mid_number))
            else:
                print(received_bytes[4:8])
        else:
            print('Unknown mid number.')

        # time.sleep(3)
        # self.socket.close()
        # print('Socket closed bye.')

    def recv(self):
        print('Start thread1.')

        while self.connected:
            try:
                data_len_bytes = self.socket.recv(4)
                data_len = int(data_len_bytes)
                # print('Data len:{}'.format(data_len))
            except TimeoutError:
                print('Timeout Error.')
                self.socket.close()
                self.connected = False
                break

            data_bytes = self.socket.recv(data_len)
            mid = data_bytes[0:4].decode('utf-8')
            print('Recv:MID{}:{}'.format(mid, data_bytes))
            if mid == '0005':
                reply_of = data_bytes[-5:-1].decode('utf-8')
                if reply_of == '0043' or reply_of == '0042' or reply_of == '0019':
                    self.state[reply_of] = True
                else:
                    print(reply_of)
            elif mid == '0061':
                self.state['0061'] = True
            elif mid == '9999':
                pass
            elif mid == '7410':
                pass
            else:
                print('Failed to resolve:{}'.format(data_bytes))

        print('Thread1 stopped.')

    def heart_beat(self, interval):
        print('Start thread2.')
        while self.connected:
            self.socket.send(MID9999)
            time.sleep(interval)
        print('Thread2 stopped.')

    def wait_reply(self, mid_number):
        start_time_stamp = time.time()
        while not self.state[mid_number]:
            time.sleep(0.1)
            if time.time() - start_time_stamp > REPLY_TIMEOUT:
                # if mid_number == '0042':
                # print('Timeout.')
                # self.state[mid_number] = True
                if mid_number == '0043':
                    self.socket.send(MID0043)
                    print('Timeout, Resend:MID0043')
                elif mid_number == '0042':
                    self.socket.send(MID0042)
                    print('Timeout, Resend:MID0042')
                elif mid_number == '0019':
                    self.socket.send(MID0019)
                    print('Timeout, Resend:MID0019')
                start_time_stamp = time.time()
        self.state[mid_number] = False

    def task(self, repeat_time):
        print('Start thread3.')
        while repeat_time and self.connected:
            repeat_time -= 1
            self.socket.send(MID0043)
            print('Send:MID0043')
            self.wait_reply('0043')
            print('Unlocked.')
            self.socket.send(MID0019)
            print('Send:MID0019')
            self.wait_reply('0019')
            self.wait_reply('0061')
            self.socket.send(MID0042)
            print('Send:MID0042')
            self.wait_reply('0042')
            print('Locked.')
            time.sleep(2)

        self.connected = False
        self.socket.close()
        print('Thread3 stopped.')

    def stop(self):
        self.socket.close()
        self.connected = False
        print('Client stopped.')

    def run(self):
        keyboard.add_hotkey('ctrl+q', self.stop, args=())
        self.thread1 = threading.Thread(target=self.recv)
        self.thread2 = threading.Thread(target=self.heart_beat, args=(3,))
        self.thread3 = threading.Thread(target=self.task, args=(999,))
        self.thread1.start()
        self.thread2.start()
        self.thread3.start()
        self.thread1.join()
        self.thread2.join()
        self.thread3.join()


if __name__ == '__main__':
    c = OpClient(SERVER_IP, SERVER_PORT)
    if c.connect():
        c.subscribe('0060')
        c.subscribe('7408')
        c.run()



