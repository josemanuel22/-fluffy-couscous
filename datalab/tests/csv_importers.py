import unittest
import datetime
import requests, json

from datalab.src.connections.connections import DB_SESSION, db_connection_setUp, es_connection_setUp
from datalab.src.importers.csv_importers import csv_import_file, csv_datalab_import


def _es_is_data(es_object, index, doc_type, timestamp1, timestamp2):

    result = es_object.search(
        index=index,
        doc_type=doc_type,
        body={
          'query': {
            'range': {
                "@timestamp":{
                    "gte": timestamp1,
                    "lte": timestamp2
                }
            }
          }
        }
    )
    return result['hits']['total']

def _get_number_data_points(server, metric, start, finish):
    query = {
        "metrics": [
        {
            "tags": {},
            "name": metric,
            "aggregators": [
            {
                "name": "sum",
                "align_sampling": True,
                "sampling": {
                    "value": "1",
                    "unit": "milliseconds"
                },
            "align_start_time": False
            }]
        }],
        "cache_time": 0,
        "start_relative": {
        "value": start,
        "unit": "years"
        },
        "end_relative": {
            "value": finish,
            "unit": "years"
        }
    }
    response = requests.post(server + "/api/v1/datapoints/query", data=json.dumps(query))
    return int(response.json()['queries'][0]['sample_size'])

class MyTestCase(unittest.TestCase):
    def test_csv_insert_file(self):
        kairos_server="http://134.171.189.10:8080"
        es_server="http://134.171.189.10"
        path_to_csv = "/Users/user/PycharmProjects/datalab/datalab/tests/wt1tcs.2006-03-10.csv.gz"
        csv_import_file(path_to_csv, kairos_server, es_server)
        es_object= es_connection_setUp(es_server)
        start=datetime.datetime(2006,1,17,0,0,0)
        finish=datetime.datetime(2006,3,11,1,0,0)
        self.assertTrue(_es_is_data(es_object, index="vltlog", doc_type="log", timestamp1=start, timestamp2=finish))
        self.assertGreater(_get_number_data_points(kairos_server, "TEL.AMBI.TEMP", 12, 10), 0)

    def test_csv_datalab_import(self):
        kairos_server = "http://134.171.189.10:8080"
        es_server = "http://134.171.189.10"
        path_to_csv = "/Users/user/PycharmProjects/datalab/datalab/tests/wt1tcs.2006-0*-1*.csv.gz"
        csv_datalab_import(path_to_csv, kairos_server, es_server)
        start=datetime.datetime(2006,1,17,0,0,0)
        finish=datetime.datetime(2006,3,11,1,0,0)
        es_object = es_connection_setUp(es_server)
        self.assertTrue(_es_is_data(es_object, index="vltlog", doc_type="log", timestamp1=start, timestamp2=finish))
        self.assertGreater(_get_number_data_points(kairos_server, "TEL.AMBI.TEMP", 12, 10), 0)
        self.assertGreater(_get_number_data_points(kairos_server, "TEL.ACTO.FOCSIDE", 12, 10), 0)


if __name__ == '__main__':
    unittest.main()
