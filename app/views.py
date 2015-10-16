from flask import render_template, request, Flask
from sourcestyle import constants
import main as coderater_MAIN
import urllib2 
import contextlib
import sys
import logging

  




###########################################
###########################################
########### LOCAL OR AWS SETUP ??? ########
###########################################
###########################################

# ONLY FOR LOCAL RUNNING ON :5000
#from app import app 

###########################################

# ONLY FOR WEB RUNNING ON :8080
app = Flask(__name__) 
if __name__=="__main__": 
  app.run(host='0.0.0.0',port=8080) 

###########################################
###########################################
###########################################




USE_LOG_FN = '/home/ubuntu/myapp.log'






def write_to_log(logfn,message):
  logger = logging.getLogger('myapp')
  hdlr = logging.FileHandler(logfn)
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  hdlr.setFormatter(formatter)
  logger.addHandler(hdlr) 
  logger.setLevel(logging.INFO)
  logger.info(message)




@app.route('/about')
def about_page():
  return render_template("about.html")



@app.route('/contact')
def contact_page():
  return render_template("contact.html")




@app.route('/')
@app.route('/index')
def code_rater():
  sourcecode = request.args.get('sourcecode')
  rawsourcecodeurl = request.args.get('rawsourcecodeurl')
  language = request.args.get('language')

  msg = ''
  predicted_num=-1
  matrix_of_stats=None
  PRO_CODE_CONSTANT_NUM=0
  mode = ''
  scorestr = ''
  currlanguage = ''
  lensource = 0
  if sourcecode != None:
    lensource = len(sourcecode)
  try:
    if rawsourcecodeurl != None and len(rawsourcecodeurl) > 0:
      (msg, sourcecode) = get_prefix_from_url(rawsourcecodeurl,constants.MAX_SOURCECODE_SIZE)
      lensource = len(sourcecode)

      if msg != '':
        sourcecode = ''
        lensource = 0
      
    if sourcecode != None and lensource>0 and lensource >= constants.MIN_SOURCECODE_SIZE and language != None and len(language)>0:
      language_extensions = None
      if lensource >= constants.MAX_SOURCECODE_SIZE:
        msg = 'We only analyzed the first '+str(constants.MAX_SOURCECODE_SIZE//1000)+'k bytes of your source!'
        sourcecode = sourcecode[:constants.MAX_SOURCECODE_SIZE]
      if language in constants.LANGUAGES_SUPPORTED:
        currlanguage = language
        language_extensions = constants.LANGUAGES_SUPPORTED[language][constants.LANGUAGES_SUPPORTED_EXTENSIONS]
        mode = constants.LANGUAGES_SUPPORTED[language][constants.LANGUAGES_SUPPORTED_CODEMIRROR_MODE]
        sourcecode = sourcecode.encode('ascii', errors='ignore')  
        (PRO_CODE_CONSTANT_NUM,predicted_num,scorestr,matrix_of_stats)=coderater_MAIN.main(mode=2, SEARCH_FILES_IN_PATH='', source_str=sourcecode, lang_exts=language_extensions, OUTPUT_FEATURES_TO_CSV_FN='', CSV_DELIMITER='', LIMIT_TO_NUM_FILES=0)
        logthismsg = rawsourcecodeurl+'\t'+language+'\t'+str(predicted_num)+'\t'+str(PRO_CODE_CONSTANT_NUM)+'\t'+scorestr
        write_to_log(USE_LOG_FN, logthismsg)
      else:
        currlanguage = ''
    #elif lensource < constants.MIN_SOURCECODE_SIZE:
    #  msg = 'We need some more code to analyze!'
    else:
      msg = "Please select a language!"
  except Exception as e:
    sys.stderr.write("code_rater(): Unexpected error:"+str(e))
    msg = "  Hmm...  Is this legit, raw source code?"
    sourcecode = ''
    matrix_of_stats=None 

  return render_template("index.html", msg = msg, origsource = sourcecode, PRO_CODE_CONSTANT_NUM=PRO_CODE_CONSTANT_NUM, predicted_num=predicted_num, scorestr = scorestr, matrix_of_stats=matrix_of_stats, currlanguage = currlanguage, currlanguage_codemirror_mode = mode, languages_supported = constants.LANGUAGES_SUPPORTED.values(), languages_supported_name_pos = constants.LANGUAGES_SUPPORTED_NAME, languages_supported_mode_pos = constants.LANGUAGES_SUPPORTED_CODEMIRROR_MODE, MIN_SOURCECODE_SIZE=constants.MIN_SOURCECODE_SIZE, MAX_SOURCECODE_SIZE=constants.MAX_SOURCECODE_SIZE, currrawsourcecodeurl = rawsourcecodeurl)





def get_prefix_from_url(url,max_prefix_len):
  msg = ''
  retrieved_str = ''
  try:
    with contextlib.closing(urllib2.urlopen(urllib2.Request(url))) as f:
      retrieved_str = f.read(max_prefix_len) 
  except urllib2.HTTPError as e:
    msg = 'HTTP issue when trying to retrieve the source code.'
  except urllib2.URLError as e:
    msg = 'URL issue: recheck the URL!'
  except Exception as e:
    sys.stderr.write('get_prefix_from_url(): Exception with url='+str(url)+', '+str(e))
  return (msg, retrieved_str)


