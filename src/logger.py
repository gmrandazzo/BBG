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
import logging
import logging.handlers
import sh

def create_listener(logfile="/var/log/nginx/access.log"):
    #using sh.tail as listener
    for line in sh.tail("-f", logfile, _iter=True):
        yield line.strip()

def create_logger(app_name, log_level=logging.INFO):
    # create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)

    # create syslog logger handler
    sh = logging.handlers.SysLogHandler(address='/dev/log')
    sh.setLevel(log_level)
    sf = logging.Formatter('%(name)s: %(message)s')
    sh.setFormatter(sf)
    logger.addHandler(sh)

    return logger


def demo1():
    log = create_logger(
        app_name="MY-TEST-APP",
        log_level=logging.DEBUG)

    log.debug("hello debug from my sample app")
    log.debug("hello error from my sample app")
    log.info("hello info from my sample app")


def demo2():
    listener = create_listener("/var/log/nginx/access.log")
    for item in listener:
        print(item)



if __name__ in "__main__":
    demo1()
    demo2()





