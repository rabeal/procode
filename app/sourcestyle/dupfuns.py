#!/usr/bin/python2.7 -tt

import math
from myutils import mypatmat
from myutils import general
from pygments import highlight
import pygments.lexers
from pygments.formatters import HtmlFormatter



MIN_GROUP_SIZE = 2
FACTOR_TO_STORE_THIS_MUCH_MORE_OF_MATCH = 1.75
MOST_PERCENT_WHITESPACE = .9
CUTOFF_WRITE_FACTOR = 4
DISPLAY_USING_PYGMENTS = True
MAX_GROUPS = 2


#this lcp is defined as lcp[i] is max lcp between text[sa[i]...] and text[sa[i+1]...]
def get_dup_groups(MEAN_FACTOR_GROUP_ONLY_IF,mean_lcp,sa,lcp,text,pygmenttextlexer,special_syms=[],symbol_counts_in_string_ith_base_0=None,variables=None,VARIABLE_PLACEHOLDER=None,strings_arr=None,STRING_PLACEHOLDER=None,digits=None,DIGITS_PLACEHOLDER=None,types=None,TYPES_PLACEHOLDER=None,linenos_for_xp_dup=None,ssym_dt=None):
  duplications = []
  i = 0
  lgt = len(lcp)
  cutoff_write = CUTOFF_WRITE_FACTOR * lgt # to avoid quadratic printing
  wrote_num=0
  used_i = []
  num_groups = 0
  another_group = False
  
  symbol_line_nos = mypatmat.get_symbol_line_no_for_sym(text)

  working_with_xp_dup = True
  if symbol_counts_in_string_ith_base_0==None:
    working_with_xp_dup = False

  for iii in xrange(lgt):
    used_i.append(0)
  
  max_indexed_lcp_vals = general.get_desc_sorted_and_indexed(lcp)  
  for currmaxlcptuple in max_indexed_lcp_vals:
    lcp_pos = currmaxlcptuple[0]
    lcp_val = currmaxlcptuple[1]
    
    i = lcp_pos
    j = lcp_pos
    minlen=lgt
    strings = []

    another_group = False
    while mypatmat.char_is_whitespace(text[sa[j]])==False and j+1<lgt and lcp[j]>0 and lcp[j]>=MEAN_FACTOR_GROUP_ONLY_IF*mean_lcp and used_i[sa[j]]==0 and used_i[sa[j]+lcp[j]-1]==0: 
      another_group = True
      for jq in xrange(lcp[j]):
        used_i[sa[j]+jq]=1

      start1 = sa[j]
      start2 = sa[j+1]
      length = lcp[j]
      
      num_symbols_to_print = int(math.floor(length*FACTOR_TO_STORE_THIS_MUCH_MORE_OF_MATCH))
      if j==i:

        if working_with_xp_dup == False:
          minlen=min(minlen,length)
          strings.append((symbol_line_nos[sa[j]],general.get_str_ascii_char_and_special(mypatmat.get_this_much_string(text,start1,num_symbols_to_print),special_syms),length))
         

        else:
          
          if DISPLAY_USING_PYGMENTS:

            now_highlight_this_prefix_length=0
            pygments_html = get_pygments_html(text,start1,length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER,ssym_dt,pygmenttextlexer)
            strings.append((linenos_for_xp_dup[start1], pygments_html,length))


          else:
            (new_string,now_highlight_this_prefix_length) = get_xp_dup_actual_string(text,start1,length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER)
            strings.append((linenos_for_xp_dup[start1], general.get_HTML_highlight(new_string,len(new_string)),length))
          minlen=min(minlen,now_highlight_this_prefix_length)


      if working_with_xp_dup == False:
        minlen=min(minlen,length)
        strings.append((symbol_line_nos[sa[j+1]],general.get_str_ascii_char_and_special(mypatmat.get_this_much_string(text,start2,num_symbols_to_print),special_syms),length))
      else:
        if DISPLAY_USING_PYGMENTS:
          now_highlight_this_prefix_length=0
          pygments_html = get_pygments_html(text,start2,length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER,ssym_dt,pygmenttextlexer)
          strings.append((linenos_for_xp_dup[start2], pygments_html,length))
        else:
          (new_string,now_highlight_this_prefix_length) = get_xp_dup_actual_string(text,start2,length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER)
          strings.append((linenos_for_xp_dup[start2], general.get_HTML_highlight(new_string,now_highlight_this_prefix_length),length))
        

        minlen=min(minlen,now_highlight_this_prefix_length)

      wrote_num += length
      if wrote_num > cutoff_write: break
      j += 1


    if len(strings)>=MIN_GROUP_SIZE and mypatmat.str_has_at_least_this_much_whitespace(strings[0],MOST_PERCENT_WHITESPACE)==False:
      num_strings = len(strings)
      for si in xrange(num_strings):
        (loc,curr,match_len)=strings[si]
        if working_with_xp_dup == False:

          if DISPLAY_USING_PYGMENTS:
            curr = get_pygments_html_exact_dup(curr,0,match_len,len(curr),pygmenttextlexer)
          else:
            curr = general.get_HTML_highlight(curr,match_len)

        strings[si]=(loc,curr)
      duplications.append(general.sort_tuple_arr(strings,0))
    if another_group: num_groups += 1
    if num_groups >= MAX_GROUPS: break

  duplications_html=['<table>']

  if len(duplications)>0:
    groupnum = 1
    for group in duplications:
      duplications_html.append('<tr><td colspan="4" style="border-top: 1px solid #000;"><h3><br>Group '+str(groupnum)+':</h3><br></td></tr>')
      groupnum += 1
      for (lineno,string) in group:
        duplications_html.append('<tr><td><b>line~'+str(lineno)+'</b></td><td style="border-right: 1px solid #000;">&nbsp;&nbsp;&nbsp;</td><td>&nbsp;&nbsp;&nbsp;</td><td>'+string+'</td></tr><tr><td><br><br></td></tr>')
  duplications_html.append('</table>')

  return ''.join(duplications_html)






