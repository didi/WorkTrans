import threading
import time

'''
https://blog.csdn.net/qq_34824856/article/details/80939449 
'''

def print_111():
    for i in range(200):
        print('1111')

def print_222():
    for i in range(200):
        print('222')


threads = []
t1 = threading.Thread(target=print_111)
threads.append(t1)
t2 = threading.Thread(target=print_222)
threads.append(t2)

if __name__=='__main__':
    start = time.time()

    print('zhangsan.....')
    for t in threads:
        t.start()
    print('lisi.....')
    for t in threads:
        t.join()

    end = time.time()
    print("完成时间: %f s" % (end - start))

print ("退出线程")
