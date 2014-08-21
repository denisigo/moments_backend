from datetime import datetime

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

from models import ValueError, TypeError

def author_name_validator(prop, value):
    """ Validator for author name. Author name can be empty (anonymous) """

    return value.strip()

def text_validator(prop, value):
    """ Validator for text. Text can't be empty """

    value = value.strip()
    if not value:
        raise ValueError("Text is empty")
    return value

class Moment(ndb.Model):
    """ Represents a moment """

    DEFAULT_LIMIT = 10
    MAX_LIMIT = 25

    @property
    def id(self):
        """ Handy property to get moment ID """
        return self.key.id()

    # Authod name
    author_name = ndb.StringProperty(indexed=False, validator=author_name_validator)
    # Moment text
    text = ndb.TextProperty(indexed=False, validator=text_validator)
    # Datetime when moment was added (timezone is UTC by default on GAE)
    added = ndb.DateTimeProperty(indexed=True)

    @classmethod
    def get_moments(cls, cursor=None, limit=DEFAULT_LIMIT, from_time=None):
        """ Gets moments. Use cursor or from_time as offset. 
        
        Args:
            cursor: ndb.Cursor instance or websafe string representation
            from_time: datetime instance to get Moments posted after this time (exclusive).
            limit: how much items to return
            
        Returns:
            tuple as (items, next_cursor)
        """

        # Perform arguments validation
        if cursor is not None:
            if not isinstance(cursor, ndb.Cursor):
                try:
                    cursor = ndb.Cursor().from_websafe_string(cursor)
                except datastore_errors.BadValueError:
                    raise ValueError("Cursor is not valid")

        if from_time is not None:
            if not isinstance(from_time, datetime):
                raise ValueError("from_time must be the type of datetime, but %s given" % (type(from_time)))

        if limit is None:
            limit = Moment.DEFAULT_LIMIT

        if not isinstance(limit, int):
            raise TypeError("Limit must be the type of integer, but %s given" % type(limit))

        if limit > Moment.MAX_LIMIT:
            raise ValueError("Limit is out of range. Max limit is %s" % Moment.MAX_LIMIT)

        # Query moments ordered by added time desc
        q = Moment.query()
        q = q.order(-Moment.added)
        
        # Use from_time if set
        if from_time is not None:
            q = q.filter(Moment.added > from_time)
            
        items, next_cursor, more = q.fetch_page(limit, start_cursor=cursor, keys_only=False)

        return items, next_cursor
