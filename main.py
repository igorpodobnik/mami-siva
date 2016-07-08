#!/usr/bin/env python
import os
import jinja2
import webapp2

import cgi
import urllib

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import ndb
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


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




class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")

class AboutHandler(BaseHandler):
    def get(self):
        return self.render_template("about.html")

class ContactHandler(BaseHandler):
    def get(self):
        return self.render_template("contact.html")

class BlogHandler(BaseHandler):
    def get(self):
        return self.render_template("blog.html")


class Rezultati(BaseHandler):
    def get(self):
        self.response.out.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name')

        greetings = Greeting.query(
            ancestor=guestbook_key(guestbook_name)) \
            .order(-Greeting.date) \
            .fetch(10)

        for greeting in greetings:
            if greeting.author:
                self.response.out.write(
                    '<b>%s</b> wrote:' % greeting.author)
            else:
                self.response.out.write('An anonymous person wrote:')
            self.response.out.write('<div><img src="/img?img_id=%s"></img>' %
                                    greeting.key.urlsafe())
            self.response.out.write('<blockquote>%s</blockquote></div>' %
                                    cgi.escape(greeting.content))

        return self.render_template("rezultati.html")

class EmptyHandler(BaseHandler):
    def get(self):
        return self.render_template("empty.html")

class VnosKategorije(BaseHandler):
    def get(self):
        return self.render_template("vnoskategorije.html")

class Admin(BaseHandler):
    def get(self):
        return self.render_template("admin.html")

class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = users.get_current_user().nickname()

        greeting.content = self.request.get('content')

        avatar = self.request.get('img')

        greeting.avatar = avatar
        greeting.put()

        self.redirect('/rezultati')


class Image(webapp2.RequestHandler):
    def get(self):
        greeting_key = ndb.Key(urlsafe=self.request.get('img_id'))
        greeting = greeting_key.get()
        if greeting.avatar:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(greeting.avatar)
        else:
            self.response.out.write('No image')


def guestbook_key(guestbook_name=None):
    """Constructs a Datastore key for a Guestbook entity with name."""
    return ndb.Key('Guestbook', guestbook_name or 'default_guestbook')


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/about', AboutHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/blog', BlogHandler),
    webapp2.Route('/empty', EmptyHandler),
    webapp2.Route('/empty', EmptyHandler),
    webapp2.Route('/img', Image),
    webapp2.Route('/sign', Guestbook),
    webapp2.Route('/rezultati', Rezultati),
    webapp2.Route('/vnoskategorije', VnosKategorije),
    webapp2.Route('/admin', Admin),
], debug=True)
