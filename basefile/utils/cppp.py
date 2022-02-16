# -*- coding:utf-8 -*-

import sys;
import pandas as pd
from forecastPOS.model.posDB import PosDBModel
from forecastPOS.service.posDBService import PosDBService
from utils.dateUtils import DateUtils

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns',1000)

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/Users/didi/work/web/tob/woqu'])

def summry(did,preType,cycles,smoothCoef,iswoqu):
    startPreDay = '2019-07-15'
    cycleLenth = 7
    cyclesCoef = [0.2, 0.5]
    endPreDay = '2019-07-22'
    cid='123456'
    # caoyabin
    historyPosData = PosDBService.getHistoryPosData(did, DateUtils.nDatesAgo(startPreDay, cycles * cycleLenth), startPreDay, preType, cid)
    avgFixDict=PosDBService.extendPreday('avgm', did, startPreDay, preType, cycleLenth, cycles, cyclesCoef, endPreDay,smoothCoef,iswoqu,cid, historyPosData)
    smoothFixDict=PosDBService.extendPreday('avgmm', did, startPreDay, preType, cycleLenth, cycles, cyclesCoef, endPreDay,smoothCoef,iswoqu,cid, historyPosData)

    startBaseDay = startPreDay
    startPreDay = '2019-07-23'
    cid='123456'
    historydataDict = PosDBModel.getBasePos(did, startBaseDay, startPreDay, preType,cid)
    sumavg = 0
    sumsmo = 0

    sum_arae90=0
    sum_smot90=0
    sum_arae80=0
    sum_smot80=0
    sum_arae70=0
    sum_smot70=0
    sum_arae60=0
    sum_smot60=0
    sum_arae50=0
    sum_smot50=0
    sum_arae40=0
    sum_smot40=0

    c=0
    for i, k in enumerate(avgFixDict.keys()):
        c+=1
        avg = avgFixDict.get(k, 0)
        smoth = smoothFixDict.get(k, 0)
        tvalue = historydataDict.get(k, 0)
        piancha_avg = (0 if (tvalue == 0) else abs(avg - tvalue) / tvalue)
        piancha_smt = (0 if (tvalue == 0) else abs(smoth - tvalue) / tvalue)

        arae90 = 1 if avg>=tvalue*0.9 and avg<=tvalue*1.1 else 0
        smot90 = 1 if smoth>=tvalue*0.9 and smoth<=tvalue*1.1 else 0

        arae80 = 1 if avg >= tvalue * 0.8 and avg <= tvalue * 1.2 else 0
        smot80 = 1 if smoth >= tvalue * 0.8 and smoth <= tvalue * 1.2 else 0

        arae70 = 1 if avg >= tvalue * 0.7 and avg <= tvalue * 1.3 else 0
        smot70 = 1 if smoth >= tvalue * 0.7 and smoth <= tvalue * 1.3 else 0

        arae60 = 1 if avg >= tvalue * 0.6 and avg <= tvalue * 1.4 else 0
        smot60 = 1 if smoth >= tvalue * 0.6 and smoth <= tvalue * 1.4 else 0

        arae50 = 1 if avg >= tvalue * 0.5 and avg <= tvalue * 1.5 else 0
        smot50 = 1 if smoth >= tvalue * 0.5 and smoth <= tvalue * 1.5 else 0

        arae40 = 1 if avg >= tvalue * 0.4 and avg <= tvalue * 1.6 else 0
        smot40 = 1 if smoth >= tvalue * 0.4 and smoth <= tvalue * 1.6  else 0


        #print('avg %d smoth %d tvalue %d' %(avg,smoth,tvalue))



        sumavg += piancha_avg
        sumsmo += piancha_smt

        sum_arae90 += (1 if tvalue==0 else arae90)
        sum_smot90 += (1 if tvalue==0 else smot90)
        sum_arae80 += (1 if tvalue==0 else arae80)
        sum_smot80 += (1 if tvalue==0 else smot80)
        sum_arae70 += (1 if tvalue==0 else arae70)
        sum_smot70 += (1 if tvalue==0 else smot70)
        sum_arae60 += (1 if tvalue==0 else arae60)
        sum_smot60 += (1 if tvalue==0 else smot60)
        sum_arae50 += (1 if tvalue==0 else arae50)
        sum_smot50 += (1 if tvalue==0 else smot50)

        sum_arae40 += (1 if tvalue == 0 else arae40)
        sum_smot40 += (1 if tvalue == 0 else smot40)


        #print(' '.join(list(map(lambda x: str(x), m[i]))), k, avg, smoth, tvalue, piancha_avg, piancha_smt)
    return c,cycles, did, smoothCoef, sumavg, sumsmo,sum_arae90,sum_smot90,sum_arae80,sum_smot80,sum_arae70,sum_smot70,sum_arae60,sum_smot60,sum_arae50,sum_smot50,sum_arae40,sum_smot40


