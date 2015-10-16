#!/usr/bin/python2.7 -tt

import sys
import os
import re
import codeformatter
import sourcestyler
import constants
import dupfuns
from myutils import myfile
from myutils import mypatmat
from myutils import mymath
from myutils import general
from pysuffix import make_sa_lcp
import pandas as pd
from pygments.lexers import *
from collections import Counter



SYM_KEYS_SEP = '<THE_SYMBOL_KEYWORD_SEP>'
ENTRY_SEP = mypatmat.NEWLINES[0]

DUP_MEAN_FACTOR_GROUP_ONLY_IF = 1
XP_MEAN_FACTOR_GROUP_ONLY_IF = 1
INVALID_FILE = 1
INVALID_KEYS_SSYM_FILE = 2

KEYWORD_CONSTANT = 100

VARIABLE_PLACEHOLDER = chr(17)
STRING_PLACEHOLDER = chr(18)
TYPES_PLACEHOLDER = chr(20)
DIGITS_PLACEHOLDER = chr(19)
SPECIAL_PLACEHOLDER = [VARIABLE_PLACEHOLDER,STRING_PLACEHOLDER,DIGITS_PLACEHOLDER,TYPES_PLACEHOLDER]

SINGLE_QUOTE_DELIMITER = "'"
DOUBLE_QUOTE_DELIMITER = '"'

MAGIC_NUMBERS_MIN = 3
NOT_MAGIC_NUMBERS = [0,1,-1,0.0,1.0,-1.0]

SMALL_IDENTIFIER_IF_LEQ = 4

MAX_IDENTIFIERS_TO_PRINT = 20

WE_WONT_SAY_THESE_ARE_IDENTIFIERS = [ 'main', 'int', 'float', 'double', 'long' 'bool' ]

