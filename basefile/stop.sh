source ~/.bash_profile
source ~/.bashrc
a=`/sbin/lsof  -i :8867|awk '{print $2}'|grep -v 'PID'`
echo $a
OLD_IFS="$IFS"
IFS=" "
arr=($a)
IFS="$OLD_IFS"
for s in ${arr[@]}
do
    echo "stop pid:" $s
    kill -9  "$s"
done
