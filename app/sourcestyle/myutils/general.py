#!/usr/bin/python2.7 -tt


def get_str_ascii_char_and_special(text,special):
  t2 = []
  for c in text:
    #print type(c)
    if len(c)==1 and c[0] in special:
      t2.append('['+str(ord(c[0]))+']')
    else:
      t2.append(c)
  return ''.join(t2)
  

def get_HTML_highlight(string,highlight_prefix_length):
  return '<span style="background-color: #FFFF00">'+string[:highlight_prefix_length]+'</span>'+string[highlight_prefix_length:]


def get_desc_sorted_and_indexed(arr):
  arr_w_index = [(i, arr[i]) for i in xrange(len(arr))]
  arr_w_index = sorted(arr_w_index,key=lambda pair: pair[1],reverse=True)
  return arr_w_index


def sort_tuple_arr(tuple_arr,sort_by_ith_feature):
  return sorted(tuple_arr, key=lambda x: x[sort_by_ith_feature])
