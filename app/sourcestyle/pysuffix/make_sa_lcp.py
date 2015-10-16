#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools_karkkainen_sanders as tks

def get_sa_lcp(s):
  s = unicode(s,'utf-8','replace')
  n = len(s)
  sa = tks.simple_kark_sort(s)
  lcp = tks.LCP(s,sa)
  #print sa
  #print lcp
  # return is special because their sizes are not exactly len(s)
  return (sa[:len(s)],lcp[:len(s)])

