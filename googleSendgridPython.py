from sendgrid import Sendgrid
from sendgrid import Message
from google.appengine.api import users

import jinja2
import os

import cgi
import webapp2

jinja_environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)))    

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()

        if user:
            template = jinja_environment.get_template('index.html')
            self.response.out.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))

class SendEmail(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()

        if user is None:
            self.redirect('/')

        # get values from form
        subject = cgi.escape(self.request.get('subject'))
        toAddress = cgi.escape(self.request.get('toAddress'))
        content = cgi.escape(self.request.get('content'))

        # make a secure connection to SendGrid
        # <sendgrid_username>,<sendgrid_password> should be replaced with the SendGrid credentials
        s = Sendgrid('<sendgrid_username>', '<sendgrid_password>', secure = True)

        message = None

        # make a message object
        try:
            message = Message(user.email(), subject, content, content)
        except Exception, msg:
            response = msg
            pass

        if message != None:
            # add a recipient
            try:
                message.add_to(toAddress)
            except Exception, msg:
                response = msg
                pass

            # use the Web API to send your message
            try:
                response = s.web.send(message)
            except Exception, msg:
                response = msg
                pass

        # check request response
        msgClass = '';
        if response == True:
            response = "Your request was successfully processed."
        else:
            msgClass = 'error';
            response = "Error: " + str(response.message)

        # display success.html template
        template_values = {
            'response': response,
            'msgClass' : msgClass
        }

        template = jinja_environment.get_template('success.html')
        self.response.out.write(template.render(template_values))

    def get(self):
        self.redirect('/')

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/send', SendEmail)],
                              debug=True)