import os
import configparser
from db import Db
import cherrypy
from cherrypy.lib import auth_basic
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint

config = configparser.ConfigParser()
config.read("config.ini")
env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)) + '/web/templates'))

def validate_password(realm, username, password):
    if username == os.environ['AUTH_USER'] and password == os.environ['AUTH_PASS']:
       return True
    return False

class App(object):

    def __init__(self):
        self.db = Db()

    @cherrypy.expose
    def index(self):
        return self.budgets()

    @cherrypy.expose
    def transactions(self, month, category, title):
        transactions = self.db.get_transactions(month, category, title)

        tmpl = env.get_template('transactions.html')
        return tmpl.render(transactions=transactions, category=category, title=title)

    @cherrypy.expose
    def transaction(self, ):
        transactions = self.db.get_transactions(1)

        tmpl = env.get_template('transactions.html')
        return tmpl.render(transactions=transactions)
    
    @cherrypy.expose
    def budget(self, month=datetime.now().strftime("%Y-%m")):
        budget = self.db.get_budget_detail(month)
        links = ( (datetime.strptime(month, "%Y-%m") + relativedelta(months=-1)).strftime("%Y-%m"),
                  (datetime.strptime(month, "%Y-%m") + relativedelta(months=+1)).strftime("%Y-%m")
        )
        tmpl = env.get_template('budget.html')
        return tmpl.render(budget=budget.values(), month=month, links=links)

    @cherrypy.expose
    def budgets(self, month=(datetime.now()+relativedelta(months=1)).strftime("%Y-%m")):
        links = ( (datetime.strptime(month, "%Y-%m") + relativedelta(months=-1)).strftime("%Y-%m"),
                  (datetime.strptime(month, "%Y-%m") + relativedelta(months=+1)).strftime("%Y-%m")
        )
        budgets = dict()
        for x in range(-8, 1, 1):
            xmonth = (datetime.strptime(month, "%Y-%m") + relativedelta(months=x)).strftime("%Y-%m")
            xbudget = self.db.get_budget_detail(xmonth)
            for x in xbudget:
                budget_line = xbudget[x]
                if budget_line["category"] not in budgets: 
                    budgets[ budget_line["category"] ] = { budget_line["title"]: { xmonth: budget_line } }
                elif budget_line["title"] not in budgets[ budget_line["category"] ]:
                    budgets[ budget_line["category"] ] [ budget_line["title"] ] = { xmonth: budget_line }
                elif xmonth not in budgets[ budget_line["category"] ] [ budget_line["title"] ]:
                    budgets[ budget_line["category"] ] [ budget_line["title"] ] [ xmonth ] = budget_line
        
        for category in budgets:
            for title in budgets[category]:
                for x in range(-8, 1, 1):
                    xmonth = (datetime.strptime(month, "%Y-%m") + relativedelta(months=x)).strftime("%Y-%m")
                    if xmonth not in budgets[category][title]:
                        budgets[category][title][xmonth] = {"budget3": 0, "amount3": 0, "ord": 2}
                mysort = dict()
                for key in sorted(budgets[category][title].keys(), reverse=True):
                    mysort[key] = budgets[category][title][key]
                budgets[category][title] = mysort

        tmpl = env.get_template('budgets.html')
        return tmpl.render(data=budgets, month=month, links=links, months=list(budgets[category][title].keys()))


cherrypy_config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    },
    '/css': {
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': "web/static/css/" 
    },
     '/': {
       'tools.auth_basic.on': True,
       'tools.auth_basic.realm': 'localhost',
       'tools.auth_basic.checkpassword': validate_password,
       'tools.auth_basic.accept_charset': 'UTF-8',
    }
}

cherrypy.quickstart(App(), '/', config=cherrypy_config)