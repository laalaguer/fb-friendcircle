import webapp2
import jinja2
import os



jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Display(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("<p> underconstruction <p>")
    def post(self):
        self.response.out.write("<p> underconstruction <p>")
        
class Assignment2Part1Page(webapp2.RequestHandler): 
    def get(self):
        template_values = {
                           'app' : 'Demo1',
                           'author':['Xiqing Chu'],
                           'part1_url':'http://fb-friendcircle.appspot.com/part1'
                           }
           
        template = jinja_environment.get_template('newpart1.html')
        self.response.out.write(template.render(template_values))
         
app = webapp2.WSGIApplication([('/display', Display),('/part1', Assignment2Part1Page)],
                              debug=True)