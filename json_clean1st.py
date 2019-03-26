# -*- coding: utf-8 -*-
filename = 'hospital_yaozhi.json'
f = open(filename, 'r')
newname = "yaozhi_clean1.json"
save = open(newname, 'w', encoding='utf-8')
line = f.readline()
#line.replace('}, ','},\n',1000000)
#print(line,file=save)
#print(line)
str = line.encode('utf-8').decode('utf-8').strip()
str = str.replace('}, ','},\n')
print(str,file=save)