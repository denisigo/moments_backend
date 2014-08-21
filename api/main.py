import json
import logging

from google.appengine.ext import webapp


# Global debug
debug = False

# Routes for handling moments
routes = [
    webapp.Route('/api/v1/moments', handler='api.v1.handlers.moments.MomentsHandler:get', methods=['GET']),
    webapp.Route('/api/v1/moments', handler='api.v1.handlers.moments.MomentsHandler:post', methods=['POST']),
]

class ApiWSGIApplication(webapp.WSGIApplication):
    """ Application class to implement self exception handling """
    
    def handle_exception(self, request, response, e):
        
        logging.exception(e)
        
        ret = None

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(e, webapp.HTTPException):
            response.set_status(e.code)
            
            message = e.title
            if e.detail:
                message = e.detail
            ret = {'error':{'code': e.code, 'message': message}}
        else:
            response.set_status(500)
            ret = {'error':{'code': 500}}
            
        # Set content type to application/json
        response.headers = {'Content-Type': 'application/json; charset=utf-8'}
        
        if ret:
            ret = json.dumps(ret)
            response.out.write(ret)

# Instantiate our application
application = ApiWSGIApplication(routes, debug=debug)