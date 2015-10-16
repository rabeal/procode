#!/usr/bin/python2.7 -tt


import re


NEWLINES = ['\n','\r']
SPACES = [' ','\t']



def extract_digits(text,replacewith=''):
   REGEX = '[^_0-9]([-+]?(\d*\.\d+|\d+))' 
   replaced = get_first_element_of_tuples(re.findall(r''+REGEX,text))
   newstr = re.sub(r''+REGEX, r''+replacewith, text)
   return (replaced, newstr)


def get_loc_of_next_such_sym(text,start_here,find_char_in_this=None,gobble_these_chars=None):
  found_at = start_here
  found = False
  if find_char_in_this is not None:
    while text[found_at] not in find_char_in_this:
      found_at += 1
    if found_at<len(text) and text[found_at] in find_char_in_this:
      found = True
  if gobble_these_chars is not None:
    while text[found_at] in gobble_these_chars:
      found_at += 1
  return found, found_at


def remove_all_in_between_on_same_line(text,startregex,endregex,replacewith=''):
   REGEX = '('+startregex+'(.*?)'+endregex+')' #don't be greedy, take the first match
   replaced = get_first_element_of_tuples(re.findall(r''+REGEX,text))
   newstr = re.sub(r''+REGEX, r''+replacewith, text)
   return (replaced, newstr)


def remove_all_in_between_on_same_line2(text,REGEX,replacewith=''):
   replaced = get_first_element_of_tuples(re.findall(r''+REGEX,text))
   newstr = re.sub(r''+REGEX, r''+replacewith, text)
   return (replaced, newstr)


def remove_all_in_between_on_same_line2_UNICODE(text,REGEX,replacewith=''):
   replaced = get_first_element_of_tuples(re.findall(ur''+REGEX,text))
   newstr = re.sub(ur''+REGEX, ur''+replacewith, text)
   return (replaced, newstr)


def remove_all_in_between_but_keep_newlines(text,startregex,endregex):
   newstr = re.sub(r'('+startregex+'(.|\n)*'+(endregex)+')', lambda m: '\n'*count_each_symbol(m.group(),['\n'])[0], text)
   return newstr


def strip_comments_but_keep_newlines(text,start_block_regex,end_block_regex,start_line_regex):
  COMMENT_BLOCK = '('+start_block_regex+'(.|\n)*?'+end_block_regex+')'
  COMMENT_LINE = '('+start_line_regex+'(.*|(\n|$)))'  
  COMMENT = COMMENT_BLOCK+'|'+COMMENT_LINE
  block_comments = get_first_element_of_tuples(re.findall(r''+COMMENT_BLOCK,text))
  line_comments = get_first_element_of_tuples(re.findall(r''+COMMENT_LINE,text))
  return ( block_comments, line_comments, re.sub(r''+COMMENT,lambda m: '\n'*count_each_symbol(m.group(),['\n'])[0],text) )


def strip_regex_but_keep_newlines(text,regex):
  replaced_vals = get_first_element_of_tuples(re.findall(r''+regex,text))
  newstr = text
  if replaced_vals != None and len(replaced_vals)>0:
    newstr = re.sub(r''+regex,lambda m: '\n'*count_each_symbol(m.group(),['\n'])[0],text)
  return ( replaced_vals, newstr )



def get_first_element_of_tuples(tuples):
  tuples2 = []
  if tuples != None:
    for t in tuples:
      if len(t)>0:
        tuples2.append(t[0])
  return tuples2



def remove_double_newline(string):
  return string.replace('\r\n','\n').replace('\n\r','\n')



def get_symbol_line_no_for_sym(string):
  lineno=1
  linenos=[]
  lgt = len(string)
  for i in xrange(lgt):
    linenos.append(lineno)
    if string[i] in NEWLINES:
      lineno += 1
  return linenos


def get_this_much_string(text,start,num_chars):
  return text[start:min(len(text),start+num_chars)]


def str_has_at_least_this_much_whitespace(s,percentws):
  count = 0
  lgt = len(s)
  for char in s:
    if char_is_whitespace(char):
      count += 1
  if float(count)/lgt >= percentws:
    return True
  else:
    return False


# text has spaces and newlines (the only types of whitespace)
def get_linenos_and_remove_newlines(text):
  linenos = []
  no = 1
  t2 = []
  lgt = len(text)
  for i in xrange(lgt):
    if text[i]=='\n':
      if i==0:
        linenos.append(no)
        t2.append(' ')
      elif text[i-1]=='\n':
        linenos[-1] += 1
      elif text[i-1]==' ':
        pass
      else:
        linenos.append(no)
        t2.append(' ')
      no += 1
    else:
      if i>0 and text[i]==' ' and (text[i-1]==' ' or text[i-1]=='\n'):
        pass
      else:
        t2.append(text[i])
        linenos.append(no)
  return ( ''.join(t2), linenos )



