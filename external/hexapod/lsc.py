#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import socketserver
import Serial_Servo_Running as SSR
# import threading
import PWMServo
import time
import get_data
import os
import signal

DEBUG = False
client_socket = []
inf_flag = False

# Enable thread running action group
SSR.start_action_thread()


class LobotServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True  # Allow address reuse


class LobotServerHandler(socketserver.BaseRequestHandler):
    global client_socket
    ip = ""
    port = None

    def setup(self):
        self.ip = self.client_address[0].strip()
        self.port = self.client_address[1]
        print("connected\tIP:"+self.ip+"\tPort:"+str(self.port))
        client_socket.append(self.request)  # Add this connection to the client list
        self.request.settimeout(6)  # The timeout is 6 seconds

    def handle(self):
        global action_num, action_times, inf_flag
        conn = self.request
        recv_data = b''
        Flag = True
        while Flag:
            try:
                buf = conn.recv(1024)
                if buf == b'':
                    Flag = False
                else:
                    recv_data = recv_data + buf
                    # Send the command to the serial port until receiving the complete command to prevent error
                    while True:
                        try:
                            index = recv_data.index(b'\x55\x55')  # Search 0x55 0x55 in the data
                            if len(recv_data) >= index+3:  # Whether the length of the data in the cache is sufficient
                                recv_data = recv_data[index:]
                                if recv_data[2] + 2 <= len(recv_data):  # Whether the length of the data in the cache is enough
                                    cmd = recv_data[0:(recv_data[2]+2)]    # Take the command
                                    recv_data = recv_data[(recv_data[2]+3):]  # Remove the taken command
                                    if cmd[0] and cmd[1] is 0x55:
                                        if cmd[2] == 0x08 and cmd[3] == 0x03:  # Data length and control single servo command
                                            print('id', cmd[7])
                                            id = cmd[7]
                                            pos = 0xffff & cmd[8] | 0xff00 & cmd[9] << 8
                                            print('pos', pos)
                                            if id == 19:
                                                PWMServo.setServo(1, pos, 20)
                                            elif id == 20:
                                                PWMServo.setServo(2, pos, 20)
                                            else:
                                                pass
                                        elif cmd[2] == 0x05 and cmd[3] == 0x06:
                                            action_num = cmd[4]
                                            action_times = 0xffff & cmd[5] | 0xff00 & cmd[6] << 8
                                            print('action', action_num)
                                            print('times', action_times)
                                            if action_times == 0:  # Infinite imes
                                                print('action_times:', action_times)
                                                SSR.change_action_value(str(action_num), action_times)
                                                inf_flag = True
                                            else:
                                                if inf_flag:
                                                    SSR.stop_action_group()
                                                    inf_flag = False
                                                else:
                                                    SSR.change_action_value(str(action_num), action_times)
                                        elif cmd[2] == 0x0b and cmd[3] == 0x03:
                                            PWMServo.setServo(1, 1500, 100)
                                            PWMServo.setServo(2, 1500, 100)
                                            time.sleep(0.1)
                                        data = get_data.read_data()
                                        print(int(data[0]))
                                        os.kill(int(data[0]), signal.SIGKILL)
                                        get_data.write_data("K", "0")
                                    if DEBUG is True:
                                        for i in cmd:
                                            print(hex(i))
                                        print('*' * 30)
                                else:
                                    break
                            else:
                                break
                        except Exception as e:   # The '\x55\x55' substring cannot be found in recv_data
                            break
                    recv_data = b''
                    action_times = None
                    action_num = None
            except Exception as e:
                print(e)
                Flag = False
                break

    def finish(self):
        client_socket.remove(self.request)  # Remove this connection from the client list
        print("disconnected\tIP:"+self.ip+"\tPort:"+str(self.port))


if __name__ == "__main__":
    PWMServo.setServo(1, 1500, 100)
    time.sleep(0.1)
    PWMServo.setServo(2, 1500, 100)
    time.sleep(0.1)
    SSR.running_action_group('25', 1)
    server = LobotServer(("", 9029), LobotServerHandler)    # Set up the server
    try:
        server.serve_forever()  # Start server cycle
    except Exception as e:
        print(e)
        server.shutdown()
        server.server_close()
