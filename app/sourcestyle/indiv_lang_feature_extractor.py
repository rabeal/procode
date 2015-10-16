#!/usr/bin/python2.7 -tt

import os
import general_feature_extractor
from pygments.lexers import CLexer
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from myutils import mypatmat



LANGFILES_PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0],'langfiles')


def get_features_for_C_lang(fn,source):
  KEYS_SPSEM_FN = os.path.join(LANGFILES_PATH,'c_keys_spsym.txt')
  COMMENT_BLOCK_REGEX = '(/\*(.|\n)*?\*/)'
  COMMENT_LINE_REGEX = '(//(.*|(\n|$)))'  
  C_WORDS_INTERESTED_IN = []#['printf','fprintf','sprintf','scanf','fscanf','fread','stdout','stderr','argc','argv','#define','#include','struct','extern','--','++','//','/*','*/','+=','-=','*=','/=','switch','case','break','continue','goto','rb','wb','ab','r','w','a','null','EOF','#if','#ifdef','#ifndef','#else','#elif','#endif']
  C_REGEXES_INTERESTED_IN = []#[(mypatmat.format_regex('return')+'\s+\w'),(mypatmat.format_regex('return')+'\s+\d+\s*[;]')]
  DIGITS_REGEX = '[^A-Za-z0-9_]([-+]?(\d*\.\d+|\d+))'#'[^A-Za-z0-9_]([-+]?(\d*\.\d+|\d+))' 
  STRINGS_REGEX = '(["](.*?)["])' 
  TYPES_REGEX = ''#'[^A-Za-z0-9_]((void)|(char)|(short)|(int)|(long)|(float)|(double))\s' ## beef up to handle unsigned, signed, and custom structs
  KEYWORDS_FOR_NOT_GENERAL = ['printf','scanf'] 

  return general_feature_extractor.get_features(KEYS_SPSEM_FN, fn, source, COMMENT_BLOCK_REGEX, COMMENT_LINE_REGEX, DIGITS_REGEX, STRINGS_REGEX, C_WORDS_INTERESTED_IN, C_REGEXES_INTERESTED_IN, TYPES_REGEX, KEYWORDS_FOR_NOT_GENERAL, CLexer())





def get_features_for_PYTHON_lang(fn,source):
  KEYS_SPSEM_FN = os.path.join(LANGFILES_PATH,'python_keys_spsym.txt')
  COMMENT_BLOCK_REGEX = "(['][']['](.|\n)*?['][']['])"
  COMMENT_LINE_REGEX = '(#(.*|(\n|$)))'  
  WORDS_INTERESTED_IN = []
  REGEXES_INTERESTED_IN = []
  DIGITS_REGEX = '[^A-Za-z0-9_]([-+]?(\d*\.\d+|\d+)[j]?)' # complex numbers too 
  STRINGS_REGEX = '(["\'](.*?)["\'])' 
  TYPES_REGEX = ''
  KEYWORDS_FOR_NOT_GENERAL = ['print','input','raw_input']

  return general_feature_extractor.get_features(KEYS_SPSEM_FN, fn, source, COMMENT_BLOCK_REGEX, COMMENT_LINE_REGEX, DIGITS_REGEX, STRINGS_REGEX, WORDS_INTERESTED_IN, REGEXES_INTERESTED_IN, TYPES_REGEX, KEYWORDS_FOR_NOT_GENERAL, PythonLexer())
















