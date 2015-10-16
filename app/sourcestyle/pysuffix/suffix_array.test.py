#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tools_karkkainen_sanders as tks

s = 'abab'
s = unicode(s,'utf-8','replace')
n = len(s)
sa = tks.simple_kark_sort(s)
lcp = tks.LCP(s,sa)
print sa
print lcp

1/0

for i in xrange(n-1) :
  if(s[sa[i]:] > s[sa[i+1]:]) :
    print s[sa[i]:][:40]
    print s[sa[i+1]:][:40]
    print '='*50
    
