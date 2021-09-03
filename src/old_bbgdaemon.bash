#!/usr/bin/env bash
# Copyright (C) <2021>  Giuseppe Marco Randazzo <gmrandazzo@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DIRNAME="/home/marco/BBG/src"
MODEL="/home/marco/BBG/src/ARMv7_models/model_20210902/"
TOLLERANCE=0.45
EXCLUDED_LOGS=(gmrnxtcl.access.log)


function inlist() {
    item=${1}
    lst=${2}
    for v in ${lst[@]}; do
	    if [ ${item} == ${v} ]; then
                echo 1
		exit
	    else
		continue
	    fi
    done
    echo 0
}

function bbgdaemon () {
    tail -fn0 ${1} | while read line ; do
        # 1) Get the URL and make the inference
        P=`python3 $DIRNAME/parse.py "${line}"`
        IP=`echo ${P} | cut -d "|" -f 1`
        URL=`echo ${P} | cut -d "|" -f 2`

        R=`python3 $DIRNAME/predict.py "${URL}" "${MODEL}"`
        PRED=`echo ${R} | cut -d " " -f 1`
        STDEV=`echo ${R} | cut -d " " -f 2`
        # 2) Emit fail2ban rule
        if [ $(echo $PRED'<'$TOLLERANCE | bc -l) -eq 1 ]; then
            logger "BBG SUSPICIOUS ${IP} ${URL}"
        else
            logger "BBG TRUSTFUL ${IP} ${URL}"
        fi
    done
}

# Scan all the nginx logs and start a child service
for log in /var/log/nginx/*.access.log; do 
    logname=`basename ${log}`
    r=$(inlist ${logname} ${EXCLUDED_LOGS})
    if [ "${r}" -eq 1 ]; then
        continue
    else
        bbgdaemon $log &
    fi
done


