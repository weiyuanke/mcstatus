#!/usr/bin/env python
# encoding: utf-8
# author: weiyuanke123@gmail.com
import sys
import os
import time
import getopt
import re


#采集的数据hoststr ->[var_dict, var_dict, ....]
datadict = {}

def Usage():
    print 'mcstatus.py usage:'
    print "-c, --conf: 'host=192.168.1.1port=11211'"

def parse_host_str(hoststr):
    matchobj = re.match(r'host=(.*)port=(.*)', hoststr)
    if not matchobj:
        return None
    host = matchobj.group(1).strip()
    port = matchobj.group(2).strip()
    return (host, port)

#hoststr事例: host=10.103.38.141port=3306user=accountpassword=`c2#^@j_
def sample_host(host, port):
    var_dict = {}
    cmd = "echo stats|nc "+host+" " + port
    output = os.popen(cmd).read().strip();
    for line in output.split('\n'):
        line_split = re.split('\t| ', line);
        if len(line_split) == 3:
            var_dict[line_split[1]] = line_split[2]
    if datadict.has_key(host):
        datadict[host].append(var_dict)
    else:
        datadict[host] = [var_dict]

def show():
    for key in datadict.keys():
        if len(datadict[key]) < 2:
            continue
        time_per = int(datadict[key][-1]['uptime']) - int(datadict[key][-2]['uptime'])
        evictions_qps = (int(datadict[key][-1]['evictions']) - int(datadict[key][-2]['evictions']))/time_per
        cmd_get_qps = (int(datadict[key][-1]['cmd_get']) - int(datadict[key][-2]['cmd_get']))/time_per
        cmd_set_qps = (int(datadict[key][-1]['cmd_set']) - int(datadict[key][-2]['cmd_set']))/time_per
        get_hits = int(datadict[key][-1]['get_hits'])
        get_miss = int(datadict[key][-1]['get_misses']);
        get_rat = (get_hits * 1.0) / (get_hits + get_miss)
        print "host\tevictions\tcurr_con\tget\tset\thitrat"
        print key+"\t"+str(evictions_qps)+"\t"+str(datadict[key][-1]['curr_connections'].strip())+"\t"+str(cmd_get_qps)+"\t"+str(cmd_set_qps)+"\t"+str(get_rat)

if __name__ == '__main__':
    hoststrs = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:n:')
    except getopt.GetoptError, err:
        Usage()
        sys.exit(2)
    for op, val in opts:
        if op == '-h':
            Usage()
            sys.exit(0)
        elif op == '-c':
            hoststrs = hoststrs + val.split('; ')
        elif op == '-n':
            num_of_iter = int(val)

    if len(hoststrs) == 0:
        Usage()
        sys.exit(0)

    for hoststr in hoststrs:
        (host, port) = parse_host_str(hoststr)
        sample_host(host, port)
    time.sleep(2)
    for hoststr in hoststrs:
        (host, port) = parse_host_str(hoststr)
        sample_host(host, port)
    show()


