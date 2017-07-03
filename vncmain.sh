#!/bin/bash
# Set them to empty is NOT SECURE but avoid them display in random logs.
export VNC_PASSWD=''
export USER_PASSWD=''

export TERM=linux

function is_running() {
    process=`ps aux | grep 'CQ.\.exe'`
    if [ "$process" == '' ]; then
        echo 0
    else
        echo 1
    fi
}

function run() {
    wine ~/coolq/CQ?.exe /account $COOLQ_ACCOUNT
}

function join() {
    while [ $(is_running) == 1 ]; do
        sleep 0.5
    done
}

function request() {
    echo `curl -I -X GET --max-time 3 http://127.0.0.1:$port/get_login_info 2>/dev/null | head -n 1 | cut -d$' ' -f2`
}

function shutdown_container() {
    pid=`ps aux | grep 'CQ.\.exe' | awk '{print $2}'`
    kill -9 $pid
    pid=`ps aux | grep 'vncmain.sh' | awk '{print $2}'`
    kill -9 $pid
}

function check_http_api() {
    port="$CQHTTP_PORT"
    if [ "$port" == '' ]; then
        port=5700
    fi
    fail_count=0
    while true; do
        ret=$(request)
        echo 'curl result' $ret
        if [ "$ret" == '' ]; then
            # 请求失败，HTTP API 未启动或已经挂了
            # 在运行中有可能因为快速重启导致 HTTP API 暂时失联
            # 但由于 join 可能未跳出，我们无法知道是为什么，因此允许在运行中失败若干次
            # 这会导致从插件崩溃，到容器退出的理论最坏时间是 30 秒
            fail_count=$(($fail_count+1))
            echo 'failed' $fail_count 'times'

            if [ "$fail_count" == 5 ]; then
                # 确实挂了，直接退出容器
                echo 'The HTTP API plugin is down, stopping...'
                shutdown_container
            fi
        else
            # 请求成功，HTTP API 正常运行
            fail_count=0
        fi
        # 每 3 秒请求一次
        sleep 3
    done
}

check_http_api &

while true; do
    # 检查进程是否存在
    if [ $(is_running) == 0 ]; then
        # 当前没再运行，自动启动，下面的 run 会阻塞直到进程退出
        echo 'Starting CoolQ...'
        run
    else
        # 当前正在运行，并且不是从上面的 if 块运行的，则等待
        echo 'CoolQ is running...'
        join # 这里的 join 可能无法在快速重启的情况下跳出，因为启动新进程的时间可能小于 join 轮询的时间
    fi
    # 进程退出后等待 3 秒后再检查，避免酷 Q 自动或快速重启导致误判
    # 这个时间不用特别长，因为酷 Q 的快速重启会很快就启动新的进程
    sleep 3
done