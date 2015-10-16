#!/usr/bin/python2.7 -tt


import constants
import indiv_lang_feature_extractor
import source_classifier
from myutils import myfile
import csv
import sys
import traceback





def style_rater(MODE,path,source_str,lang_exts,OUTPUT_FEATURES_TO_CSV_FN,CSV_DELIMITER,LIMIT_TO_NUM_FILES):
  ret = 0

  if MODE == constants.MODE_RETURN_PREDICTION_ON_SOURCE and source_str != None and len(source_str)>0 and lang_exts != None and len(lang_exts) > 0:
    header = None
    features = None
    predicted_class = ''
    try:
      return execute_by_lang_ext(MODE,'',source_str,lang_exts[0])
      
    except Exception as e:
        sys.stderr.write("style_rater(): Unexpected error:"+str(e))
    return (ret)

  elif MODE == constants.MODE_LOG_FEATURES_ON_FNS and path != None and len(path)>0:
    curr = 1
    ret = 0
    wroteheader = False
    validfns = myfile.get_file_names(path,lang_exts,LIMIT_TO_NUM_FILES)

    output_csv_file = open(OUTPUT_FEATURES_TO_CSV_FN,'w') 
    wr = csv.writer(output_csv_file, delimiter=CSV_DELIMITER)
    lgt = len(validfns)

    for fn in validfns:
      try:   
        (header,features) = execute_by_lang_ext(MODE,fn,'',lang_exts)
        if wroteheader==False and header!=None:
          wr.writerow(header)
          wroteheader=True
        if header != None: # not a fail code
          wr.writerow(features)
      except Exception as e:
        sys.stderr.write("style_rater(): Unexpected error:"+str(e))
      curr += 1
    output_csv_file.close()

  return (ret,'')



def execute_by_lang_ext(mode,fn,source_str,dont_have_file_just_use_lang_ext):
  header = None
  features = None
  predicted_class = ''
  ret = 0
  FEATURES_HEADER = None
  features = None

  # BEGIN LANGUAGES
  if myfile.has_extension(fn,constants.C_INFO[constants.LANGUAGES_SUPPORTED_EXTENSIONS]) or dont_have_file_just_use_lang_ext in constants.C_INFO[constants.LANGUAGES_SUPPORTED_EXTENSIONS]:
    (FEATURES_HEADER,features,duplications,xp_duplications,poor_identifier_display,magic_numbers_display) = indiv_lang_feature_extractor.get_features_for_C_lang(fn,source_str)
  elif myfile.has_extension(fn,constants.PYTHON_INFO[constants.LANGUAGES_SUPPORTED_EXTENSIONS]) or dont_have_file_just_use_lang_ext in constants.PYTHON_INFO[constants.LANGUAGES_SUPPORTED_EXTENSIONS]:
    (FEATURES_HEADER,features,duplications,xp_duplications,poor_identifier_display,magic_numbers_display) = indiv_lang_feature_extractor.get_features_for_PYTHON_lang(fn,source_str)
  # END LANGUAGES

  if FEATURES_HEADER == None or features == None:
    return (None,None)
  
  if mode==constants.MODE_LOG_FEATURES_ON_FNS:
    return (FEATURES_HEADER,features)

  if features != None and mode==constants.MODE_RETURN_PREDICTION_ON_SOURCE:
    (constants.PRO_CODE_PREDICTION,predicted_num,scorestr,matrix_of_stats) = source_classifier.get_prediction_info(FEATURES_HEADER,features,duplications,xp_duplications,poor_identifier_display,magic_numbers_display)
    return (constants.PRO_CODE_PREDICTION,predicted_num,scorestr,matrix_of_stats)

  return ret


