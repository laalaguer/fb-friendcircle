#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
A barebones AppEngine application that uses Facebook for login.

1.  Make sure you add a copy of facebook.py (from python-sdk/src/)
    into this directory so it can be imported.
2.  Don't forget to tick Login With Facebook on your facebook app's
    dashboard and place the app's url wherever it is hosted
3.  Place a random, unguessable string as a session secret below in
    config dict.
4.  Fill app id and app secret.
5.  Change the application name in app.yaml.

"""
FACEBOOK_APP_ID = "PLEASE USE YOUR OWN APP ID....XIQIING CHU"
FACEBOOK_APP_SECRET = "USE YOUR OWN APP SECRET....XIQING CHU"

import facebook
import webapp2
import os
import jinja2
import urllib2
from photoModel import Photo

from google.appengine.ext import db
from webapp2_extras import sessions

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='thisisarandomnumber')


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)


class BaseHandler(webapp2.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if self.session.get("user"):
            # User is logged in
            return self.session.get("user")
        else:
            # Either used just logged in or just saw the first page
            # We'll see here
            cookie = facebook.get_user_from_cookie(self.request.cookies,
                                                   FACEBOOK_APP_ID,
                                                   FACEBOOK_APP_SECRET)
            if cookie:
                # Okay so user logged in.
                # Now, check to see if existing user
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    # Not an existing user so get user info
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(
                        key_name=str(profile["id"]),
                        id=str(profile["id"]),
                        name=profile["name"],
                        profile_url=profile["link"],
                        access_token=cookie["access_token"]
                    )
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                # User is now logged in
                self.session["user"] = dict(
                    name=user.name,
                    profile_url=user.profile_url,
                    id=user.id,
                    access_token=user.access_token
                )
                return self.session.get("user")
        return None

    def dispatch(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        """
        This snippet of code is taken from the webapp2 framework documentation.
        See more at
        http://webapp-improved.appspot.com/api/webapp2_extras/sessions.html

        """
        return self.session_store.get_session()


class HomeHandler(BaseHandler):
    def get(self):
        template = jinja_environment.get_template('newexample.html')
        self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=self.current_user
        )))


    def post(self):
        self.get();

class LogoutHandler(BaseHandler):
    def get(self):
        if self.current_user is not None:
            self.session['user'] = None

        self.redirect('/')

class PostTextHandler(BaseHandler):
    def post(self):
        text = self.request.get('chat_info')
        if text:
            text = text.encode('utf-8') # for non-english text 
            current_user = self.current_user
            if current_user:
                graph = facebook.GraphAPI(self.current_user['access_token'])
                graph.put_object("me", "feed", message=text)
                self.response.out.write('yes') # just a feedback response
            else:
                self.response.out.write('no') # just a feedback response
        else:
            self.response.out.write('no') # just a feedback repsonse
            
class PostImageURLHandler(BaseHandler):
    def post(self):
        pic_url = self.request.get('url')
        info = self.request.get('pic_info') # endcode to be international
        info = info.encode('utf-8')
        headers = {
                   'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
                   }
        req = urllib2.Request(
                              url = pic_url,
                              headers = headers
                              )
        try:
            my_file = urllib2.urlopen(req)
            graph = facebook.GraphAPI(self.current_user['access_token'])
            response = graph.put_photo(my_file, info)
            photo_url = ("http://www.facebook.com/"
                     "photo.php?fbid={0}".format(response['id']))
            self.redirect(str(photo_url))
        except Exception,e:
            self.response.out.write('<h1> Sorry! This Url is anti-Robot! </h1>')

class PostImageFileHandler(BaseHandler):
    def post(self):
        
        p = db.Blob(self.request.get('img')) # Get new pic 
        newPhoto = Photo(picture = p)
        newPhoto.put() # Store in DataBase
                
        try:
            # This links to our own website
            pic_url = 'http://fb-friendcircle.appspot.com/photoget?pid=%s'% newPhoto.key()
            my_file = urllib2.urlopen(pic_url)
            
            # endcode to be international
            info = self.request.get('pic_info') 
            info = info.encode('utf-8')
            
            # upload file
            graph = facebook.GraphAPI(self.current_user['access_token'])
            response = graph.put_photo(my_file, info)
            photo_url = ("http://www.facebook.com/"
                     "photo.php?fbid={0}".format(response['id']))
            self.redirect(str(photo_url))
        except Exception,e:
            self.response.out.write('<h1> Sorry! This File cannot be uploaded! </h1>')
            

class Image(webapp2.RequestHandler):
    def get(self):
        p = db.get(self.request.get('pid'))
        if p.picture!= None:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(p.picture)
        else:
            self.error(404)
            
class FriendsHandlerGraph(BaseHandler):
    def get(self):
        self.show_friends()
 
    def post(self):
        self.show_friends()
         
    def show_friends(self):
        friends_list = []
        current_user = self.current_user
        if current_user:
            graph = facebook.GraphAPI(self.current_user['access_token'])
            friends_list = graph.get_connections("me", "friends",limit='50')['data'] # Get 100 Friends at most
            for f in friends_list:
                f_pic_object = graph.get_object(f['id'],fields='picture')
                f_pic = f_pic_object['picture']
                f_pic_data = f_pic['data']
                f_pic_url = f_pic_data['url']
                f['u_pic'] = f_pic_url
        template = jinja_environment.get_template('friends.html')
        self.response.out.write(template.render(dict(
            facebook_app_id=FACEBOOK_APP_ID,
            current_user=self.current_user,
            friends_list=friends_list
        )))
        
class FriendsHandlerFQL(BaseHandler):
    def get(self):
        self.show_friends()
 
    def post(self):
        self.show_friends()
         
    def show_friends(self):
        current_user = self.current_user
        if current_user:
            graph = facebook.GraphAPI(self.current_user['access_token'])
            q = {
                 "q1": "SELECT uid, name, pic_square, pic_big ,current_location.id, current_location.name,sex,profile_url FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me() order by rand() limit 100 )",
                 "q2": "SELECT page_id,location.latitude, location.longitude FROM page WHERE page_id IN (SELECT current_location.id FROM #q1)"
                 }
            try:
                results_list = graph.fql(q) # a list with 2 elements: result of q1 and q2
                locations_list = results_list[1]['fql_result_set'] # a list of {page_id, location}
                names_list = results_list[0]['fql_result_set'] # a list of {uid,name,pic, current_location.id,etc}
            
            
                friends_list = []
                for l in locations_list:
                    if l['location']:
                        for n in names_list:
                            if n['current_location']:
                                if n['current_location']['id'] == l['page_id']:
                                    n['current_location']['latitude'] = l['location']['latitude']
                                    n['current_location']['longitude'] = l['location']['longitude']
                                    friends_list.append(n)  
                male = 0
                female = 0
                for n in names_list:
                    if n['sex'] == 'male':
                        male = male + 1
                    elif n['sex'] == 'female':
                        female = female + 1
                    else:
                        male = male + 1
                template = jinja_environment.get_template('friends2.html')
                self.response.out.write(template.render(dict(
                    facebook_app_id=FACEBOOK_APP_ID,
                    current_user=self.current_user,
                    friends_list=friends_list,
                    locations_list = locations_list,
                    names_list = names_list,
                    male = male,
                    female = female     
                )))                
            except Exception as data:
                self.response.out.write('<h1> Sorry! Cookies Expired, log out then login! </h1>')
                self.response.out.write('<a href="/"><h1> Link is here </h1></a>')
                


        
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/', HomeHandler), ('/logout', LogoutHandler),('/posttext',PostTextHandler),('/postimgurl',PostImageURLHandler),('/postimgfile',PostImageFileHandler),('/photoget',Image),('/friends',FriendsHandlerGraph),('/showfriends/',FriendsHandlerFQL)],
    debug=True,
    config=config
)
