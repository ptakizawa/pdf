from flask import Flask,request,  render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import psycopg2
import re
import json

DBNAME = "curriculum"
DBUSER = "curriculum_admin"
DBHOST = "localhost"
DBPASSWORD = "9kzH5bSLtFRHz5Uh"
COLUMNS = ('id', 'data', 'doc', 'match', 'score')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp key'
bootstrap = Bootstrap(app)
manager = Manager(app)

SQL = "SELECT id, data, doc, ts_headline(doc, q), rank FROM (SELECT id, data, doc, q, ts_rank_cd(tsv, q) as rank from pdfs.fulltext_search, to_tsquery(%s) q where tsv @@ q order by rank desc) as foo"

#SQL = "SELECT data, ts_rank(tsv, keywords) AS rank FROM pdfs.fulltext_search, to_tsquery(%s) keywords WHERE keywords @@ tsv ORDER BY rank DESC"

try:
    conn = psycopg2.connect(database=DBNAME, user=DBUSER, host=DBHOST, password=DBPASSWORD)
    cursor = conn.cursor()
except:
    print "I an unable to connect to the database."

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
    	terms = form.search_string.data
    	form.search_string.data = ''
    	search_terms = str(re.sub("\s+", " & ", terms.rstrip()))
    	cursor.execute(SQL, (search_terms,))
    	results = []
    	search_results =[]
    	for row in cursor.fetchall():
    		results.append(dict(zip(COLUMNS, row)))
    	print json.dumps(results, indent=2)
    	"""for result in results:
    		for item in result:
    			if type(item) is dict:
    				search_results.append(item)
    			if type(item) is str:
    				search_results[-1]['text'] = item.decode('utf-8', 'ignore')
    	print search_results"""
    	return render_template('search_results.html',form=form, terms=terms, results=results)
    return render_template('index.html', form=form)

@app.route('/search_results', methods=['GET', 'POST'])
def search_results(terms, results):
	form = SearchForm()
	if form.validate_on_submit():
		terms = form.search_string.data
		form.search_string.data = ''
		search_terms = str(re.sub("\s\s+", " & ", terms))
		cursor.execute(SQL, (search_terms,))
		results = cursor.fetchall()
		return redirect(url_for(search_results, terms=terms, results=results))
	return render_template('search_results.html', form=form, terms=terms, data=results)

class SearchForm(FlaskForm):
	search_string = StringField("What are you looking for?", validators=[Required()])
	submit = SubmitField('Submit')

if __name__ == '__main__':
    manager.run()



