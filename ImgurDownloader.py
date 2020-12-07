import string, random, requests, os, time, threading

INVALID = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556]

ROOT_DIR = './photos/'

cooldown = 10

def parse_args() -> int:
    if len(sys.argv) < 2:
        sys.exit("\033[37mUsage: python3 " + sys.argv[0] + " (Number of threads)")
    THREAD_AMOUNT = int(sys.argv[1])
    if THREAD_AMOUNT > 500:
        sys.exit("Maximum amount of threads is 500!")
    return THREAD_AMOUNT

chars = string.ascii_letters + string.digits
chars1 = string.ascii_lowercase + string.digits

THREADS_PER_PROCESS = 10


REQUESTS = []
RESPONSES = []

BAD = []

COOLDOWN = False

def downloader():
    global COOLDOWN
    url = 'http://i.imgur.com/'
    while True:
        if COOLDOWN:
            time.sleep(cooldown)
        try:
            request = REQUESTS.pop(0)
        except:
            time.sleep(0.5)
            continue
           
        try:
            content = requests.get(url+request).content
        except:
            COOLDOWN = True
            continue
        if len(content) in INVALID or b'<!doctype html' == content[:14].lower():
            BAD.append(request)
            continue
           
        RESPONSES.append((request,content))

def writer():
    while True:
        try:
            response = RESPONSES.pop(0)
        except:
            time.sleep(0.5)
            continue
        file = open(ROOT_DIR+response[0],'wb')
        file.write(response[1])
        file.close()



def download():
    global COOLDOWN
    threads = []
    for i in range(THREADS_PER_PROCESS):
        threads.append(threading.Thread(target=downloader,args=[]))
        threads[i].start()
        
    threads.append(threading.Thread(target=writer,args=[]))
    threads[-1].start()
    
    while True:
        if COOLDOWN:
            print(f"COOLDOWN! {cooldown} secs. pausing {THREADS_PER_PROCESS} threads!")
            time.sleep(cooldown)
            cooldown = False
            
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
            time.sleep(0.2)
        # content = requests.get(url+filename).content
        # if len(content) in INVALID or b'<!doctype html' == content[:14].lower():
            # continue
        # try:
            # response = RESPONSES.pop(0)
        # except:
            # delta = int(time.time()) - start
            # if delta < timeout:
                # time.sleep(timeout - delta)
            # continue
        # file = open(ROOT_DIR+response[0],'wb')
        # file.write(response[1])
        # file.close()
        # delta = int(time.time()) - start
        # if delta < timeout:
            # time.sleep(timeout - delta)






def main():
    
    THREAD_AMOUNT = parse_args()
    try:
        os.mkdir(ROOT_DIR)
    except:
        pass
    print('Root folder:',ROOT_DIR)
    print('Starting:',THREAD_AMOUNT,'threads')
    for i in range(THREAD_AMOUNT):
        multiprocessing.Process(target=download).start()

    while True:
        time.sleep(1)


if __name__ == '__main__':
    import sys, time, multiprocessing
    main()
