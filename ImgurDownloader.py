import string, random, os, time, threading
import socket
import ssl
import select

INVALID = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556]

ROOT_DIR = './photos/'

MAX_CONNECTIONS = 10
THREADS_PER_PROCESS = 2


def parse_args() -> int:
    if len(sys.argv) < 2:
        sys.exit("\033[37mUsage: python3 " + sys.argv[0] + " (Number of threads) MAX_CONNECTIONS(optional)")
    THREAD_AMOUNT = int(sys.argv[1])
    if THREAD_AMOUNT > 500:
        sys.exit("Maximum amount of threads is 500!")

    if len(sys.argv)==3:
        max_cons = int(sys.argv[2])
    else:
        max_cons = MAX_CONNECTIONS
    return THREAD_AMOUNT,max_cons

chars = string.ascii_letters + string.digits
chars1 = string.ascii_lowercase + string.digits

HOSTNAME = 'i.imgur.com'

server_ip = socket.gethostbyname(HOSTNAME)
server_port = 443

REQUESTS = []
RESPONSES = []

BAD = []


def get_payload(filename:str):
    data = bytes(f'GET /{filename} HTTP/1.1\r\nHost: {HOSTNAME}\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0\r\nAccept: */*\r\nAccept-Encoding: gzip, deflate\r\nConnection: keep-alive\r\n\r\n','ascii')
    return data


def parse_headers(data:str):
    if data[9:12]!='200':
        return 0

    offset = data.find('Content-Length: ')+len('Content-Length: ')
    num = ''
    while data[offset] != '\r':
        num += data[offset]
        offset += 1
    num = int(num)
    return num


def downloader():
    global BAD,REQUESTS,MAX_CONNECTIONS
    #url = 'http://i.imgur.com/'  
    connections = []
    connections_data = []
    context = ssl.create_default_context()
    for i in range(MAX_CONNECTIONS):
        sock = socket.socket()
        sock.connect((server_ip,server_port))
        ssock = context.wrap_socket(sock,server_hostname=HOSTNAME)
        ssock.setblocking(0)
        connections.append(ssock)
        connections_data.append([0,b'',False,'',False])


    while True:#main loop
        rcon,wcon,xcon = select.select(connections,connections,[])
        for connection in wcon:
            id = connections.index(connection)
            if not connections_data[id][2]:
                try:
                    request = REQUESTS.pop(0)
                except:           
                    continue

                try:
                    connection.send(get_payload(request))
                except:
                    REQUESTS.append(request)
                    connections[id].close()
                    sock = socket.socket()
                    sock.connect((server_ip,server_port))
                    ssock = context.wrap_socket(sock,server_hostname=HOSTNAME)
                    ssock.setblocking(0)
                    connections[id] = ssock
                    continue
                connections_data[id][2] = True
                connections_data[id][3] = request

        for connection in rcon:
            try:
                id = connections.index(connection)
            except:                
                continue
            if not connections_data[id][2]:
                continue
            request = connections_data[id][3]
            if connections_data[id][0] == 0:

                try:
                    data_raw = connection.recv(2048)
                except Exception as e:
                    REQUESTS.append(request)
                    connections[id].close()
                    sock = socket.socket()
                    sock.connect((server_ip,server_port))
                    ssock = context.wrap_socket(sock,server_hostname=HOSTNAME)
                    ssock.setblocking(0)
                    connections[id] = ssock
                    connections_data[id] = [0,b'',False,'',False]
                    continue

                if data_raw == b'':
                    REQUESTS.append(request)
                    connections[id].close()
                    sock = socket.socket()
                    sock.connect((server_ip,server_port))
                    ssock = context.wrap_socket(sock,server_hostname=HOSTNAME)
                    ssock.setblocking(0)
                    connections[id] = ssock
                    connections_data[id] = [0,b'',False,'',False]
                    continue

                data = data_raw.decode('ascii')
                size = parse_headers(data)
                if size in INVALID:
                    BAD.append(request)
                    connections_data[id] = [0,b'',False,'',False]
                    continue
                connections_data[id][0] = size
                connections_data[id][4] = False

            else:
                try:
                    data_raw = connection.recv(connections_data[id][0])
                except:
                    REQUESTS.append(request)
                    connections[id].close()
                    sock = socket.socket()
                    sock.connect((server_ip,server_port))
                    ssock = context.wrap_socket(sock,server_hostname=HOSTNAME)
                    ssock.setblocking(0)
                    connections[id] = ssock
                    connections_data[id] = [0,b'',False,'',False]
                    continue
                if not connections_data[id][4]:
                    if b'<!doctype html' == data[:14].lower():
                        BAD.append(request)
                        connections_data[id] = [0,b'',False,'',False]
                        continue
                    connections_data[id][4] = True

                connections_data[id][1] += data_raw
                connections_data[id][0] -= len(data_raw)

                if connections_data[id][0] == 0:
                    RESPONSES.append((request,connections_data[id][1]))
                    connections_data[id] = [0,b'',False,'',False]
        #time.sleep(0.05)
        





def writer():
    default_times = 0
    times = default_times
    
    while True:
        if len(RESPONSES)<10:
            if times < 3:
                time.sleep(0.5)
                times += 1
                default_times = 0
                continue
            else:
                default_times = 3
        times = default_times
        try:
            response = RESPONSES.pop(0)
        except:
            time.sleep(0.5)
            continue
        file = open(ROOT_DIR+response[0],'wb')
        file.write(response[1])
        file.close()


def download(max_cons):
    global MAX_CONNECTIONS
    MAX_CONNECTIONS = max_cons
    threads = []
    for i in range(THREADS_PER_PROCESS):
        threads.append(threading.Thread(target=downloader,args=[]))
        threads[i].start()
        
    threads.append(threading.Thread(target=writer,args=[]))
    threads[-1].start()
    counter = 0
    while True:
        
            
        start = int(time.time())
        length = random.choice((5, 6))
        filename = ''
        if length == 5:
            filename += ''.join(random.choice(chars) for _ in range(5))
        else:
            filename += ''.join(random.choice(chars) for _ in range(3))
            filename += ''.join(random.choice(chars1) for _ in range(3))
        filename += '.jpg'

        if filename in BAD or filename in os.listdir(ROOT_DIR) or filename in REQUESTS:#if file exists
            pass
        else:
            REQUESTS.append(filename)
            counter += 1
        if counter == MAX_CONNECTIONS*2:
            counter = 0
            time.sleep(0.3)
        


def main():
    
    THREAD_AMOUNT,max_cons = parse_args()
    try:
        os.mkdir(ROOT_DIR)
    except:
        pass
    print('Root folder:',ROOT_DIR+'\n')
    print(HOSTNAME)
    print(f'{server_ip}:{server_port}\n')
    
    print('Starting:',THREAD_AMOUNT,'threads')
    print(f'{THREADS_PER_PROCESS} downloading threads per process')
    print(f'{max_cons} connections per thread in process')
    for i in range(THREAD_AMOUNT):
        multiprocessing.Process(target=download,args=[max_cons]).start()
    #download()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    import sys, time, multiprocessing
    main()
    
