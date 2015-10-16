#!/usr/bin/python2.7 -tt

import constants
import os
import pickle
import pandas as pd
import sys
from sklearn import metrics
from sklearn import cross_validation
from sklearn.ensemble import GradientBoostingClassifier
import datetime
from pylab import *






def get_prediction_info(FEATURES_HEADER,features,duplications,xp_duplications,poor_identifier_display,magic_numbers_display):
  absfn = os.path.join(os.path.dirname(os.path.abspath(__file__)),constants.MODEL_FN)
  matrix_of_stats = []
  predicted_num = -1
  scorestr = ''

  try:
    df = pd.DataFrame(features,index=FEATURES_HEADER).transpose()

    STUDENT_MULT_FACTOR = .6
    BONUS_POINTS_MAX = 1.25
    COL_NAME = 0
    PRETTY_NAME = 1
    PROS_CONSTANT = 2
    IMPROVE_DESC = 3
    HTML_STR = 4
    vals = []

    vals.append(['orig_dup_mean_div_count','Copy & Paste Profile',constants.COPY_PASTE_MOST_PROS_SCORE,'Better leverage constructs like loops and functions.  When you copy and paste code, think this: there must be a better way!  It is very difficult to maintain multiple segments of redundant code.',duplications])
   
    vals.append(['xp_dup_mean_div_count','Copy, Paste, & Replace Profile',constants.COPY_PASTE_REPLACE_MOST_PROS_SCORE,'Copy, paste, & replace occurs when you have code that you like and you copy/paste and then make some variable/identifier replacements to solve the current problem.  In this case, look to functions with nice parameter lists.  It is extremely difficult to maintain copy/paste/replace code.  Consider the changes you would need if you later find a bug in a copy/paste/replace segment.',xp_duplications])

    vals.append(['count_small_identifier_percent','Identifier Length',constants.SMALL_IDENTIFIER_PERCENT_PROS_SCORE,'Short variable names make it simpler to code your program.  However, in the long run, when you reassess your code, it will take longer to understand and debug.  Further, newbies to your system will have a much larger learning curve to understand your code.  So, it is good practice to use longer identifier names.',poor_identifier_display])

    vals.append(['identifier_creativity_uppercase_underscore_percent','Identifier Style',constants.IDENTIFIER_CREATIVITY_PROS_SCORE,'The most readable identifier names are those that look like this: a_variable_name, aVariableName, and CONSTANT.  Professional code will include such identifier styles.',''])

    vals.append(['magic_numbers_per_number','CONSTANTS',constants.MAGIC_NUMBERS_PER_NUMBER_PROS_SCORE,'In a source file, when you find yourself hard-coding a number like 12.32 two or more times, then you should declare a constant instead.  We call these reoccurring numbers *magic* numbers.  It is much easier to maintain one constant than many hard-coded values. ',magic_numbers_display])

    vals.append(['generality_flag','Generality',constants.GENERALITY_FLAG_PROS_SCORE,'Writing professional code does not include hard-coded print statements to the terminal; you should be able to print to files, error streams, or the monitor with ease.  If you need to include print statements to the monitor, in C for example, a more general way to is use fprintf with stdout.  The same sentiment goes for input. ',''])

    vals.append(['comment_lines_div_orig_loc','Documentation',constants.COMMENT_LINES_DIV_ORIG_LOC_PROS_SCORE,'Including comments in your code is important for many reasons. Comments help document sophisticated segments of source code.  They help you read and understand code that you wrote months ago or code that you are inheriting.  While it is impractical that every function have a block comment stating its description, preconditions, and postconditions, you definitely should focus on documenting your most sophisticated functions.',''])



    df2 = df[constants.CLASSIFY_BY_ONLY_COLS]
    score_num = 0
    score_denom = 0

    

    with open(absfn, 'rb') as f:
      randomforestmodel = pickle.load(f)
      predicted_nums = randomforestmodel.predict(df2) # predicted_num = 0 or 1

      predicted_num = predicted_nums[0]  

    matrix_of_stats.append(['Statistic', 'Your Grade', 'Ideas to Improve', None])

    MULT_FACTOR = 1
    if constants.PRO_CODE_PREDICTION != predicted_num: MULT_FACTOR = STUDENT_MULT_FACTOR
    for val in vals:
      yourscore = df.ix[0,val[COL_NAME]]
      proscore = val[PROS_CONSTANT][1]
      condition = val[PROS_CONSTANT][0]
      ispro = constants.is_condition_met(yourscore,condition,proscore)
      if condition == constants.GREATER_THAN or condition == constants.EQUAL_TO:
        if proscore == 0: temp = 0
        else: temp = yourscore / proscore
      else:
        if yourscore == 0: temp = 0
        else: temp = proscore / yourscore
      score_num += min(BONUS_POINTS_MAX, temp*MULT_FACTOR)
      score_denom += 1
      matrix_of_stats.append([val[PRETTY_NAME],get_html_label_for_stat(ispro),val[IMPROVE_DESC],val[HTML_STR]])
      
    thescore = min(1, score_num / (score_denom+1))
    scorestr = '%.0f%%' %(thescore*100)

  except Exception as e:
    sys.stderr.write("get_prediction: Unexpected error: "+str(e))
  
  return (constants.PRO_CODE_PREDICTION,predicted_num,scorestr,matrix_of_stats)