def get_features(kewords_special_symbols_fn,source_fn,source_str,block_comment_regex,line_comment_regex,numbers_regex,strings_regex,find_words,find_regexes,types_regex,keywords_for_not_general,pygments_lexer):
  keys_dt,ssym_dt = get_keys_ssym_dicts(kewords_special_symbols_fn)

  if (source_str == None or len(source_str)==0) and source_fn != None and len(source_fn)>0:
    source_str = myfile.get_text(source_fn)

  if source_str is None or len(source_str)<=1: # INVALID_FILE
    return (None,None)
 
  source_str = source_str + mypatmat.NEWLINES[0] # prime
  initLOC = mypatmat.count_each_symbol(source_str,[mypatmat.NEWLINES[0]])[0]

  source_str = mypatmat.remove_double_newline(source_str)
  source_str = re.sub(r'\\.',' ',source_str) # remove escaped symbols for simplicity
  source_str = source_str.replace(SINGLE_QUOTE_DELIMITER,DOUBLE_QUOTE_DELIMITER)  # treat chars as strings for simplicity

  theoriginal_str = source_str

  (block_comments, source_str) = mypatmat.strip_regex_but_keep_newlines(source_str,block_comment_regex)
  (line_comments, source_str) = mypatmat.strip_regex_but_keep_newlines(source_str,line_comment_regex) 

  num_block_comments = len(block_comments)
  num_line_comments = len(line_comments)
  total_comment_lines = mypatmat.count_each_symbol(mypatmat.NEWLINES[0].join(block_comments),[mypatmat.NEWLINES[0]])[0] + num_line_comments
  comment_lines_div_orig_loc = total_comment_lines / float(max(1,initLOC))

  source_w_just_spaces_and_newlines = mypatmat.replace_whitespace_with_single_space(source_str,except_newline=True)
  source_w_just_spaces = source_w_just_spaces_and_newlines.replace('\n',' ') # after this, we can match more, but we still maintain where the newlines are in 

  (orig_sa,orig_lcp)=make_sa_lcp.get_sa_lcp(source_w_just_spaces)
  stats_orig_lcp = mymath.get_list_describe_pandas_features(orig_lcp)
  duplications = dupfuns.get_dup_groups(DUP_MEAN_FACTOR_GROUP_ONLY_IF,stats_orig_lcp[mymath.INDEX_OF_MEAN],orig_sa,orig_lcp,source_w_just_spaces_and_newlines,pygments_lexer,SPECIAL_PLACEHOLDER)
  orig_dup_mean_div_count = stats_orig_lcp[mymath.INDEX_OF_MEAN] / float(max(1,stats_orig_lcp[mymath.INDEX_OF_COUNT]))
  
  (temp, linenos_arr) = mypatmat.get_linenos_and_remove_newlines(source_w_just_spaces_and_newlines)
  origLOC = mypatmat.count_each_symbol(source_str,[mypatmat.NEWLINES[0]])[0]
  myLOC = len(set(linenos_arr))
  

  # X-parameterized transformation
  (sourcemod,tokens,tokens_str,variables,strings,digits,types) = get_data_str(source_str,keys_dt,ssym_dt,strings_regex,numbers_regex,types_regex)

  (thereconstructed_str,linenos_for_xp_dup) = reconstruct_the_original(theoriginal_str,tokens_str,variables,VARIABLE_PLACEHOLDER,strings,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER)

  (xp_sa,xp_lcp)=make_sa_lcp.get_sa_lcp(tokens_str)
  stats_xp_lcp = mymath.get_list_describe_pandas_features(xp_lcp)
  
  symbol_counts_in_string_ith_base_0 = mypatmat.get_symbol_counts_in_string_ith_base_0(tokens_str)
  
  counts_word = mypatmat.dirty_search_for_num_occ_of_pat_lst_in_text(tokens_str,find_words,pat_whitespace_to_left=True,pat_whitespace_to_right=False,pattern_lst_is_regex=False)
  counts_regex = mypatmat.dirty_search_for_num_occ_of_pat_lst_in_text(tokens_str,find_regexes,pat_whitespace_to_left=True,pat_whitespace_to_right=False,pattern_lst_is_regex=True)
  counts_not_general_keywords = mypatmat.dirty_search_for_num_occ_of_pat_lst_in_text(tokens_str,keywords_for_not_general,pat_whitespace_to_left=True,pat_whitespace_to_right=False,pattern_lst_is_regex=False)

  generality_flag = 1
  if sum(counts_not_general_keywords) > 0:
    generality_flag = 0

  xp_duplications = dupfuns.get_dup_groups(XP_MEAN_FACTOR_GROUP_ONLY_IF,stats_xp_lcp[mymath.INDEX_OF_MEAN],xp_sa,xp_lcp,tokens_str,pygments_lexer,SPECIAL_PLACEHOLDER,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER,linenos_for_xp_dup,ssym_dt)
  xp_dup_mean_div_count = stats_xp_lcp[mymath.INDEX_OF_MEAN] / float(max(1,stats_xp_lcp[mymath.INDEX_OF_COUNT]))

  (total_literals_count, unique_literals_count, magic_numbers_count, magic_numbers_per_number, magic_numbers_display) = get_magic_number_info(digits)

  ( identifier_avg_length, count_small_identifier, count_small_identifier_percent, identifier_creativity_uppercase_underscore_count, identifier_creativity_uppercase_underscore_percent, poor_identifier_display ) = get_identifier_info(variables)

  
  


  # #################
  # BEGIN gather features and return them with header
  # #################
  
  FEATURES_HEADER = ['language','filename']
  features_val = [constants.C_LANGUAGE[0],source_fn]

  FEATURES_HEADER += mypatmat.prepend_and_or_append_str_to_strlst(mymath.DESCRIBE_FEATURES_HEADER,prependstr='orig_dup_')
  features_val += stats_orig_lcp

  FEATURES_HEADER += mypatmat.prepend_and_or_append_str_to_strlst(mymath.DESCRIBE_FEATURES_HEADER,prependstr='xp_dup_')
  features_val += stats_xp_lcp

  FEATURES_HEADER += ['init_loc','orig_loc','my_loc']
  features_val += [initLOC, origLOC, myLOC]

  FEATURES_HEADER += mypatmat.prepend_and_or_append_str_to_strlst(find_words,prependstr='word_count_')
  features_val += counts_word

  FEATURES_HEADER += mypatmat.prepend_and_or_append_str_to_strlst(find_regexes,prependstr='regex_count_')
  features_val += counts_regex

  FEATURES_HEADER += ['count_line_comments','count_block_comments','count_total_comment_lines','comment_lines_div_orig_loc']
  features_val += [ num_line_comments, num_block_comments, total_comment_lines, comment_lines_div_orig_loc ]

  FEATURES_HEADER += ['total_literals_count', 'unique_literals_count', 'magic_numbers_count', 'magic_numbers_per_number']
  features_val += [ total_literals_count, unique_literals_count, magic_numbers_count, magic_numbers_per_number ]

  FEATURES_HEADER += ['identifier_avg_length', 'count_small_identifier', 'count_small_identifier_percent', 'identifier_creativity_uppercase_underscore_count', 'identifier_creativity_uppercase_underscore_percent']
  features_val += [ identifier_avg_length, count_small_identifier, count_small_identifier_percent, identifier_creativity_uppercase_underscore_count, identifier_creativity_uppercase_underscore_percent ]

  FEATURES_HEADER += ['orig_dup_mean_div_count', 'xp_dup_mean_div_count']
  features_val += [orig_dup_mean_div_count, xp_dup_mean_div_count]

  FEATURES_HEADER += ['generality_flag']
  features_val += [generality_flag ]

  # #################
  # END
  # #################

  return (FEATURES_HEADER, features_val, duplications, xp_duplications, poor_identifier_display, magic_numbers_display)






