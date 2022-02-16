#!/usr/bin/env bash

mkdir -p /home/xiaoju/data1/woqu/logs
rm -rf /home/xiaoju/woqu/logs
ln -s /home/xiaoju/data1/woqu/logs /home/xiaoju/woqu/logs
chown -R xiaoju.xiaoju /home/xiaoju/data1/
