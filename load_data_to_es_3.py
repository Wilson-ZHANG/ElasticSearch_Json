#!/bin/env python
# -*- coding: utf-8 -*-
'''
使用bulk接口，curl提交
封装成class，方便调用
'''

import sys
import os
from optparse import OptionParser
from datetime import datetime
import subprocess as sub
import json


class loadDataToES:
    def __init__(self, field_desc, data_file, host='127.0.0.1', port='9200', index='test', doctype='others',
                 delimeter=',', tmp_file='/dev/shm/_tmp_data_to_es', cut_off=10000):
        self.host = host
        self.port = port
        self.index = index
        self.doctype = doctype
        self.delimeter = delimeter
        self.tmp_file = tmp_file
        self.field_desc = field_desc
        self.data_file = data_file
        self.header = '{"index":{"_index":"%s", "_type":"%s"}}' % (self.index, self.doctype)
        self.cut_off = cut_off
        self.url = 'http://%s:%s/_bulk' % (self.host, self.port)

    def load_data(self):
        '''
        expample data from the file:
        2015-09-24 09:17:29,memory_11601,123988
        '''
        self.body_list = []
        self.bulk = ''
        self.line_num = 0
        self.pretty_print('INFO: loadding data to es, host: %s, index: %s' % (self.host, self.index))
        self.parse_field()
        with open(self.data_file, 'r') as f_desc:
            for line in f_desc:
                self.do_line(line)
                self.line_num += 1
                if self.line_num >= self.cut_off:
                    self.bulk_content = '\n'.join(self.body_list)
                    self._load_data()
                    self.body_list = []
                    self.bulk = ''
                    self.line_num = 0
            if self.line_num > 0:
                self.bulk_content = '\n'.join(self.body_list)
                self._load_data()
        self.pretty_print('INFO: all lines parsed.')

    def do_line(self, line):
        fields = line.strip().split(self.delimeter)
        if len(fields) != self.field_len:
            self.pretty_print("ERROR: line %d not match fields" % line_num)
            return
        body_tmp = str(self.get_body(fields, self.fields_list))
        self.body_list.append(self.header)
        self.body_list.append(body_tmp.replace("'", '"'))

    def parse_field(self):
        fields_list = []
        fields_desc = self.field_desc.strip().split(self.delimeter)
        for item in fields_desc:
            items = item.split('|')
            fields_list.append([items[0], items[1]])
        self.fields_list = fields_list
        self.field_len = len(fields_list)

    def _load_data(self):
        open(self.tmp_file, 'w').write(self.bulk_content)
        p = sub.Popen(['curl', '-s', '-XPOST', self.url, '--data-binary', "@" + self.tmp_file], stdout=sub.PIPE)
        for line in iter(p.stdout.readline, b''):
            ret_dict = json.loads(line)
            if not ret_dict['errors']:
                self.pretty_print("INFO: %6s lines parseed with no errors, total cost %d ms." % (
                len(ret_dict['items']), ret_dict['took']))
            else:
                self.pretty_print("ERROR: %6s lines parseed with some errors, total cost %d ms." % (
                len(ret_dict['items']), ret_dict['took']))

    def pretty_print(self, str):
        print('%s %s' % (datetime.now(), str))

    def get_body(self, fields, fields_list):
        counter = 0
        body = {}
        while (counter < len(fields)):
            # if the data type is 'date', we will translate the value str to date
            # type
            if fields_list[counter][1] == 'date':
                body[fields_list[counter][0]] = self.translate_str_to_date(
                    fields[counter])
            # and if the data type is 'int', we translate it to int
            elif fields_list[counter][1] == 'int':
                body[fields_list[counter][0]] = self.translate_str_to_int(
                    fields[counter])
            elif fields_list[counter][1] == 'float':
                body[fields_list[counter][0]] = self.translate_str_to_float(
                    fields[counter])
            # other is defalut to be str
            else:
                body[fields_list[counter][0]] = fields[counter]
            counter += 1
        # print(my_body)
        return body

    def translate_str_to_date(self, date_str):
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            return date.isoformat()
        except:
            self.pretty_print("Unexpected error: %s" % (sys.exc_info()[0]))
            self.pretty_print("Failed to translate '%s' to date." % (date_str))
        return False

    def translate_str_to_int(self, num_str):
        try:
            return int(num_str)
        except:
            self.pretty_print("Failed to translate '%s' to int." % (num_str))
        return False

    def translate_str_to_float(self, num_str):
        try:
            return float(num_str)
        except:
            self.pretty_print("Failed to translate '%s' to int." % (num_str))
        return False


if __name__ == '__main__':
    '''
    example fields_desc:@timestamp|date,process|str,mem|int
    example lines in file:
    2015-09-24 09:17:29,memory_11601,203532
    2015-09-24 09:17:29,memory_11602,223112
    '''
    loader = loadDataToES(field_desc='@timestamp|date,process|str,mem|int', data_file='/root/scripts/in.data',
                          host='10.21.102.60', index='test')
    loader.load_data()