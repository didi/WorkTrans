import os
db_config={
    "db" :{
        'mysql': {
            'driver': 'mysql',
            'host': '100.69.238.14',
            'port': 4102,
            'database': 'woqu_schedule',
            'user': 'woq_sch_6gsjwh_rw',
            'password': 'ywHRDjTvp5hQZmb',
            'prefix': '',
            'use_unicode': False
        }
    },
    "dbold":{
        'mysql': {
            'driver': 'mysql',
            'host': '10.86.53.56',
            'port': 3306,
            'database': 'woqu',
            'user': 'root',
            'password': 'tongjirenzhi6+A',
            'prefix': '',
            'use_unicode': False
        }
    },
    "db1":{
        'mysql': {
            'driver': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'database': 'woqu',
            'user': 'root',
            'password': '123456',
            'prefix': '',
            'use_unicode': False
        }
    },
    "dbtest":{
        'mysql': {
            'driver': 'mgiysql',
            'host': '100.69.238.14',
            'port': 4142,
            'database': 'woqu_test',
            'user': 'woqu_test_kiclwu_rw',
            'password': 'OeMLQZC5kbBoWs8',
            'prefix': '',
            'use_unicode': False
        }
    }
}


class conf():
        db_config_name = os.environ.get('DIDIENV_ODIN_DB_CON','db')
        db = db_config[db_config_name]
