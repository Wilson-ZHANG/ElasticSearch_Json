import os
import os.path

ext_from = '.blv'


read_file_dir = "D:\KG\QING\\to_attr_get"

files = os.listdir(read_file_dir) # 列出当前目录下所有的文件

for filename in files:
    newname = "attr_get_"+filename  #改新的新扩展名
    os.chdir(read_file_dir)
    os.rename(filename,newname)
    print(os.path.basename(filename)+' -> '+ os.path.basename(newname))