#!/usr/bin/env python  
# -*- coding: utf-8 -*-
"""
@author: zhangslob
@file  : test_csv.py
@time  : 2019-06-15
@desc  :
         
"""

import csv

with open('employee_file.csv', mode='w', newline='', encoding='utf-8-sig') as f:
    employee_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    employee_writer.writerow(['name', 'account', 'November'])
    employee_writer.writerow(['John Smith', 'Accounting', 'November'])
    employee_writer.writerow(['Erica Meyers', 'IT', 'March'])