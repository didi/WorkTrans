#!/bin/bash
workspace=$(cd $(dirname $0) && pwd -P)
cd $workspace

## function
function build() {
    # do nothing
    echo -e "build ok"
}

function make_output() {
    # 创建临时目录
    local output="/tmp/soter/output"
    rm -rf $output &>/dev/null
    mkdir -p $output &>/dev/null
    # 填充output目录, output的内容即为待部署内容
    (
        rm -rf "./output" &&       # 删除 workspace下老的output目录
        cp -rf ./basefile ./control.sh init docker/Dockerfile $output &&      # 拷贝 必要的文件至临时output目录, 此处拷贝所有
        chmod a+x $output/control.sh &&
        chmod a+x $output/basefile/run.py &&
        mv $output ./ &&           # 将临时output目录 移动到workspace, 此即为我们的部署包内容
        echo -e "make output ok"
    ) || { echo -e "make output error"; exit 2; } # 填充output目录失败后, 退出码为 非0
}

##########################################
## main
## 其中,
##      1.进行编译
##      2.生成部署包output
##########################################
# 1.进行编译
build

# 2.生成部署包output
make_output

# 编译成功
echo -e "build done"
exit 0
