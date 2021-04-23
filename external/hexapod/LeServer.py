#!/usr/bin/python
# encoding: utf-8

import SocketServer
import threading
import time
import re
from LeCmd import LeError
import LeCmd


class ServoServer(SocketServer.BaseRequestHandler):
    Flag = True

    def handle(self):
        print("Conneced")
        conn = self.request
        while self.Flag:
            try:
                # Here hasn't considered that whether the data sent by the sending side is beyond the range of receiving (1024)！
                recv_data = conn.recv(1024)
                if not recv_data:
                    self.Flag = False
                    print("break")
                    break
                # Remove the blank space
                recv_data = recv_data.replace(' ', '')
                # Generate regular objects
                cp = re.compile(r'\r\n')
                test = cp.search(recv_data)
                if test:
                    rdata = recv_data.split("\r\n")  # Separate
                    rdata = [rdata[0]]
                    for data in rdata:  # Because there is only one element in rdata, it will only execute once
                        if data:
                            # print("Cmd:%s"%(data))
                            rex = re.compile(r'^(I[0-9]{3}).*')  # Determine whether the instruction received conforms to the rules
                            match = data
                            match = rex.match(match)
                            if match:
                                if not 0 == match.start() or not len(data) == match.end():
                                    print("Wrong command 1")
                                else:
                                    # print 'data', data
                                    data = data.split('-')
                                    cmd = data[0][1:5]
                                    del data[0]
                                    par = []
                                    try:
                                        cmd = int(cmd)
                                        if 3 <= cmd <= 9:
                                            LeCmd.cmd_list[cmd](conn, data)
                                        else:
                                            for p in data:
                                                par.append(int(p))
                                            print 'par:', par
                                            LeCmd.cmd_list[cmd](par)
                                    except LeError as err:
                                        print(err.msg)
                                        print(err.data)
                                    except:
                                        print("Command execution error")
                            else:
                                pass
                else:
                    pass
                if not self.Flag:
                    break
            except Exception as e:
                print(e)
                break

    def finish(self):
        print("Disconnected")


class LeServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    server = LeServer(("", 1444), ServoServer)
    try:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()
        while True:
            time.sleep(0.1)
    except:
        server.shutdown()
        server.server_close()