def get_identifier_info(identifiers): 
  identifier_avg_length=0
  count_small_identifier=0
  count_small_identifier_percent=0
  identifier_creativity_uppercase_underscore_count=0
  identifier_creativity_uppercase_underscore_percent=0
  poor_identifier_display='<table><tr><td style="border-bottom: 1px solid #000;"><b>Weak Identifiers</b></td></tr>'

  id_set = sorted(set(identifiers))

  tmp = []
  for i in id_set:
    li = len(i)
    identifier_avg_length += li
    if li <= SMALL_IDENTIFIER_IF_LEQ and i not in WE_WONT_SAY_THESE_ARE_IDENTIFIERS:
      count_small_identifier += 1
      if count_small_identifier <= MAX_IDENTIFIERS_TO_PRINT:
        tmp.append('<tr><td>'+i+'</td></tr>')
      elif count_small_identifier == MAX_IDENTIFIERS_TO_PRINT + 1:
        tmp.append('<tr><td>...</td></tr>')
    for letter in i:
      if ('A'<=letter and letter<='Z') or letter=='_':
        identifier_creativity_uppercase_underscore_count += 1
        break
  poor_identifier_display += ''.join(tmp)
  identifier_avg_length /= max(1,len(id_set))
  count_small_identifier_percent = count_small_identifier / float(max(1,len(id_set)))
  identifier_creativity_uppercase_underscore_percent = identifier_creativity_uppercase_underscore_count / float(max(1,len(id_set)))

  poor_identifier_display += '</table>'

  if count_small_identifier == 0:
    poor_identifier_display = ''

  return ( identifier_avg_length, count_small_identifier, count_small_identifier_percent, identifier_creativity_uppercase_underscore_count, identifier_creativity_uppercase_underscore_percent, poor_identifier_display )




def get_magic_number_info(digits):
  digits2 = digits
  total_literals_count = len(digits2)
  for i in xrange(len(digits2)):
    var = digits2[i]
    try:
      if var.count('.') == 1:
        digits2[i] = float(var)
      else:
        digits2[i] = int(var)
    except Exception as e:
        sys.stderr.write("get_magic_number_info(): Unexpected error:"+str(e))
        digits2[i] = 0
  unique_literals_count = len(set(digits2))
  digits2_set = Counter(digits2).most_common()
  magic_numbers_count = 0
  magic_numbers_display='<table><tr><td style="border-bottom: 1px solid #000;"><b>Hard-Coded Numbers&nbsp;&nbsp;&nbsp;&nbsp;</b> </td><td style="border-bottom: 1px solid #000;border-left: 1px solid #000;">&nbsp;&nbsp;&nbsp;&nbsp;</td><td style="border-bottom: 1px solid #000;"><b>Frequency</b></td></tr>'
  magic_numbers_and_freq = []
  tmp = []
  for (d,freq) in digits2_set:
    if freq>=MAGIC_NUMBERS_MIN and d not in NOT_MAGIC_NUMBERS:
      magic_numbers_count += 1
      tmp.append('<tr><td>'+str(d)+'</td><td style="border-left: 1px solid #000;"></td><td>'+str(freq)+'</td></tr>')
  magic_numbers_display += ''.join(tmp) + '</table>'
  if magic_numbers_count == 0:
    magic_numbers_display = ''
  magic_numbers_per_number = magic_numbers_count / float(max(1,len(digits2_set)))
  return (total_literals_count, unique_literals_count, magic_numbers_count, magic_numbers_per_number, magic_numbers_display)




def reconstruct_the_original(THE_ORIGINAL_STR,tokens_str,variables,variable_PLACEHOLDER,strings,string_PLACEHOLDER,digits,digit_PLACEHOLDER,types,types_PLACEHOLDER):
  origstr = []
  var_num = 0
  str_num = 0
  dig_num = 0
  types_num = 0
  orig_index = 0
  orig_str_len = len(THE_ORIGINAL_STR)
  orig_str_lineno = 1
  linenos = []

  for tok in tokens_str:
    i = tok 

    theval = ''
    foreach = False

    if len(i)==1:
      if ord(i)==ord(variable_PLACEHOLDER):
        theval = reconstruct_the_original_helper(variables,var_num)
        origstr.append(' '+theval)
        var_num += 1
      elif ord(i)==ord(string_PLACEHOLDER):
        theval = reconstruct_the_original_helper(strings,str_num)
        origstr.append(theval)
        str_num += 1 
      elif ord(i)==ord(digit_PLACEHOLDER):
        theval = str(reconstruct_the_original_helper(digits,dig_num))
        origstr.append(theval+' ')
        dig_num += 1
      elif ord(i)==ord(types_PLACEHOLDER):
        theval = str(reconstruct_the_original_helper(types,types_num))
        origstr.append(theval+' ')
        types_num += 1
      elif i == ' ':
        pass 
      else:
        theval = i
        origstr.append(i)
        foreach = True
    else:
      theval = i
      foreach = True
      origstr.append(theval)

    for thevalchar in theval:
      if thevalchar not in mypatmat.NEWLINES and thevalchar not in mypatmat.SPACES:
        while orig_index < orig_str_len:
          if THE_ORIGINAL_STR[orig_index] in mypatmat.NEWLINES:
              orig_str_lineno += 1
          if THE_ORIGINAL_STR[orig_index] == thevalchar:  
            orig_index += 1
            break
          orig_index += 1

    linenos.append(orig_str_lineno)

  return (''.join(origstr), linenos)


