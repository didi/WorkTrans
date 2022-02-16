import threading
import time

class myThread(threading.Thread):
    def __init__(self,func):
        threading.Thread.__init__(self)
        # self.threadID = threadID
        # self.name = name
        # self.counter = counter
        self.func = func
    def run(self):
        print ("开始线程：" + self.name)
        self.func()
        print ("退出线程：" + self.name)

