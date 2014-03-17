'''
 foowoo application
 J. Thomas
'''

from flask import Flask,jsonify
from flask import render_template
from pymongo import MongoClient
from yelp import Yelp
import logging
import logging.handlers

app = Flask(__name__)

#
#setup logger
#
foo_logger = logging.getLogger('MyLogger')
foo_logger.setLevel(logging.INFO)
log_handler = logging.handlers.SysLogHandler(address = '/dev/log') # we are on Linux
foo_logger.addHandler(log_handler)


#
# configure and instantiate Yelp Object
#
app.config.from_pyfile('config.py', silent=True)
app.config.from_envvar('foowoo_config', silent=True)

yelp = Yelp(app.config['CONSUMER_KEY'],app.config['CONSUMER_SECRET'],app.config['TOKEN'],app.config['TOKEN_SECRET'])



#
# connect to MongoDB
#


connection = MongoClient(app.config['MONGO_URI'],app.config['MONGO_PORT'])

if app.config['MONGO_USER']!='':
    connection.nyc.authenticate(app.config['MONGO_USER'], app.config['MONGO_PASSWORD'])
db = connection.nyc                # attach to db
collection = db.restaurants        # specify the colllection
foo_logger.info('Connected to MongoDB at %s on PORT %s',
    app.config['MONGO_URI'],app.config['MONGO_PORT'])


#
# use this to page through result sets
#
def pager(someCursor,page):
   # process cursor
    json_docs = []
    pagination = []

    # get the entire result set
    for doc in someCursor:    
        json_docs.append(doc) 

    # return the requested page (10 items per page)
    for i in range((page-1)*10,page*10):

        try:
             # don't let building number be a integer
            json_docs[i]['building'] = str(json_docs[i]['building'])

            # the city uses 'Jewish/Kosher', but Yelp uses 'Kosher'
            if json_docs[i]['cusine_description'] == 'Jewish/Kosher' :
                json_docs[i]['cusine_description'] = 'Kosher'

            pagination.append(json_docs[i])
        except:
            break
    return pagination

@app.route('/')
def index():
    return render_template('index.html')

'''
  GET restaurant listing by restaurant name
'''
@app.route('/name/<name>/<int:page>')
def getByName(name,page):
    restaurantName = name.upper()

    if (restaurantName == 'undefined'):
        return ""
    print "show name listing for " + restaurantName

    # search for restaurant name in MongoDB
    cursor = collection.find({'dba':{'$regex':'^' + restaurantName}},fields={'_id': False},sort=[('dba',1)]) 
    # get a "page" full of results
    pageData = pager(cursor,page)
    return jsonify({'total_docs': cursor.count(), 'results' : pageData})

'''
  GET restaurant listing by borough
'''
@app.route('/boro/<boroName>/<int:page>')
def getByBoro(boroName,page):

    if (boroName == 'undefined'):
        return ""
    print "show boro listing for " + boroName

    # search for boro in MongoDB
    cursor = collection.find({'boro_name':boroName },fields={'_id': False},sort=[('dba',1)]) 
    # get a "page" full of results
    pageData = pager(cursor,page)
    return jsonify({'total_docs': cursor.count(), 'results' : pageData})

'''
  GET restaurant listing by cusine/borough
'''
@app.route('/cusine/<cusine>/<boroName>/<int:page>')
def getByCusineBoro(cusine,boroName,page):

    if (boroName == 'undefined'):
        return ""
    if (cusine == 'undefined'):
        return ""              
    print "show cusine listing for " + cusine + " in " + boroName

    # search for cusine/boro in MongoDB
    cursor = collection.find({'boro_name':boroName, 'cusine_description': cusine },fields={'_id': False},sort=[('dba',1)]) 
    # get a "page" full of results
    pageData = pager(cursor,page)
    return jsonify({'total_docs': cursor.count(), 'results' : pageData})


'''
  call Yelp object to fetch restaurant data
'''
@app.route('/yelp/<address>/<phone>/<cusine>')
def getYelpData(address,phone,cusine):

    arg = 'location=' + address + '&telephone=' + phone + '&term=' + cusine
    result = yelp.getData(arg)
    yelpData=""
    places =  result['businesses'];
    for place in places:
        if (place.get('phone') == phone):

            yelpData = place
            break;

    return jsonify(yelpData)

'''
  show Yelp data in a modal window
'''
@app.route('/yelpmodal.html')
def showModal():
    return render_template('yelpmodal.html')


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')

