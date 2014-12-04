from google.appengine.ext import db

class Photo(db.Model):
    picture = db.BlobProperty()
    
class PhotoOperation():
    def storePhoto(self, photo):
        newPhoto = Photo(picture = photo)
        newPhoto.put()
        
    def listPhotos(self):
        q = db.GqlQuery("SELECT * FROM Photo")
        return q