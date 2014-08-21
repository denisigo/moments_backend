from datetime import datetime

from api.v1.handlers.basehandler import BaseHandler
import models
from models.moment import Moment

class MomentsHandler(BaseHandler):
    """ Moments handler """

    def get(self):
        """ Gets moments with given cursor and limit. """
        
        # Get request arguments
        cursor = self.request.get('cursor', None)
        limit = self.request.get('limit', None)
        from_time = self.request.get('from_time', None)
        
        # Try to convert them to expected types
        if limit is not None:
            try:
                limit = int(limit)
            except ValueError:
                self.abort(400, "limit must be a number");
                
        if from_time is not None:
            try:
                from_time = datetime.strptime(from_time, "%Y-%m-%dT%H:%M:%S")
            except:
                self.abort(400, "from_time must be ISO 8601 date")
                
        # Get moments from DB
        try:
            moments, next_cursor = Moment.get_moments(cursor=cursor, limit=limit, from_time=from_time)
        except (models.TypeError, models.ValueError) as e:
            self.abort(400, str(e))
        
        # Generate moments response list
        ret_moments = []
        if moments is not None:
            for moment in moments:
                ret_moments.append({'id': moment.id,
                                     'author_name': moment.author_name,
                                     'text': moment.text,
                                     'added': moment.added.isoformat()})
                
        # Pack response with cursor and moments
        if next_cursor is not None:
            next_cursor = next_cursor.urlsafe()
                
        ret = {'cursor': next_cursor,
               'moments': ret_moments}

        self.ret_json(ret)
        
    def post(self):
        """ Adds a new moment. """
        
        # Get decoded JSON request body
        data = self.request_body
        
        # Get request data
        author_name = data.get('author_name', "")
        text = data.get('text', "")
        
        # Create and put new moment
        try:
            # Remove microseconds
            added = datetime.now()
            added = added.replace(microsecond=0)
            
            moment = Moment()
            moment.author_name = author_name
            moment.text = text
            moment.added = added
            moment.put()
        except (models.TypeError, models.ValueError) as e:
            self.abort(400, str(e))