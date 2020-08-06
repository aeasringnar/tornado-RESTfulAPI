#!/bin/bash
current_dir=$(dirname $(readlink -f $0))
port=8080
echo "项目地址：${current_dir}"
echo "web服务绑定的端口：${port}"
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
# 判断logs目录是否存在，没有则创建
if [ ! -d "${current_dir}/logs" ]
then
  `mkdir ${current_dir}/logs`
fi
# echo "pid list：${pid_list}"
# echo "cat：$*"
if [ $# != 0 ]
then
    if [ $1 == "start" ]
    then
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
        fi
        if [ $2 ]
        then
            if [ $2 == "prod" ]
            then
                echo 'prod'
                `cp ${current_dir}/config/prod_settings.py ${current_dir}/base/settings.py`
            else
                echo 'dev'
                `cp ${current_dir}/config/dev_settings.py ${current_dir}/base/settings.py`
            fi
        else
            echo 'dev'
            `cp ${current_dir}/config/dev_settings.py ${current_dir}/base/settings.py`
        fi
        `nohup python3 manage.py runserver 0.0.0.0:${port} > /dev/null 2>&1 &`
        echo "web服务启动成功..."
    elif [ $1 == 'stop' ]
    then
        if [ "$pid_list" ]
        then
            kill -9 ${pid_list}
            echo "web服务停止成功..."
        else
            echo "web服务未启动，无需停止..."
        fi
    elif [ $1 == 'show' ]
    then
        if [ "$pid_list" ]
        then
            echo "web服务运行中..."
            echo "进程信息："
            pid=`lsof -i:${port}  | grep -v PID | head -1 | awk '{print $2}'` && if [ "${pid}" ];then ps -ef | grep ${pid} | grep -v grep;fi
            echo "监听的tcp："
            lsof -i:${port}
        else
            echo "web服务未启动..."
        fi
    else
        echo "start：开启(or 重启)服务；stop：停止服务；show：显示详情；help：帮助信息"
    fi
else
    echo "参数错误，可以尝试命令：bash server.sh help"
fi