def get_html_label_for_stat(is_professional):
  if is_professional:
    return '<b><font color="green">Professional</font><b>'
  else:
    return '<b><font color="red">Student</font><b>'






def write_model_to_file_and_return_for_fun(model,fn):
  with open(fn, 'wb') as f:
    pickle.dump(model, f)
    f.close()

  with open(fn, 'rb') as f:
    returned_model = pickle.load(f)
    f.close()
    return returned_model

  return None


def get_roc(clf, X, Y):
  acc = clf.score(X,Y)

  Y_score = clf.decision_function(X)
  fpr = dict()
  tpr = dict()
  fpr, tpr, _ = metrics.roc_curve(Y, Y_score)

  roc_auc = dict()
  roc_auc = metrics.auc(fpr, tpr)

  return (roc_auc,fpr,tpr)

    
    
def plot_roc(auc_train,fpr_train,tpr_train,auc_test,fpr_test,tpr_test):
  plt.figure(figsize=(4,4))
  plt.title('ROC Curve')
  plt.plot([0, 1], [0, 1], 'k--')
  plt.xlim([-0.05, 1.0])
  plt.ylim([0.0, 1.05])
  plt.xlabel('False Positive Rate')
  plt.ylabel('True Positive Rate')
  plt.grid(True)
  plt.plot(fpr_train, tpr_train, label='%-6s AUC = %.2f' %('Train:',auc_train))  
  plt.plot(fpr_test, tpr_test, label='%-6s  AUC = %.2f' %('Test:',auc_test))        
  plt.legend(loc="lower right", shadow=True, fancybox =True) 
  plt.show




def make_model(model_out_fn, DEBUG = False):

  good_df = pd.read_csv(constants.GOOD_CSV)
  bad_df = pd.read_csv(constants.BAD_CSV)
  complete_dataset = pd.concat([good_df,bad_df])
  complete_targets = [1]*len(good_df) + [0]*len(bad_df)

  complete_dataset = complete_dataset[constants.CLASSIFY_BY_ONLY_COLS]
  (training_new, test_new, training_target, test_target) = cross_validation.train_test_split( \
      complete_dataset, complete_targets, test_size=0.6, random_state=0)

  model = GradientBoostingClassifier(min_samples_split=1, random_state=5, max_features=len(constants.CLASSIFY_BY_ONLY_COLS))
  model.fit(training_new,training_target)
  fi = model.feature_importances_
  max_fi = max(fi)

  model = write_model_to_file_and_return_for_fun(model,model_out_fn)


  if DEBUG:
    print(model)
    print max_fi 
  
    print 'TEST METRICS'
    expected = test_target
    predicted = model.predict(test_new)
    print(metrics.classification_report(expected, predicted))
    print(metrics.confusion_matrix(expected, predicted))

    print 'TRAINING METRICS'
    expected = training_target
    predicted = model.predict(training_new)
    print(metrics.classification_report(expected, predicted))
    print(metrics.confusion_matrix(expected, predicted))

    (auc_train,fpr_train,tpr_train) = get_roc(model, training_new, training_target)
    (auc_test,fpr_test,tpr_test) = get_roc(model, test_new, test_target)
    plot_roc(auc_train,fpr_train,tpr_train,auc_test,fpr_test,tpr_test)
    plt.show()

    ## just for sanity check
    predicted = model.predict(training_new)
    print 'TRAINING METRICS (using model saved to .pkl)'
    print(metrics.classification_report(expected, predicted))
    print(metrics.confusion_matrix(expected, predicted))




