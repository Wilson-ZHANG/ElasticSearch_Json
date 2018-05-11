
# coding: utf-8
import requests
import io
import sys


url ='http://118.89.234.98:9200/insu/health/_search?q=company:幸福'
newname = 'x.json'
save = open(newname, 'a+', encoding='utf-8')

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码
html = requests.get(url)
html.encoding = 'utf-8' #这一行是将编码转为utf-8否则中文会显示乱码。
print(html.text,file=save)