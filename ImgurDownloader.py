import string, random, requests, os, time

INVALID = [0, 503, 5082, 4939, 4940, 4941, 12003, 5556]

ROOT_DIR = './photos/'

timeout = 4

def parse_args() -> int:
    if len(sys.argv) < 2:
        sys.exit("\033[37mUsage: python3 " + sys.argv[0] + " (Number of threads)")
    THREAD_AMOUNT = int(sys.argv[1])
    if THREAD_AMOUNT > 500:
        sys.exit("Maximum amount of threads is 500!")
    return THREAD_AMOUNT

chars = string.ascii_letters + string.digits
chars1 = string.ascii_lowercase + string.digits

def download():
    url = 'http://i.imgur.com/'
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

        if filename in os.listdir(ROOT_DIR):#if file exists
            continue
    
        content = requests.get(url+filename).content
        if len(content) in INVALID or b'<!doctype html' == content[:14].lower():
            continue

        file = open(ROOT_DIR+filename,'wb')
        file.write(content)
        file.close()
        delta = int(time.time()) - start
        if delta < timeout:
            time.sleep(timeout - delta)






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
