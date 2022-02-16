#!/bin/bash
#############################################
## main
## 非托管方式, 启动服务
## control.sh脚本, 必须实现start和stop两个方法
#############################################
source ~/.bash_profile
source ~/.bashrc
workspace=$(cd $(dirname $0) && pwd -P)
cd ${workspace}
module="basefile/run.py"
app=${module}
conf=cfg/cfg.toml
logfile=var/app.log
pidfile=var/app.pid
python=python3
port=8867
if [ ${DIDIENV_ODIN_DB_CON}x == "dbtest"x ]; then
    python=python3.6
    port=8088
fi
## function
function start() {
    # 创建日志目录
    mkdir -p var &>/dev/null
    # check服务是否存活,如果存在则返回
    check_pid
    if [ $? -ne 0 ];then
        local pid=$(get_pid)
        echo "${app} is started, pid=${pid}"
        exit 0
    fi
    # 以后台方式 启动程序
    # nohup ./${app} -c ${conf} >>${logfile} 2>&1 &

    nohup ${python} ${app} --port=${port} >>${logfile} 2>&1 &
    # 记录服务pid
    pid=$(echo $!)
    # 保存pid到pidfile文件中
    echo ${pid} > ${pidfile}
    # 检查服务是否启动成功
    check_pid
    if [ $? -eq 0 ];then
        echo "${app} start failed, please check"
        exit 1
    fi

    echo "${app} start ok, pid=${pid}"
    # 启动成功, 退出码为 0
    exit 0
}
function stop() {
    # 循环stop服务, 直至60s超时
    for (( i = 0; i < 60; i++ )); do
        # 检查服务是否停止,如果停止则直接返回
        check_pid
        if [ $? -eq 0 ];then
           echo "${app} is stopped"
           exit 0
        fi
        # 检查pid是否存在
        local pid=$(get_pid)
        if [ ${pid} == "" ];then
           echo "${app} is stopped, can't find pid on ${pidfile}"
           exit 0
        fi
        # 停止该服务
        kill ${pid} &>/dev/null
        # 检查该服务是否停止ok
        check_pid
        if [ $? -eq 0 ];then
            # stop服务成功, 返回码为 0
            echo "${app} stop ok"
            exit 0
        fi

        # 服务未停止, 继续循环
        sleep 1
    done
    # stop服务失败, 返回码为 非0
    echo "stop timeout(60s)"
    exit 1
}

function status(){
    check_pid
    local running=$?
    if [ ${running} -ne 0 ];then
        local pid=$(get_pid)
        echo "${app} is started, pid=${pid}"
    else
        echo "${app} is stopped"
    fi
    exit 0
}

## internals
function get_pid() {
    if [ -f $pidfile ];then
        cat $pidfile
    fi
}

function check_pid() {
    pid=$(get_pid)
    if [ "x_" != "x_${pid}" ]; then
        running=$(ps -p ${pid}|grep -v "PID TTY" |wc -l)
        return ${running}
    fi
    return 0
}
action=$1
case $action in
    "start" )
        # 启动服务
        start
        ;;
    "stop" )
        # 停止服务
        stop
        ;;
    "status" )
        # 检查服务
        status
        ;;
    * )
        echo "unknown command"
        exit 1
        ;;
esac
