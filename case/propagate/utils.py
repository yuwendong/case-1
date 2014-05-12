from SSDB import SSDB
SSDB_HOST='202.108.211.4'
SSDB_PORT=8888
def forest_from_elevator(topic_id):
    try:
        ssdb = SSDB(SSDB_HOST, SSDB_PORT)
        result = ssdb.request('get', ['topic_%s' % str(topic_id)])
        if result.code == 'ok' and result.data:
            return result.data
        return None
    except Exception, e:
        print e
        return None