def reconstruct_the_original_helper(arr,arr_num):
  val = '?'
  if arr!=None and arr_num<len(arr):
    val = arr[arr_num]
  return val



def tokens_to_str(tokens,pretty_sep=''):
  tmp = []
  lgt = len(tokens)
  previous_was_also_keyword = False;
  for i in xrange(lgt):
    tok = tokens[i]
    if isinstance(tok,tuple):
      if len(tok) == 3 and tok[2]==KEYWORD_CONSTANT: # just a keyword
        if previous_was_also_keyword: tmp.append(' ')
        previous_was_also_keyword = True;
      else: previous_was_also_keyword = False;
      tmp.append(tok[0])
    else: # just a keyword
      previous_was_also_keyword = False
      tmp.append(tok)

  return pretty_sep.join(tmp)



def get_data_str(source,keys_dt,ssym_dt,STRINGS_REGEX,DIGITS_REGEX,TYPES_REGEX):
  tokens = []
  variables = []
  SPACE = mypatmat.SPACES[0]
  

  (strings_removed,source) = mypatmat.remove_all_in_between_on_same_line2(source,STRINGS_REGEX,replacewith=' '+STRING_PLACEHOLDER+' ')

  types_removed = []

  (digits_removed,source) = mypatmat.remove_all_in_between_on_same_line2(source,DIGITS_REGEX,replacewith=' '+DIGITS_PLACEHOLDER+' ')

  source = mypatmat.replace_whitespace_with_single_space(source)
  source = mypatmat.ensure_thissym_around_syms(source,ssym_dt,SPACE)
  
  token_lines = source.split(SPACE)
  

  pos_in_source = 0
  num = 0
  strings_num = 0
  digits_num = 0
  variables_num = 0
  types_num = 0
  for tok in token_lines:
    # symbol token
    if tok in ssym_dt:
      tokens.append((tok,pos_in_source))
    # keyword token
    elif tok in keys_dt:
      tokens.append((tok,pos_in_source,KEYWORD_CONSTANT))
    
    elif tok != None and len(tok)>0:
      if len(tok)==1:
        if ord(tok)==ord(DIGITS_PLACEHOLDER):
          tokens.append((DIGITS_PLACEHOLDER,pos_in_source,strings_num))
          strings_num += 1
        elif ord(tok)==ord(STRING_PLACEHOLDER):
          tokens.append((STRING_PLACEHOLDER,pos_in_source,digits_num))
          digits_num += 1
        elif ord(tok)==ord(TYPES_PLACEHOLDER):
          tokens.append((TYPES_PLACEHOLDER,pos_in_source,types_num))
          types_num += 1
        else: # variables (identifier)
          tokens.append((VARIABLE_PLACEHOLDER,pos_in_source,num))
          variables.append(tok)
          variables_num += 1
        num += 1
      elif tok!=SPACE:  # variable (identifier)
        tokens.append((VARIABLE_PLACEHOLDER,pos_in_source,num))
        num += 1
        variables.append(tok)
        variables_num += 1
    pos_in_source += len(tok) + 1 # + 1 for the SPACE

  tokens_str = tokens_to_str(tokens)

  


  return (source,tokens,tokens_str,variables,strings_removed,digits_removed,types_removed)






def get_keys_ssym_dicts(keys_spsym_fn):
  tmp = myfile.get_text(keys_spsym_fn)
  mtch = re.finditer(r''+SYM_KEYS_SEP,tmp)
  
  tmp = tmp.split(ENTRY_SEP)
  setkeys = False
  keys_dt = {}
  ssym_dt = {}
  for line in tmp:
    if line == SYM_KEYS_SEP:
      setkeys = True
      continue
    if line is not None and len(line.strip())>0:
      if setkeys:
        keys_dt[line]=True
      else:
        ssym_dt[line]=True
  return keys_dt,ssym_dt




  
