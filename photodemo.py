import cgi
import webapp2
from google.appengine.ext import db
from photoModel import Photo


class UploadPage(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("""
              <form action="/photodemo" enctype="multipart/form-data" method="post">
                <div>Upload image of customer</div>
                <div><input type="file" name="img"/></div>
                <div><input type="submit" value="upload"></div> 
              </form>
        """)
        
    def post(self):
        
        p = db.Blob(self.request.get('img'))
        
        newPhoto = Photo(picture = p)
        newPhoto.put()
        
        photo_list = Photo.all()
        if photo_list is not None:
            for e in photo_list:
                self.response.out.write('<hr>')
                self.response.out.write('<li><img src="photoget?pid=%s"/></li>'% e.key())
        
class Image(webapp2.RequestHandler):
    def get(self):
        p = db.get(self.request.get('pid'))
        if p.picture!= None:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(p.picture)
        else:
            self.error(404)
                

app = webapp2.WSGIApplication([('/photodemo', UploadPage),('/photoget',Image)],
                              debug=True)