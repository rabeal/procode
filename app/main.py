#!/usr/bin/python2.7 -tt


import sys
from sourcestyle import sourcestyler
from sourcestyle import constants


def main(mode=constants.MODE_LOG_FEATURES_ON_FNS, SEARCH_FILES_IN_PATH='', source_str='', lang_exts=constants.C_LANGUAGE, OUTPUT_FEATURES_TO_CSV_FN='', CSV_DELIMITER=',', LIMIT_TO_NUM_FILES=-1):
  try:
    return sourcestyler.style_rater(mode,SEARCH_FILES_IN_PATH,source_str,lang_exts,OUTPUT_FEATURES_TO_CSV_FN,CSV_DELIMITER,LIMIT_TO_NUM_FILES)
  except Exception as e:
    sys.stderr.write("main(): Unexpected error:"+str(e))
    return (None,None,None)



if __name__=='__main__':
  ret = main() 
  print ret


