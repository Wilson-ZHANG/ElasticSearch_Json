from pymongo import MongoClient
from elasticsearch import Elasticsearch, helpers
import datetime

# 一次同步的数据量，批量同步
syncCountPer = 100000

# Es 数据库地址
es_url = 'http://172.16.7.107:9200/'

# mongodb 数据库地址
mongo_url='172.16.1.99:27017'

# mongod 需要同步的数据库名
DB = 'beauty'
# mongod 需要同步的表名
COLLECTION = '20171120'

count = 0

if __name__ == '__main__':
    es = Elasticsearch(es_url)
    client = MongoClient(mongo_url)
    db_mongo = client[DB]
    syncDataLst = []
    mongoRecordRes = db_mongo.find()
    for record in mongoRecordRes:
        count += 1
        # 因为mongodb和Es中，对于数据类型的支持是有些差异的，所以在数据同步时，需要对某些数据类型和数据做一些加工
        # 删掉 url 这个字段
        record.pop('url', '')
        # Es中不支持 float('inf') 这个数据， 也就是浮点数的最大值
        if record['rank'] == float('inf'):
            record['rank'] = 999999999999

        syncDataLst.append({
            "_index": DB,               # mongod数据库 == Es的index
            "_type": COLLECTION,        # mongod表名 == Es的type
            "_id": record.pop('_id'),
            "_source": record,
        })

        if len(syncDataLst) == syncCountPer:
            # 批量同步到Es中，就是发送http请求一样，数据量越大request_timeout越要拉长
            helpers.bulk(es, 
                         syncDataLst, 
                         request_timeout = 180)
            # 清空数据列表
            syncDataLst[:]=[]
            print(f"Had sync {count} records at {datetime.datetime.now()}")
    # 同步剩余部分
    if syncDataLst:
        helpers.bulk(es, 
                     syncDataLst, 
                     request_timeout = 180)
        print(f"Had sync {count} records rest at {datetime.datetime.now()}")