def char_is_whitespace(char):
  return char in SPACES or char in NEWLINES


def replace_whitespace_with_single_space(text,except_newline=False):
  curr = re.sub(r'^[ 	]+', r'', remove_double_newline(text))

  if except_newline:
    with_newlines = re.sub(r'[ 	]*\n[ 	]*', r'\n', remove_double_newline(curr))
    with_newlines = re.sub(r'[ 	]+\n[ 	]+', r'\n', with_newlines)
    with_newlines = re.sub(r'[ 	]+', r' ', with_newlines)
    return with_newlines
  else:
    return re.sub(r'\s+', r' ', curr)



def ensure_thissym_around_syms(text,syms_dict,thissym):
  tmp = []
  lgt = len(text)
  # put a space before/after each ssym if not already one
  for i in xrange(lgt):
    curr = text[i]
    if curr in syms_dict:
      if i > 0 and text[i-1] != thissym:
        tmp.append(thissym)
      tmp.append(curr)
      if i+1 < lgt and text[i+1] != thissym:
        tmp.append(thissym)
    else: tmp.append(curr)
  return ''.join(tmp)


def count_each_symbol(text,syms_lst):
  counts = [0] * len(syms_lst)

  lgt = len(text)
  for i in xrange(lgt):
    curr = text[i]
    if curr in syms_lst:
      counts[syms_lst.index(curr)] += 1
  return counts


def gobble_and_remove_blocks(source,startchar,endchar,keeponsameline,PLACEHOLDER,digitliteral=False):
  removed_vals = []
  sourcemod = []
  i=0
  lgt = len(source)
  while i<lgt:
    curr = source[i]
    j = i+1
    if digitliteral and curr.isspace() and j<lgt and ( (source[j].isdigit()) ):
        to_remove = []
        if source[j]=='-':
          to_remove.append('-')
          j += 1
        while j<lgt and source[j].isdigit():
          to_remove.append(source[j])
          j += 1
        removed_vals.append(''.join(to_remove))
        sourcemod.append(' '+PLACEHOLDER+' ')
    elif digitliteral==False and curr==startchar:
      to_remove = []
      while j<lgt and source[j]!=endchar:
        to_remove.append(source[j])
        j += 1
        if keeponsameline and source[j]=='\n':
          break
      
      if j<lgt and source[j]==endchar: # remove the middle
        sourcemod.append(startchar+PLACEHOLDER+endchar)
        removed_vals.append(''.join(to_remove))
      i = j
    else: sourcemod.append(curr)

    i += 1
  return (''.join(sourcemod),removed_vals)



def get_symbol_counts_in_string_ith_base_0(string):
  symbols_freq = []
  counts_dt = {}
  for sym in string:
    count = 0
    if sym not in counts_dt:
      counts_dt[sym] = count
    else:
      counts_dt[sym] += 1
      count = counts_dt[sym]
    symbols_freq.append(count)
  return symbols_freq



def format_regex(regex):
  new = ''
  for i in regex:
    new += '['+i+']'
  return new



def dirty_search_for_num_occ_of_pat_lst_in_text(text,pattern_lst,pat_whitespace_to_left=True,pat_whitespace_to_right=True,pattern_lst_is_regex=False):
  counts = []
  for pattern in pattern_lst:
    counts.append(dirty_search_for_num_occ_of_pat_in_text(text,pattern,pat_whitespace_to_left,pat_whitespace_to_right,pattern_lst_is_regex))
  return counts


def dirty_search_for_num_occ_of_pat_in_text(text,pattern,pat_whitespace_to_left=True,pat_whitespace_to_right=True,pattern_lst_is_regex=False):
  if pattern_lst_is_regex==False:
    pattern = format_regex(pattern)
  return dirty_search_for_num_occ_of_regex_in_text(text,pattern,pat_whitespace_to_left,pat_whitespace_to_right)


def dirty_search_for_num_occ_of_regex_in_text(text,regex,pat_whitespace_to_left=True,pat_whitespace_to_right=True):
  if pat_whitespace_to_left: regex = '\s'+regex
  if pat_whitespace_to_right: regex = regex+'\s'

  matches = re.findall(r''+regex,text)
  return len(matches)



def prepend_and_or_append_str_to_strlst(strlst,prependstr='',appendstr=''):
  new = []
  for s in strlst:
    new.append(prependstr+s+appendstr)
  return new




