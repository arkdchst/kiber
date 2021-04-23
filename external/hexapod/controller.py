#!/usr/bin/python3
# -*- coding: UTF-8 -*-
#
# ##Only one servo can be set at one time, and the raspberry PI extension board can only be connected to one servo, so you have to set the parameter of servos one by one
#
import subprocess
import time
import threading
import os
import socketserver
import re
import signal
import get_data

lastMode = 0
lastPID = None


class LobotServer(socketserver.TCPServer):
    allow_reuse_address = True  # Reuse the address


class LobotServerHandler(socketserver.BaseRequestHandler):
    ip = ""
    port = None
    buf = ""

    def setup(self):
        self.ip = self.client_address[0].strip()  # Get the IP of the client
        self.port = self.client_address[1]  # Get the client port
        print("connected\tIP:" + self.ip + "\tPort:" + str(self.port))
        self.request.settimeout(20)  # Set the connection timeout to 20 seconds

    def handle(self):
        global lastMode
        global lastPID
        Flag = True
        while Flag:
            try:
                recv = self.request.recv(128)  # Receive datav
                if recv == b'':
                    Flag = False  # Exit if it is empty
                else:
                    self.buf += recv.decode()  # Decode
                    #print(self.buf)
                    self.buf = re.sub(r'333333','',self.buf, 10)  # Appoint the client sends '3' to perform the heartbeat and remove the 3 from the character string
                    s = re.search(r'mode=\d{1,2}', self.buf, re.I) # Find the MODE= number character string in the formatted string
                    if s:
                        self.buf=""   # Clear all caches as long as find one
                        Mode = int(s.group()[5:])  # Get the value of mode from the character string
                        print(Mode)
                        data = get_data.read_data()
                        if data[1] == "0":
                            lastMode = 0
                        # According to the value of Mode, continue sending running signal to the corresponding subprocess, and the corresponding subprocess will run
                        if Mode == 0:
                            if lastMode != Mode: # Only if the last time mode is different from the current mode, the mode should convert
                                lastMode = Mode   
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                            self.request.sendall("OK".encode())   # Send "OK" to the client
                        elif Mode == 1:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvColor = subprocess.Popen(["python2", "/home/pi/hexapod/color.py"])  # Colour identification
                                lastPID = ChildCvColor.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 2:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvColorFollow = subprocess.Popen(["python2", "/home/pi/hexapod/color_follow.py"])  # Colour tracking
                                lastPID = ChildCvColorFollow.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 3:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvColorFollowMove = subprocess.Popen(["python2", "/home/pi/hexapod/color_follow_move.py"])  # Ogranism colour tracking
                                lastPID = ChildCvColorFollowMove.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 4:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildBalance = subprocess.Popen(["python2", "/home/pi/hexapod/balance.py"])  # Self balance
                                lastPID = ChildBalance.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 5:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvFind = subprocess.Popen(["python2", "/home/pi/hexapod/sonar.py"]) # Ultrasonic aviodance
                                lastPID = ChildCvFind.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        elif Mode == 6:
                            if lastMode != Mode:
                                lastMode = Mode
                                if lastPID is not None:
                                    os.kill(lastPID, signal.SIGKILL)
                                ChildCvLineFollow = subprocess.Popen(["python2", "/home/pi/hexapod/linefollow.py"])  # Line following
                                lastPID = ChildCvLineFollow.pid
                                get_data.write_data(str(lastPID), str(lastMode))
                                print("lastPID:", lastPID)
                            self.request.sendall("OK".encode())
                        else:
                            lastMode = 0
                            if lastPID is not None:
                                os.kill(lastPID, signal.SIGKILL)
                            lastPID = None
                            self.request.sendall("Failed".encode())
                            pass
            except Exception as e:
                print(e)
                Flag = False

    def finish(self):
        global lastMode
        global lastPID

        lastMode = 0
        data = get_data.read_data()
        print("data[0]:", len(data[0]))
        if data[0] != "K":
            os.kill(lastPID, signal.SIGKILL)
        lastPID = None
        get_data.write_data(str("K"), str(lastMode))
        print("disconnected\tIP:" + self.ip + "\tPort:" + str(self.port))


if __name__ == '__main__':
    server = LobotServer(("", 9040), LobotServerHandler)
    server.serve_forever()  # Enable serve

