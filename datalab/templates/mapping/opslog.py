OPSLOG_MAPPING = {
    "mappings": {
        "opslog": {
            "_all": {
                "enabled": "false"
            },
            "properties": {
                "@timestamp": {
                    "type": "date"
                },
                "envname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errlocation": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errseverity": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errstack": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "errstackidx": {
                    "type": "long"
                },
                "keywname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 100
                        }
                    }
                },
                "keywvalue": {
                    "type": "float"
                },
                "loghost": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "logtext": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "module": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                },
                "procid": {
                    "type": "long"
                },
                "procname": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 20
                        }
                    }
                }
            }
        }
    },
    "settings": {
        "index.number_of_shards": "20",
        "index.number_of_replicas": "0",
        "index.query.default_field": "logtext"
    }
}

