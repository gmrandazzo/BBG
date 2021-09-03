#!/usr/bin/env python3
"""
Copyright (C) <2021>  Giuseppe Marco Randazzo <gmrandazzo@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import csv
from copy import copy
import sys
import string
import re

def parse_nginx_line(line):
    splits = []
    buff = ""
    quotes = 0
    brakets = 0
    for c in line:
        if "\"" == c:
            if quotes == 1:  # ON
                quotes = 0
                if len(buff) > 0:
                    splits.append(copy(buff))
                buff = ""
            else:
                quotes = 1
        elif "[" == c:
            if len(splits) < 4 and brakets == 0:
                brakets = 1
        elif "]" == c:
            if len(splits) < 4 and brakets == 1:
                brakets = 0
                if len(buff) > 0:
                    splits.append(copy(buff))
                buff = ""
        else:
            if quotes == 1:  # ON
                buff += c
            else:
                if " " == c and brakets == 0:
                    if len(buff) > 0:
                        splits.append(copy(buff))
                    buff = ""
                else:
                    buff += c
    return splits


def parse_nginx_line_(line):
    splits = []
    buff = ""
    v = str.split(line.strip(), " ")
    i = 0
    while i < len(v):
        if len(v) > 1:
            if v[i][0] == '"' and v[i][-1] != '"':
                # print("first char is \" on %s" % (v[i]))
                buff = v[i]
                for j in range(i+1, len(v)):
                    if v[j][-1] == '"':
                        buff += " "+v[j]
                        # print("add %s and stop" % (v[j]))
                        i = j+1
                        break
                    else:
                        buff += " "+v[j]
                        # print("add %s " % (v[j]))
                # print("Final buffer")
                # print(buff)
                # input()
                splits.append(buff)
            else:
                if v[i][0] == '[' and v[i+1][-1] == ']':
                    splits.append("%s %s" % (v[i], v[i+1]))
                    i += 2
                else:
                    splits.append(v[i])
                    i += 1
        else:
            splits.append(v[i])
            i += 1
    nsplits = []
    for i in range(len(splits)):
        nsplits.append(splits[i].replace('"', ""))
    return nsplits


def parse_line(line):
    d = None
    data = parse_nginx_line_(line)
    if len(data) != 9:
        print("problem with this line >> %s" % (line))
    v = str.split(data[4], " ")
    request = None
    request_str = None
    http_type = None
    if ("GET" == v[0] or
        "HELP" in v[0] or
        "PROPFIND" in v[0] or
        "POST" in v[0] or
        "PUT" in v[0] or
        "DELETE" in v[0] or
        "HEAD" in v[0] or
        "MOVE" in v[0] or
        "REPORT" in v[0] or
        "OPTIONS" in v[0] or
        "SEARCH" in v[0] or
        "PATCH" in v[0] or
        "MKCOL" in v[0] or
        "CONNECT" in v[0]):
        request = v[0]
        if "HTTP/" in v[-1]:
            request_str = " ".join(v[1:-1])
            http_type = v[-1]
        else:
            request_str = " ".join(v[1:])
            http_type = ""
    else:
        if v[0].isalpha():
            print("problem with %s" % (data[4]))
        request = ""
        request_str = None
        if "HTTP/" in data[4]:
            r = str.split(data[4], "HTTP/")
            request_str = r[0]
            http_type = "HTTP/"+r[1]
        else:
            request_str = data[4]
            http_type = ""

    d = {"ip": data[0],
         "user": data[2],
         "local-time": data[3],
         "request": request,
         "request-string": request_str,
         "http_type": http_type,
         "status": data[5],
         "http-user-agent": data[-1]
         }
    return d


def process_log_file(fin, fout):
    fi = open(fin, "r")
    fo = open(fout, "w")
    for line in fi:
        d = parse_line(line)
        if d is not None:
            s = ('"%s","%s","%s","%s","%s","%s"' % (d["local-time"],
                                                    d["ip"],
                                                    d["user"],
                                                    d["request"],
                                                    d["request-string"],
                                                    d["status"]))
            fo.write("%s\n" % (s))
    fi.close()
    fo.close()

def main():
    if len(sys.argv) == 2:
        res = parse_line(sys.argv[1])
        print("%s|%s|%s" % (res["ip"], res["request-string"], res["http_type"]))
    elif len(sys.argv) == 3:
        process_log_file(sys.argv[1], sys.argv[2])
    else:
        print("\nUsage: %s [input nginx log file] [parsed nginx file]" % (sys.argv[0]))
        print("       %s [nginx url]\n" % (sys.argv[0]))
    return 0

def demo():
    d = parse_nginx_line_('192.241.218.189 - - [22/Aug/2021:05:33:51 +0200] "GET / HTTP/1.1" 200 1082 "-" "Mozilla/5.0 zgrab/0.x"')
    print(d)

if __name__ in "__main__":
    main()
    # demo()
