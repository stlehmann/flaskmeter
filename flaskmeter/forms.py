
from wtforms import Form, DecimalField


class DataForm(Form):
    cpu = DecimalField('Current CPU Usage:')
    mem = DecimalField('Current Memory Usage:')
