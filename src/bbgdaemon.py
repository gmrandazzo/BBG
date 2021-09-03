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
from pathlib import Path
from parse import parse_line
from predict import load_models
from predict import predict
from logger import create_logger
from logger import create_listener

class BBGDaemon(object):
    def __init__(self,):
        self.banned_ip_lst = []
        self.treshold=0.45

    def run(self):
        # enabled = self.read_site_enabled()
        enabled=["/var/log/nginx/gmrandazzo.access.log"] 
                #"/var/log/nginx/gmrnxtcl.access.log"]
        listener = self.global_listener(enabled)
        log = create_logger(app_name="BBG")
        model, header = load_models("/home/marco/BBG/src/ARMv7_models/model_20210903/") #"/var/opt/bbg_model")
        for msg in listener:
            if "==>" in msg or len(msg) ==0:
                continue
            else:
                d = parse_line(msg)
                if self.already_banned(d["ip"]):
                    continue
                else:
                    res = predict(d["request-string"], model, header)
                    if res["prediction"] > self.treshold:
                        log.info("TRUSTED %s %s" % (d["ip"], d["request-string"]))
                    else:
                        log.info("SUSPICIOUS %s %s" % (d["ip"], d["request-string"]))
                        self.banned_ip_lst.append(d["ip"])
        return

    def already_banned(self, ip):
        return ip in self.banned_ip_lst

    def read_conf(self, fconf):
        conf = {}
        f = open(fconf, "r")
        for line in f:
            v = str.split(line.strip(), ",")
            if len(v) == 2:
                conf[v[0]] == v[1]
            else:
                continue
        f.close()
        return conf

    def read_site_enabled(self,):
        enabled = []
        p = Path("/etc/bbg/enabled/")
        for fconf in p.glob("*/**.conf"):
            conf = self.read_conf(fconf)
            for key in conf.keys():
                if conf[key] == "enabled":
                    enabled.append(key)
                else:
                    continue
        return enabled

    def global_listener(self, enabled):
        args = []
        for site in enabled:
            args.append("-fn0")
            args.append("%s" % (site))
        return create_listener(args)

def main():
    bbgdaemon = BBGDaemon()
    bbgdaemon.run()

if __name__ in "__main__":
    main()
