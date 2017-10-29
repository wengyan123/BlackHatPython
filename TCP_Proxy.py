import sys
from socket import *
from threading import Thread
import time


LOGGING = 1


def log(s):
    if LOGGING:
        print '%s %s' % (time.ctime(), s)


class Pipe(Thread):
    pipes = []

    def __init__(self, source, dest):
        Thread.__init__(self)
        self.source = source
        self.dest = dest
        log('Creating new pipe thread %s (%s -> %s)' %\
            (self, source.getpeername(), dest.getpeername()))
        Pipe.pipes.append(self)
        log('%s pipes active' % len(Pipe.pipes))

    def run(self):
        while 1:
            try:
                data = self.source.recv(1024)
                if not data:
                    break
                self.dest.send(data)
            except Exception as e:
                log(e)
                break
        log('%s terminating' % self)
        self.dest.close()
        self.source.close()
        Pipe.pipes.remove(self)
        log('%s pipes active' % len(Pipe.pipes))


class Proxy(Thread):

    def __init__(self, port, fwdhost, fwdport):
        Thread.__init__(self)
        log('Redireacting: localhost:%s -> %s:%s' % (port, fwdhost, fwdport))
        self.fwdhost = fwdhost
        self.fwdport = fwdport
        # listen client connection
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(5)

    def run(self):
        while 1:
            clientsock, clientaddress = self.sock.accept()
            log('Creating new session for %s %s ' % clientaddress)
            fwdsock = socket(AF_INET, SOCK_STREAM)
            fwdsock.connect((self.fwdhost, self.fwdport))
            Pipe(clientsock, fwdsock).start()
            Pipe(fwdsock, clientsock).start()


if __name__ == '__main__':

    print 'Starting TCPproxy'

    #sys.stdout = open('TCPproxy.log', 'w')

    if len(sys.argv) > 1:
        # if does not specify fwdport, fwdport = localport
        port = fwdport = int(sys.argv[1])
        fwdhost = sys.argv[2]
        if len(sys.argv) == 4: fwdport = int(sys.argv[3])

        Proxy(port, fwdhost, fwdport).start()
    else:
        print "usage: TCP_Proxy.py port host [newport]"