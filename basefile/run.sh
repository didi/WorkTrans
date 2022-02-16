source ~/.bash_profile
source ~/.bashrc
workdir=$(cd $(dirname $0); pwd)
echo "runsh:  $workdir"
nohup /bin/python3 ${workdir}/run.py  >> ${workdir}/log/run.log &