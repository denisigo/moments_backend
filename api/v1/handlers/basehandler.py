import json

from google.appengine.ext import webapp

class BaseHandler(webapp.RequestHandler):
    """ Base handler for API. Implements basic I/O functions """
    
    def __init__(self, request, response):
        super(BaseHandler, self).__init__(request, response)
    
    def ret_json(self, payload, status=200):
        """ Sets given payload to response with given HTTP status.
        Automatically dumps dicts or lists to json. """
        
        self.response.headers = {'Content-Type': 'application/json; charset=utf-8'}
        
        if isinstance(payload, dict) or isinstance(payload, list):
            payload = json.dumps(payload)
        
        self.response.set_status(status)
        self.response.out.write(payload)
    
    @property
    def request_body(self):
        """ Gets request body decoded from json """
        
        try:
            body = json.loads(self.request.body)
        except ValueError:
            self.abort(400, 'Unable to parse request body.')
        else:
            return body