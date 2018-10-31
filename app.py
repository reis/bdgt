import sys
from include import config
from include import db
import cherrypy
import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dateutil.relativedelta import relativedelta

env = Environment(loader=FileSystemLoader(config.ROOT + 'src/web/templates'))

cherrypy.config.update({'server.socket_port': 8081})

class App(object):

    def __init__(self):
        self.db = db.db()

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
        transactions = self.db.get_transactions()

        tmpl = env.get_template('transactions.html')
        return tmpl.render(transactions=transactions, category=category)
    
    @cherrypy.expose
    def budget(self, month=datetime.now().strftime("%Y-%m")):
        budget = self.db.get_budget_detail(month)
        links = ( (datetime.strptime(month, "%Y-%m") + relativedelta(months=-1)).strftime("%Y-%m"),
                  (datetime.strptime(month, "%Y-%m") + relativedelta(months=+1)).strftime("%Y-%m")
        )
        tmpl = env.get_template('budget.html')
        return tmpl.render(ROOT = config.ROOT, budget=budget, month=month, links=links)

    @cherrypy.expose
    def budgets(self, month=(datetime.now()+relativedelta(months=1)).strftime("%Y-%m")):
        links = ( (datetime.strptime(month, "%Y-%m") + relativedelta(months=-1)).strftime("%Y-%m"),
                  (datetime.strptime(month, "%Y-%m") + relativedelta(months=+1)).strftime("%Y-%m")
        )
        budgets = dict()
        xtotal = dict()
        for x in range(0, -8, -1):
            xmonth = (datetime.strptime(month, "%Y-%m") + relativedelta(months=x)).strftime("%Y-%m")
            xbudget = self.db.get_budget_detail(xmonth)
            xtotal[xmonth] = { "amount3": 0.0, "budget3": 0.0 }
            for budget_line in xbudget:
                if budget_line["category"] not in budgets: 
                    budgets[ budget_line["category"] ] = { budget_line["title"]: { xmonth: budget_line } }
                elif budget_line["title"] not in budgets[ budget_line["category"] ]:
                    budgets[ budget_line["category"] ] [ budget_line["title"] ] = { xmonth: budget_line }
                elif xmonth not in budgets[ budget_line["category"] ] [ budget_line["title"] ]:
                    budgets[ budget_line["category"] ] [ budget_line["title"] ] [ xmonth ] = budget_line
                xtotal[xmonth]["amount3"] += budget_line["amount3"]
                xtotal[xmonth]["budget3"] += budget_line["budget3"]
        budgets["TOTAL"] = { None: xtotal }
        
        for category in budgets:
            for title in budgets[category]:
                for x in range(0, -8, -1):
                    xmonth = (datetime.strptime(month, "%Y-%m") + relativedelta(months=x)).strftime("%Y-%m")
                    if xmonth not in budgets[category][title]:
                        budgets[category][title][xmonth] = {"budget3": 0, "amount3": 0, "ord": 2}
                mysort = dict()
                for key in sorted(budgets[category][title].keys(), reverse=True):
                    mysort[key] = budgets[category][title][key]
                budgets[category][title] = mysort

        #print(json.dumps(budget_line, indent=2))
        tmpl = env.get_template('budgets.html')
        return tmpl.render(ROOT = config.ROOT, data=budgets, month=month, links=links, months=list(budgets[category][title].keys()))


config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    },
    '/css': {
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': "/dev/bdgt/src/web/static/css/" 
    }
}

cherrypy.quickstart(App(), '/', config=config)