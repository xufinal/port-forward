from __future__ import print_function
from gevent.server import StreamServer
from gevent.socket import create_connection
import gevent
import socket
from gevent.pool import Pool


def forward(socket,address):
    print('New connection from %s:%s' % address)
    try:
        dest = create_connection(('127.0.0.1',8000))
    except IOError as ex:
        print('error connection proxy')
        return ''

    forwarders = (gevent.spawn(forward_handle, socket, dest),
                  gevent.spawn(forward_handle, dest, socket))
    gevent.joinall(forwarders)




def forward_handle(source, dest):
    source_address = '%s:%s' % source.getpeername()[:2]
    dest_address = '%s:%s' % dest.getpeername()[:2]
    try:
        while True:
            try:
                data = source.recv(60000)
                if not data:
                    break
                dest.sendall(data)
            except KeyboardInterrupt:
                # On Windows, a Ctrl-C signal (sent by a program) usually winds
                # up here, not in the installed signal handler.
                
                break
            except socket.error:
                break
    finally:
        source.close()
        dest.close()




if __name__ == '__main__':
    pool = Pool(10000) 
    server = StreamServer(('0.0.0.0', 8800), forward ,spawn=pool)
    print('Starting forward server on port 8800')
    server.serve_forever()
