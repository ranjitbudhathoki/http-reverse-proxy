import socket
import sys

OWN_ADDR = ("0.0.0.0", 8000)
UPSTREAM_ADDR = ("127.0.0.1", 9000)

def log(message):  
    print(message, file=sys.stderr)

# create a socket interface where client can connect 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(OWN_ADDR)
s.listen()
log(f"Accepting new connection on ${OWN_ADDR}")


# accept a connecction froma  accept queue (long running process)
while True:
    client_con, client_addr = s.accept()
    log(f"New connection from {client_addr}")
    # receive packets from a client connection
    data = client_con.recv(4096)
    log(f"->*   {len(data)}B")
    try:
    # create a socket with upstream server
        upstream_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        upstream_sock.connect(UPSTREAM_ADDR)
        log(f"Connected to {UPSTREAM_ADDR}")

        #forward data received from client to upstream 
        upstream_sock.send(data)
        log(f"   *->{len(data)}B")

        # receive the response back from the upstream
        while True:
            res = upstream_sock.recv(4096)
            log(f"   *<-{len(res)}B")

            if not res:
                break
            # send the response received from the upstream to client
            client_con.send(res)
            log(f"<-*  {len(res)}B")
    except ConnectionRefusedError:
        client_con.send(b'HTTP/1.1 502 BAD GATEWAY\r\n\r\n')
        log("<-* BAD GATEWAY")
    except OSError as err:
       log(err) 
    finally:
        upstream_sock.close()
        client_con.close()
s.close()

