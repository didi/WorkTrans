# -*- coding:utf-8 -*-
import time
import threading
import socket


def doGet():
    requests.get('http://127.0.0.1:8868/predict?a=1&b=2').text

if __name__ == "__main__":
    start = time.time()

    # 查看当前主机名
    print('当前主机名称为 : ' + socket.gethostname())

    # 根据主机名称获取当前IP
    print('当前主机的IP为: ' + socket.gethostbyname(socket.gethostname()))

    threads = []
    for i in range(200):
        threads.append(threading.Thread(target=doGet))

    start1=time.time()
    print('开始启动：%f s' %(start1-start))
    for t in threads:
        t.start()

    start2 = time.time()
    print('  启动完成：%f s' % (start2 - start1))
    for t in threads:
        t.join()
    end = time.time()
    print("  执行完成: %f s" % (end - start2))

    print("完成时间: %f s" % (end - start))



