#!/usr/bin/python


def make_pretty_code_format(tokens,variables,VARIABLE_PLACEHOLDER,keywords_dict,newline_before_syms,newline_after_syms,indent_on_syms,dedent_on_syms,spaces_after_syms,spaces_before_syms,indent_space_num=2,tup_index_of_actual_token=0,tup_index_of_variable=2):
  sourcemod = []
  depth = 0
  lgt = len(tokens)
  just_newline = True
  newline_count = 0
  for i in xrange(lgt):
    curr = tokens[i][tup_index_of_actual_token] # the actual token
    
    if curr in indent_on_syms:
      depth += indent_space_num
    elif curr in dedent_on_syms:
      depth -= indent_space_num

    if curr in newline_before_syms:
      sourcemod.append('\n')
      newline_count +=1
      just_newline = True

    if just_newline: 
      sourcemod.append(str(' '*depth))
      just_newline = False
 
    if curr in spaces_before_syms:
      sourcemod.append(' ')
    if curr == VARIABLE_PLACEHOLDER:
      sourcemod.append(' '+variables[tokens[i][tup_index_of_variable]]+' ')
    else:
      sourcemod.append(str(curr))

    if depth < 0: depth = 0 # in case users code is wrong and doesn't compile

    if (curr in keywords_dict) or (curr in spaces_after_syms):
      sourcemod.append(' ')
  
    if curr in newline_after_syms: 
      sourcemod.append('\n')
      newline_count += 1
      just_newline = True
      if depth == 0: # end of function
        sourcemod.append('\n\n\n')

  return (newline_count,(''.join(sourcemod)))


    






