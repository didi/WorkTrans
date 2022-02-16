from laborCnt.model import labor_shift_split_rule_db as db

def test_insert():
    flag = db.LaborShiftSplitRule.insert_record('1','2','3','4','5','6','7',True,1)
    print(flag)

def test_soft_delete():
    flag = db.LaborShiftSplitRule.soft_delete_record('123456','20190329124156363056100123kg025l','14')
    print(flag)

def test_update():
    flag = db.LaborShiftSplitRule.update_record('123456','20190329124156363056100123kg025l','34','worktime','lt',480,True,24)
    print(flag)

def test_select_record():
    # 4	20190329124156363056100123kg025l	123456	14	modify	worktime	lt	480	1	2019-09-10 19:27:58	2019-09-10 19:27:58	1
    '''
    24	20190329124156363056100123kg025l	123456	14	modify	worktime	lt	480	1	2019-09-11 11:21:29	2019-09-11 11:21:29	1
    :return:
    '''
    flag,auto_id = db.LaborShiftSplitRule.select_record_exists('123456','20190329124156363056100123kg025l','14','modify','worktime','lt','480',True,1)
    print(flag,auto_id)


if __name__ == '__main__':
    #test_soft_delete()
    #test_insert()
    #test_update()
    #test_select_record()

    combiRuleData = {"combiRule": "20190605101543145043101404020054,20190605101543145043101404020053",
                     "combiRuleNewVal": "3-5",
                     "combiRuleOldVal": "3-4"}
    print(combiRuleData['combiRule'].split(",")[0])


