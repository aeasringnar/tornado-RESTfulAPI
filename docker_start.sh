#!/bin/bash
current_dir=$(dirname $(readlink -f $0))
if [ $1 ]
then
    port=$1
else
    port=8080
fi
echo "项目地址：${current_dir}"
echo "web服务绑定的端口：${port}"
pid_list=`lsof -i:${port} | grep -v PID | awk '{print $2}'`
if [ $# != 0 ]
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
    tail -f /dev/null
else
    if [ "$pid_list" ]
    then
        kill -9 ${pid_list}
    fi
    echo 'dev'
    `cp ${current_dir}/config/dev_settings.py ${current_dir}/base/settings.py`
    `nohup python3 manage.py runserver 0.0.0.0:${port} > /dev/null 2>&1 &`
    echo "web服务启动成功..."
    tail -f /dev/null
fi