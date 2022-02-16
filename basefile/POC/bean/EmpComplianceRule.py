'''
create by liyabin
'''

from POC.model.forecast_task_DB import ForecastTaskDB


class EmpComplianceRule:
    @staticmethod
    def create_rule_file(cid: str):
        rule_result = ForecastTaskDB.read_all_rule(cid)
        #print(rule_result)
        rules_dict = {}
        # rule : ptype,cid,eid,did,ruleType,ruleCpType,ruletag,ruleCpNum,startDate,dayFusion,cycle,timeRange,shiftId,cret,caution,bid
        for rule in rule_result:
            temp_list = []
            r_d = {}

            ptype = rule[0]
            cid = rule[1]
            # 组织规则
            if (ptype == "organizerule"):
                continue
            # 员工规则
            elif (ptype == "emprule"):
                eid = rule[2]
                # r_d["eid"] = eid
                #bid = rule[15]

                r_d["cid"] = cid
                r_d["eid"] = eid

                r_d["ruleType"] = rule[4]
                r_d["ruleCpType"] = rule[5]
                r_d["ruletag"] = rule[6]
                r_d["ruleCpNum"] = rule[7]
                r_d["startDate"] = rule[8]
                r_d["dayFusion"] = rule[9]
                r_d["cycle"] = rule[10]
                r_d["timeRange"] = rule[11]
                r_d["shiftId"] = rule[12]
                r_d["cret"] = rule[13]
                r_d["caution"] = rule[14]


                # key = cid + "-" + eid + "-" + ptype
                key = cid + "-" + eid + "-" + ptype
                if key not in rules_dict:
                    temp_list.append(r_d)
                    rules_dict[key] = temp_list
                else:
                    rules_dict[key].append(r_d)
        return rules_dict

    @staticmethod
    def create_rule_file_new(cid: str):
        rule_result = ForecastTaskDB.read_all_rule(cid)
        # print(rule_result)
        rules_dict = {}
        # rule : ptype,cid,eid,did,ruleType,ruleCpType,ruletag,ruleCpNum,startDate,dayFusion,cycle,timeRange,shiftId,cret,caution,bid
        for rule in rule_result:
            temp_list = []
            r_d = {}

            ptype = rule[0]
            cid = rule[1]
            bid = rule[15]

            r_d["cid"] = cid
            r_d["bid"] = bid

            r_d["ruleType"] = rule[4]
            r_d["ruleCpType"] = rule[5]
            r_d["ruletag"] = rule[6]
            r_d["ruleCpNum"] = rule[7]
            r_d["startDate"] = rule[8]
            r_d["dayFusion"] = rule[9]
            r_d["cycle"] = rule[10]
            r_d["timeRange"] = rule[11]
            r_d["shiftId"] = rule[12]
            r_d["cret"] = rule[13]
            r_d["caution"] = rule[14]

            # key = cid + "-" + eid + "-" + ptype
            key = cid + "-" + bid
            if key not in rules_dict:
                temp_list.append(r_d)
                rules_dict[key] = temp_list
            else:
                rules_dict[key].append(r_d)
        return rules_dict

if __name__ == '__main__':
    print(EmpComplianceRule.create_rule_file_new(cid="50000735"))