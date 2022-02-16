import time
import random
from datetime import datetime
from multiprocessing import Process

def piao(name):
    s=datetime.now()
    print('%s piaoing %s' %(name,s))
    t=random.randrange(2,7)
    time.sleep(t)
    e=datetime.now()
    print('%s piao end %s %s' %(name,(e-s).seconds,t))

if __name__ == '__main__':

    '''
    #实例化得到四个对象
    p1=Process(target=piao,args=('egon',)) #必须加,号
    p2=Process(target=piao,args=('alex',))
    p3=Process(target=piao,args=('wupeqi',))
    p4=Process(target=piao,args=('yuanhao',))

    #调用对象下的方法，开启四个进程
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    '''



    for i in range(10):
        Process(target=piao, args=('egon  - '+str(i),)).start()
    print('主')
