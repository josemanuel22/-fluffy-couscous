import multiprocessing
import os, time
import glob

import math
import pandas as pd

from datalab import miscellaneous
from datalab.miscellaneous import clean_for_kairos
from datalab.src.importers.es_impoters import ES_BASIC_INDEXES, ES_BASIC_INDEXES_FILTERS, ES_BASIC_DOC_TYPES, \
    ES_BASIC_DOC_TYPES_FILTERS, ES_VLTLOG_OPSLOG_GENERATORS_DATA, es_insert_2
from datalab.src.importers.kairos_importers import kairos_insert
from datalab.src.loggers import datalab_loggers

datalab_logger_csvImporters_object = datalab_loggers.datalab_logger(my_format=datalab_loggers.DATALAB_LOGGER_FORMAT)
datalab_logger_csvInserters = datalab_logger_csvImporters_object.datalab_logger

def csv_vltlog_opslog_filter(data_point):
    try:
        x = float(data_point[8])
        if math.isnan(x) or math.isinf(x): return False
        return True
    except (ValueError, TypeError):
        return False

def csv_kairos_parser(data_point):
    data_point_parsed = {
        "name": clean_for_kairos(data_point[7]),
        "timestamp": int(time.mktime(time.strptime(str(data_point[1]), "%Y-%m-%d %H:%M:%S"))) * 1000,
        # kairosdb time in miliseconds
        "value": float(data_point[8]),
        "tags": {
            "proc": clean_for_kairos(data_point[4]),
            "env": clean_for_kairos(data_point[3]),
            "logh4pysost": clean_for_kairos(data_point[2]),
            "logtext": clean_for_kairos(str(data_point[9]).replace(" ", "_")),
        }
    }
    return data_point_parsed


def csv_kairos_parser(data_point):
    data_point_parsed = {
        "name": clean_for_kairos(data_point[7]),
        "timestamp": int(time.mktime(time.strptime(str(data_point[1]), "%Y-%m-%d %H:%M:%S"))) * 1000,
        # kairosdb time in miliseconds
        "value": float(data_point[8]),
        "tags": {
            "proc": clean_for_kairos(data_point[4]),
            "env": clean_for_kairos(data_point[3]),
            "logh4pysost": clean_for_kairos(data_point[2]),
            "logtext": clean_for_kairos(str(data_point[9]).replace(" ", "_")),
        }
    }
    return data_point_parsed


CSV_VLTLOG_OPSLOG_HEADER = ['typelog', 'tm', 'loghost', 'env', 'procname', 'procid', 'module', 'keyw', 'keyv',
                            'logtext', 'errstack', 'errstackidx', 'errlocation', 'errseverity']


def csv_kairos_import(path_to_csv, kairos_server="http://192.168.1.10:8080", header=CSV_VLTLOG_OPSLOG_HEADER,
                      csv_filter=csv_vltlog_opslog_filter, kairos_parser=csv_kairos_parser):
    chunksize = int((int(os.path.getsize(path_to_csv) + 1) / int(miscellaneous.CSV_NUM_BYTESXLINE)) / 4)
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1', usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                     na_filter=False, chunksize=chunksize)
    pool = multiprocessing.Pool(4)
    for chunk in df:
        r = pool.apply_async(kairos_insert,
                             args=[chunk.values, kairos_server, csv_filter, kairos_parser])  # ,callback=callBack)
        # result.append(r.get()) #RECOJER LOS RESULTADOS RALENTIZA X4
    pool.close()
    pool.join()
    return r.get()  # DEVOLVEMOS SOLO EL ULTIMO RESULTADO POR MOTIVOS DE VELOCIDAD. CON ESTE SE PUEDE DEDUCIR SI LA INSERCION FUE BIEN


def csv_es_import(path_to_csv, es_server, nproc_to_use=2, chunksize=50000, header=CSV_VLTLOG_OPSLOG_HEADER,
                  indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS, doc_types=ES_BASIC_DOC_TYPES,
                  doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS, es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1', usecols=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                     na_filter=False,
                     chunksize=chunksize)
    pool = multiprocessing.Pool(nproc_to_use)
    for chunk in df:
        result = pool.apply_async(es_insert_2, args=[es_server, chunk.values, indexes, indexes_filters, doc_types,
                                                     doc_types_filters, es_generator_data])  # ,callback=callBack)
    pool.close()
    pool.join()
    return result


def csv_import_file(path_to_csv, kairos_server, es_server, nproc_to_use=2, es_chunksize=50000,
                    header=CSV_VLTLOG_OPSLOG_HEADER,
                    kairos_filter=csv_vltlog_opslog_filter, kairos_parser=csv_kairos_parser,
                    indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS, doc_types=ES_BASIC_DOC_TYPES,
                    doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS, es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    df = pd.read_csv(filepath_or_buffer=path_to_csv, names=header, compression='gzip', na_values=[""],
                     parse_dates=['tm'], engine='c', encoding='latin-1', na_filter=False, chunksize=es_chunksize)

    pool = multiprocessing.Pool(nproc_to_use)
    for chunk in df:
        kairos_result = pool.apply_async(kairos_insert, args=[chunk.values, kairos_server, kairos_filter,
                                                              kairos_parser])  # ,callback=callBack)
        es_result = pool.apply_async(es_insert_2, args=[es_server, chunk.values, indexes, indexes_filters, doc_types,
                                                        doc_types_filters, es_generator_data])
    pool.close()
    pool.join()
    return (kairos_result, es_result)


def csv_datalab_import(path_to_csv, kairos_server, es_server, nproc_to_use=2, es_chunksize=50000, header=CSV_VLTLOG_OPSLOG_HEADER,
                       kairos_filter=csv_vltlog_opslog_filter, kairos_parser=csv_kairos_parser,
                       indexes=ES_BASIC_INDEXES, indexes_filters=ES_BASIC_INDEXES_FILTERS, doc_types=ES_BASIC_DOC_TYPES,
                       doc_types_filters=ES_BASIC_DOC_TYPES_FILTERS,
                       es_generator_data=ES_VLTLOG_OPSLOG_GENERATORS_DATA):
    files = glob.glob(path_to_csv)
    total = 0;
    total_inserted = 0;
    bash = 0
    for mi_file in files: total += os.path.getsize(mi_file)
    for f in files:
        s = time.time()
        result = csv_import_file(f, kairos_server, es_server, nproc_to_use, es_chunksize, header, kairos_filter, kairos_parser, indexes,
                                 indexes_filters, doc_types, doc_types_filters, es_generator_data)
        total_inserted += os.path.getsize(f);
        bash += os.path.getsize(f)
        if (bash / 1000000) > 20:  # Cada 100MB damos un respiro al sistema
            time.sleep(5)
            bash = 0
        # timeToFinish=int((((total/total_inserted)*(time.time()-s))+s)-time.time())/60
        datalab_logger_csvInserters.info("Inserted: %s file in %.2f secs, %.2f MB-%.2f MB" % (
            f, time.time() - s, total_inserted / 1000000.0, total / 1000000.0))
    return result
