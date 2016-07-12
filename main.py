#!/usr/bin/env python
import os
import jinja2
import webapp2

import cgi
import urllib

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import mail
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore



params={}

def is_logged_in(params):
    p=params
    user = users.get_current_user()
    if user:
        preverialiobstaja()
        admin=preverialiadmin()
        logiran = True
        logout_url = users.create_logout_url('/')
        paramsif = {"logiran": logiran, "logout_url": logout_url, "user": user, "admin": admin}
    else:
        logiran = False
        login_url = users.create_login_url('/')
        paramsif = {"logiran": logiran, "login_url": login_url, "user": user}
    p.update(paramsif)
    return paramsif

def preverialiobstaja():
    user = users.get_current_user()
    emailprejemnika = user.email()
    user = Uporabniki(user=emailprejemnika)
    # preverjam ce je user ze v bazi
    prisoten = Uporabniki.query(Uporabniki.user == emailprejemnika).fetch()
    if prisoten:
        print "NOTRI JE ZE!"
    else:
        user.put()
        mail.send_mail("podobnik.igor@gmail.com", "podobnik.igor@gmail.com", "Nov uporabnik", "Novega userja imas in sicer %s" %emailprejemnika)

def preverialiadmin():
    user = users.get_current_user()
    emailprejemnika = user.email()
    admin = Uporabniki.query(ndb.AND(Uporabniki.user == emailprejemnika, Uporabniki.admin == True)).fetch()
    if admin:
        return True
    else:
        return False




class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))

class Greeting(ndb.Model):
    """Models a Guestbook entry with an author, content, avatar, and date."""
    author = ndb.StringProperty()
    content = ndb.TextProperty()
    avatar = ndb.BlobProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class Categorija(ndb.Model):
    cat_slika = ndb.BlobProperty()
    cat_naslov = ndb.StringProperty()
    cat_opis = ndb.TextProperty()
    cat_aktivni = ndb.BooleanProperty(default=True)

class Slike(ndb.Model):
    kategorija = ndb.StringProperty()
    opis = ndb.TextProperty()
    slika = ndb.BlobProperty()
    datum = ndb.DateTimeProperty(auto_now_add=True)

class Uporabniki(ndb.Model):
    user = ndb.StringProperty()
    approved = ndb.BooleanProperty(default=False)
    admin = ndb.BooleanProperty(default=False)


class MainHandler(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("index.html", params=params)

class AboutHandler(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("about.html", params=params)

class ContactHandler(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("contact.html", params=params)

class BlogHandler(BaseHandler):
    def get(self):

        vsekategorije = Categorija.query().fetch()
        params = {"kat" : vsekategorije}
        is_logged_in(params)

        return self.render_template("blog.html", params=params)


class EmptyHandler(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("empty.html", params=params)

class VnosKategorije(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("vnoskategorije.html", params=params)

class Admin(BaseHandler):
    def get(self):
        is_logged_in(params)
        return self.render_template("admin.html", params=params)



class KreirajKategorijo(webapp2.RequestHandler):
    def post(self):
        naslov = self.request.get('kat_naslov')
        kat = Categorija(parent=kat_key(naslov))
        kat.cat_opis = self.request.get('kat_opis')
        slika = self.request.get('kat_slika')
        kat.cat_slika = slika
        kat.cat_naslov = naslov
        kat.put()
        self.redirect('/blog')



def kat_key(naslov=None):
    return ndb.Key('Naslov', naslov or 'def_naslov')


class Image(webapp2.RequestHandler):
    def get(self):
        is_logged_in(params)
        categorija_key = ndb.Key(urlsafe=self.request.get('img_id'))
        katt = categorija_key.get()
        if katt.cat_slika:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(katt.cat_slika)
        else:
            self.response.out.write('No image')


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/about', AboutHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/blog', BlogHandler),
    webapp2.Route('/empty', EmptyHandler),
    webapp2.Route('/img', Image),
    webapp2.Route('/kreirajkat', KreirajKategorijo),
    webapp2.Route('/vnoskategorije', VnosKategorije),
    webapp2.Route('/admin', Admin),
], debug=True)
