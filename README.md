# inf510_project

First of all:

Please download all the data files, .py files and .ipynb file in one local folder. If you need to run 'HUANG_XUEWEI_hw5.py' to scrape data, please move the data files away. If you just want to get the results of data analysis, you can run the notebook, it will import the data files that you downloaded from github.

Secondly,

How to get data:

1. Please install two packages before running my file 'HUANG_XUEWEI_hw5.py'.

pip install python-google-places 

pip install -U googlemaps 


2. terminal command：

(My python is 3.7, maybe yours is just 'python')

python3.7 HUANG_XUEWEI_hw5.py --source=test

python3.7 HUANG_XUEWEI_hw5.py --source=remote(about 30-35min)

python3.7 HUANG_XUEWEI_hw5.py --source=local


3. If --source=test or remote, please delete all files（1 .db file, 4 .csv files） created by the command in #2 each time, then run the next command in #2.

If --source=local, you should only delete the .db file, the command will get data from the 4 local csv files.


Finally,

How to get analysis results:

Run the notebook(about 2min)
