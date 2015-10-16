#!/usr/bin/python2.7 -tt


import sys
import re
import os
import shutil
import commands
import random




def get_file_names(thedir,keep_only_extensions_list,LIMIT_TO_NUM_FILES):
  fns = []
  for (dir, _, files) in os.walk(thedir):
    for f in files:
      path = os.path.join(dir, f)
      if has_extension(path,keep_only_extensions_list):
        fns.append(path)
  #print 'Total of ',len(fns),' files with extension ',repr(keep_only_extensions_list),' in ',thedir
  if LIMIT_TO_NUM_FILES<=0:
    return fns
  return random.sample(fns,min(len(fns),LIMIT_TO_NUM_FILES))



def has_extension(fn,extensions_list):
  has = False
  spl = fn.split('.')
  if spl!=None and len(spl)>1:
    if spl[-1].upper() in (ext.upper() for ext in extensions_list):
      has = True
  return has



def write_files(filenames,from_dir,to_dir):
  make_dir_if_it_doesnt_exist(to_dir)
  for fn in filenames:
    frompath = get_abs_path(from_dir,fn)
    topath = get_abs_path(to_dir,fn)
    print 'Copying %s to %s  ...' %(frompath, topath)
    shutil.copy(frompath,topath)


def write_tuple_list_to_file(tl,fn):
  f = open(fn,'w')
  for i in tl:
    f.write(repr(i) + '\n')
  f.close()
  


def get_text(filename):
  text = None
  try:
    f = open(filename,'rU')
    text = f.read()
    f.close()
  except IOError, e:
    pass
  return text