def get_pygments_html(text,start,length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER,ssym_dt,pygmenttextlexer):

  (new_string,now_highlight_this_prefix_length) = get_xp_dup_actual_string(text,start,length,length,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER)
  highlight_this = new_string[:now_highlight_this_prefix_length]
  highlight_this = get_pygments_and_allow_to_wrap(highlight_this, pygmenttextlexer, ssym_dt)
  now_highlight_this_prefix_length = len(highlight_this)
  pygments_prefix = general.get_HTML_highlight(highlight_this,now_highlight_this_prefix_length)          
  suffixlen = num_symbols_to_print-length
  (pygments_suffix,_) = get_xp_dup_actual_string(text,start+length,num_symbols_to_print,suffixlen,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings_arr,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER)
  pygments_suffix = get_pygments_and_allow_to_wrap(pygments_suffix, pygmenttextlexer, ssym_dt)
  return pygments_prefix+' '+pygments_suffix






def get_pygments_html_exact_dup(text,start,highlight_length,num_symbols_to_print,pygmenttextlexer):
  pygments_prefix = get_pygments_and_allow_to_wrap(mypatmat.get_this_much_string(text,start,highlight_length),pygmenttextlexer, {})
  rest = num_symbols_to_print-highlight_length
  pygments_suffix = get_pygments_and_allow_to_wrap(mypatmat.get_this_much_string(text,start+highlight_length,rest),pygmenttextlexer, {})
  return general.get_HTML_highlight(pygments_prefix,len(pygments_prefix))+' '+pygments_suffix







def get_pygments_and_allow_to_wrap(text,pygmenttextlexer,ssym_dt):
  pygmentstext = highlight(mypatmat.ensure_thissym_around_syms(text,ssym_dt,' '), pygmenttextlexer, HtmlFormatter(noclasses=False))
  (replaced,pygmentstext) = mypatmat.remove_all_in_between_on_same_line2_UNICODE(pygmentstext,'<pre.*?>',replacewith='<span class="highlight">')
  (replaced,pygmentstext) = mypatmat.remove_all_in_between_on_same_line2_UNICODE(pygmentstext,'</pre>',replacewith='</span>')
  (replaced,pygmentstext) = mypatmat.remove_all_in_between_on_same_line2_UNICODE(pygmentstext,'<div.*?>',replacewith='<span class="highlight">')
  (replaced,pygmentstext) = mypatmat.remove_all_in_between_on_same_line2_UNICODE(pygmentstext,'</div>',replacewith='</span>')
  return pygmentstext



def get_xp_dup_actual_string(source,start_pos,highlight_length,num_symbols_to_print,symbol_counts_in_string_ith_base_0,variables,VARIABLE_PLACEHOLDER,strings,STRING_PLACEHOLDER,digits,DIGITS_PLACEHOLDER,types,TYPES_PLACEHOLDER):
  string = []
  ind = start_pos
  end_pos = len(source)
  now_highlight_this_prefix_length = 0
  chars_used = 0

  while ind < end_pos and chars_used < num_symbols_to_print:
    i = source[ind]
    if ord(i) == ord(VARIABLE_PLACEHOLDER) or ord(i) == ord(STRING_PLACEHOLDER) or ord(i) == ord(DIGITS_PLACEHOLDER) or ord(i) == ord(TYPES_PLACEHOLDER):
      val = '[?]'
      pos_in_array = symbol_counts_in_string_ith_base_0[ind]
      if ord(i) == ord(VARIABLE_PLACEHOLDER) and pos_in_array < len(variables):
        val = ' '+variables[pos_in_array]+' '
      elif ord(i) == ord(STRING_PLACEHOLDER) and pos_in_array < len(strings):
        val = ' '+strings[pos_in_array]+' '
      elif ord(i) == ord(DIGITS_PLACEHOLDER) and pos_in_array < len(digits):
        val = ' '+digits[pos_in_array]+' '
      elif ord(i) == ord(TYPES_PLACEHOLDER) and pos_in_array < len(types):
        val = ' '+types[pos_in_array]+' '
      string.append(val)
      if chars_used < highlight_length:
        now_highlight_this_prefix_length += len(val)
    else:
      string.append(i)
      if chars_used < highlight_length:
        now_highlight_this_prefix_length += len(i)
    ind += 1
    chars_used += 1
  return (''.join(string),now_highlight_this_prefix_length)








