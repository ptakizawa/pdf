from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pyPdf import PdfFileReader
import re
import string
import operator
import os
import nltk
from nltk.corpus import stopwords
import psycopg2
import json

DBNAME = "curriculum"
DBUSER = "curriculum_admin"
DBHOST = "localhost"
DBPASSWORD = "9kzH5bSLtFRHz5Uh"

SQL = "INSERT INTO pdfs.fulltext_search(data, doc) VALUES (%s, %s)"

BASE_FOLDER = '/Users/ptakizawa/curriculum_pdfs'

COMMON_WORDS = ["the", "be", "and", "of", "a", "in", "to", "have", "it","i", "that", "for",
"you", "he", "with", "on", "do", "say", "this", "they", "is", "an", "at", "but", "we", "his",
"from", "that", "not", "by", "she", "or", "as", "what", "go", "their","can", "who", "get", "if",
"would", "her", "all", "my", "make", "about", "know", "will", "as", "up", "one", "time", "has",
"been", "there", "year", "so", "think", "when", "which", "them", "some", "me", "people", "take",
"out", "into", "just", "see", "him", "your", "come", "could", "now", "than", "like", "other",
"how", "then", "its", "our", "two", "more", "these", "want", "way", "look", "first", "also",
"new", "because", "day", "more", "use", "no", "man", "find", "here", "thing", "give", "many",
"well"]

def get_files(folder):
    file_list = []
    for path, dirs, files in os.walk(BASE_FOLDER):
        for f in files:
            path_array = path.split('/')
            document = {}
            document['course'] = path_array[-2]
            document['pedagogy'] = path_array[-1]
            document['session_title'] = f.strip('.pdf')
            document['url'] = '/'.join([path_array[-2], path_array[-1], f])
            document['path'] = '/'.join([path, f])
            file_list.append(document)
    return file_list

def cleanInput(input):
    if type(input) is str:
        input = re.sub('\n+', ' ', input).lower()
        input = re.sub(' +', ' ', input)
        input = re.sub('\x0c', ' ', input)
        input = input.decode('UTF-8', 'ignore')
        input = input.encode('ascii', 'ignore')
        print input
        """input = input.split(' ')
        cleanInput = []
        for item in input:
            item = item.strip(string.punctuation)
            if len(item) > 1 or (item.lower() == 'a' or item.lower() == 'i'):
                cleanInput.append(item)"""
        return input
    else:
        return ""

def getNgrams(input, n):
    input = cleanInput(input)
    output = {}
    for i in range(len(input) - n+1):
        ngramTemp = " ".join(input[i:i+n])
        if removeStopWords(ngramTemp) == False:
            if ngramTemp not in output:
                output[ngramTemp] = 0
            output[ngramTemp] += 1
    return output

def removeStopWords(ngram):
    ngram = ngram.split(' ')
    for word in ngram:
        if word in COMMON_WORDS:
            return True
    return False

def convert(fname, pages=None):
    print fname
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    codec = 'utf-8'
    converter = TextConverter(manager, output, codec=codec, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    try:
        infile = file(fname, 'rb')
        if PdfFileReader(infile).isEncrypted != True:
        
            for page in PDFPage.get_pages(infile, pagenums, check_extractable=True):
                try:
                    interpreter.process_page(page)
                except Exception as e:
                    print e
                    continue
                finally:
                    pass

            infile.close()
            converter.close()
            text = output.getvalue()
            output.close
            print "text processed"
            return text
    except Exception as e:
        print e

    finally:
        pass

def searchNgrams(term):
    for key, value in ngrams.iteritems():
        ngram_list = key.split(' ')
        if term in ngram_list:
            return key

 
# folder = raw_input("Enter the name of the directory: ")
files = get_files(BASE_FOLDER)
print len(files)
ngrams = {}
try:
    conn = psycopg2.connect(database=DBNAME, user=DBUSER, host=DBHOST, password=DBPASSWORD)
    cursor = conn.cursor()
except:
    print "I an unable to connect to the database."

entry_id = 0
for f in files:
    if f['path'].endswith('pdf'):
        #entry_id += 1
        data = json.dumps({
           "url": f['url'],
           "session_title": f['session_title'],
           "course": f['course'],
           "pedagogy": f['pedagogy'] 
        })

        text = convert(f['path'])
        cleaned_text = cleanInput(text)
        #print type(data)
        #print type(cleaned_text)
        cursor.execute(SQL, (data, cleaned_text))
        #print f
        #print "-----------------------------------------------"
        #print data
        #print cleaned_text
        #print text
        #print cleanInput(text)
        #if type(text) == str:
        #    file_ngrams = getNgrams(text, 2)
        #    ngrams.update(file_ngrams)


conn.commit()
cursor.close()
conn.close()

#sortedNGrams = sorted(ngrams.viewitems(), key=operator.itemgetter(1), reverse=True)
#print len(sortedNGrams)
#print searchNgrams('gender')
#print sortedNGrams[:100]
