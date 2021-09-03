# MAchine LEarning-Based BAnning 

MALEBBA is an ML framework that analyzes nginx access logs
and predicts if the user connected to the web server may have bad intentions.
MALEBBA then produces a log file connected with fail2ban to ban bad IP.

License
=======
GPLv3

Dependencies
============

    - python3
    - pandas
    - xgboost
    - numpy
    - scikit-learn
    - sh
    - pickle
    - fail2ban
    - rsyslog

Install
=======

1) Login as root: su -

2) Clone the code on a directory that you want: git clone https://github.com/gmrandazzo/MALEBBA.git

Usage
=====

1) Extract data from your web server and annotate it manually defining:
   1: good URLs
   0: bad URLs
   For the extraction collect all your logs into /var/lib/nginx/*.access.log* and put all of them in one file

2) Parse all the log using the parse.py script
   parse.py all.log log_parsed.csv

3) Open the log_parsed.csv, copy the URLs column into another file and annotate manually the good (1)  and bad urls (0).   
   Save the URLs and the annotated column file into a csv file (i.e. dataset.csv)
   Here an example:
   URLs,target
   /index.php?pageid=home,1
   /hahhuidasuias6asdoajhsdoiaiuhsdasdkjajsd6,0
   ...

4) Produce features from the URLs and previous annotated file: urlfeaturizer.py dataset.csv dataset.features.target.csv
  

5) Train the model: train.py dataset.features.target.csv out_model
   Check the training results and see if classification exceed 0.90 in Precision-Recall Average Area and Accuracy score.

6) Modify the path of malebbadaemon.bash by editing the DIRNAME and MODEL paths.   
   If you want, you can modify also the tollerance treshold.
   vim src/malebbadaemon.bash

7) Copy into fail2ban the filter and the jail:
   cp src/fail2ban/filter.d/malebba.conf /etc/fail2ban/filter.d/bbg.conf
   cp src/fail2ban/jail.d/malebba.conf /etc/fail2ban/jail.d/bbg.conf
   Modify the jail using your preferred parameters.
  
8) Copy the systemd service file and modify the MALEBBA path
   cp src/systemd/system/malebba.service /etc/systemd/system/bbg.service
   vim /etc/systemd/system/malebba.service

9) Install the systemd services and run it.

10) Enjoy how many bad guys are now banned using ML.


Developer
=========
Giuseppe Marco "zeld" Randazzo <gmrandazzo AT gmail DOT com>


