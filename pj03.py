from mako.template import Template
from contextlib import closing
from pprint import pprint
import mysql.connector
import cgi
from cgi import parse_qs, escape

# setup mysql connection information
mysql_connection_info = {
    'host': 'localhost',
    'user': 'pj03',
    'passwd': 'Project3!',
    'database': 'pj03',
    'auth_plugin': 'mysql_native_password'
}
# returns a string with the query
def query_presidents(mysql_connection, pageNumber, column, queryList):
    presidents = []
    with closing(mysql_connection.cursor(dictionary = True)) as mysql_cursor:
      pageNumber = pageNumber -1
      offset = pageNumber*50
      myQuery = "SELECT * FROM baby_namess ORDER BY {} ASC LIMIT 50 OFFSET {:d}".format(column,offset)
      if(queryList[0] == "SELECT * FROM baby_namess LIMIT 50"):   # If base page was passed in
        myQuery = "SELECT * FROM baby_namess LIMIT 50"
      queryList[0] = myQuery        # Query saved in list so it can be accessed later
      mysql_cursor.execute(myQuery)
      presidents = mysql_cursor.fetchall()
    return presidents

def application(env, start_response):
      with closing (mysql.connector.connect(**mysql_connection_info)) as mysql_connection:
        try:
          start_response('200 OK', [('Content-Type', 'text/html')])
          qs = parse_qs(env['QUERY_STRING'])
          queryList = [""]
          #If the query string isn't empty
          if len(qs) > 0:
            pageNumber = int(qs.get("page",1)[0])             # if page isn't a number, should be caught by try-execpt
            column = cgi.escape(str(qs.get("col","rank")[0])) # input get's sanitized
          else:
            pageNumber = 1
            column = ""
            queryList[0] = "SELECT * FROM baby_namess LIMIT 50" # Must be base page
          html_template = Template(filename = 'templates/baby.html')
          html_dict = {
              'presidents': query_presidents(mysql_connection, pageNumber, column, queryList),
              'year_of_birth': "",
              'ethnicity': "",
              'first_name': "",
              'gender': "",
              'count': "",
              'ranking': "",
              'query': queryList[0]
          } # html_dict
          # If column matches ORDER BY column add ">" to column header
          for x in html_dict:
            if(column == x):
              html_dict[column] = ">"
          # If page number is out of bounds 
          if pageNumber > 227 or pageNumber < 0:
            html_template = Template(filename = 'templates/error.html')
            html_dict = {
            'query': "page is out of range"
          } # html_dict
          response = html_template.render(**html_dict)
          return response.encode()
        except:
          # Catches unseen errors
          html_template = Template(filename = 'templates/error.html')
          html_dict = {
            'query': queryList[0]
          } # html_dict
          response = html_template.render(**html_dict)
          return response.encode()