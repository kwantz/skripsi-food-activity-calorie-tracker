
from dateutil.parser import parse as dateparse
from datetime import datetime, timezone
import pytz

class Datetime:

    def __init__(self, stringdate=None):
        if stringdate is None:
            self.date = datetime.utcnow()
        else:
            self.date = dateparse(stringdate)
            self.date.replace(tzinfo=pytz.UTC)

    def todate(self):
        return self.date