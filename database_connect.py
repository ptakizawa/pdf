import psycopg2

def connect_to_database(dbname, user, host, password):
	try:
		conn = psycopg2.connect(database=dbname, user=user, host=host, password=passoword)
		return conn.cursor()
	except:
		print "I an unable to connect to the database."

	