if __name__ == '__main__':
    for did in 14:#[14,6,49,58,16,44,52,47,51,50]:
       for cycles in [1]:#range(1,55):
           for smoothCoef in [1]:
                iswoqu=False
                c,cycles, did, smoothCoef, sumavgp, sumsmop, sum_arae90p, sum_smot90p, sum_arae80p, sum_smot80p, sum_arae70p, sum_smot70p, sum_arae60p, sum_smot60p, sum_arae50p, sum_smot50p, sum_arae40p, sum_smot40p = summry(did, 'trueOrders', cycles, smoothCoef,iswoqu)
                print('c,cycles, did, smoothCoef,sum_arae90p, sum_smot90p' ,c,cycles, did, smoothCoef,sum_arae90p, sum_smot90p)

if __name__ == '__main__1':
    for did in [6]:#[14,6,49,58,16,44,52,47,51,50]:
        for preType in ['trueOrders']:#['trueGMV','truePeoples']:
            endDay='2019-07-25'
            predictParam = {'token': 'x5989976c5441a5d32a29d11fb38c330f', 'timestr': '2019-08-12 13:16:07.203', 'predictType': 'WEEK','dayCount': 7, 'did': did, 'startDay': '2019-07-15', 'endDay': endDay, 'preType': preType, 'smoothCoef': 0.9, 'cyclesCoef': [0.2, 0.5]}

            a=PosDBService.predictProcess(predictParam)
            #print(a)

            avgDict=a.get('avgDict')
            smoothDict=a.get('smoothDict')
            deepDict=a.get('deepDict')
            prophetDict=a.get('prophetDict')
            seq2seqDict=a.get('seq2seqDict')

            did=predictParam.get('did')
            preType=predictParam.get('preType')

            startBaseDay = predictParam.get('startDay')
            startPreDay = endDay
            cid='123456'

            historydataDict = PosDBModel.getBasePos(did, startBaseDay, startPreDay, preType,cid)

            suma = 0
            sumb = 0
            sumc = 0
            sumd = 0
            sume = 0


            c=0
            c0=0
            for  k,t in avgDict.items():
             v = historydataDict.get(k, 0)

             l = avgDict.get(k)['scope'][0]
             r = avgDict.get(k)['scope'][1]
             if ( v>=l and v<=r) :
                 suma+=1

             l = smoothDict.get(k)['scope'][0]
             r = smoothDict.get(k)['scope'][1]
             if (v >= l and v <= r) :
                 sumb += 1

             l = deepDict.get(k)['scope'][0]
             r = deepDict.get(k)['scope'][1]
             if (v >= l and v <= r) or v == 0:
                 sumc += 1

             l = prophetDict.get(k)['scope'][0]
             r = prophetDict.get(k)['scope'][1]
             if (v >= l and v <= r) or v == 0:
                 sumd += 1

             l = seq2seqDict.get(k)['scope'][0]
             r = seq2seqDict.get(k)['scope'][1]
             if (v >= l and v <= r) or v == 0:
                 sume += 1

             c+=1
             if v==0:
                 c0+=1
             #print(c,c0,"suma,sumb,sumc,sumd,sume",[suma,sumb,sumc,sumd,sume],[v],avgDict.get(k)['scope'],smoothDict.get(k)['scope'],deepDict.get(k)['scope'],prophetDict.get(k)['scope'],seq2seqDict.get(k)['scope'])

            print('result',did,startBaseDay,startPreDay,preType,"suma,sumb,sumc,sumd,sume",c,c0,(suma,sumb,sumc,sumd,sume),(suma/c,sumb/c,sumc/c,sumd/c,sume/c))

