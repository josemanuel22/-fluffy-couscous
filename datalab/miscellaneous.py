import re, math

def clean_for_kairos(s):
    """
    Simple kairos parser utility funcion for insert

    :param s: a simple string value to insert in kairos
    :type s: string
    :return: value string parsed ready to insert in kairos
    """
    removelist = r'[^A-Za-z0-9./_-]'
    return re.sub(removelist,"", s)