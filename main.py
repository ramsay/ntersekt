#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

class BaseHandler(webapp.RequestHandler):
    ''' My custom base handler for simple request handlers. Implements a render method to simplify rendering webapp
    templates.
    '''
    def render(self, template_path, args):
        '''Uses webapp.template to render the template at template_path using the args dict to fill in the template
        variables.
        '''
        self.response.out.write(
            template.render(template_path, args)
        )

from chat import ChatHandler

class MainHandler(BaseHandler):
    '''The simple index page for ntersekt. Gives a short explanation of the website and has options to start new chats
    regular and NSFW.
    '''
    def get(self):
        self.render("templates/index.html", {'page_title': "Welcome"})


def main():
    application = webapp.WSGIApplication(
        [('/', MainHandler),
         ('/chat', ChatHandler)],
        debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
