class messageobj:
    def __init__(self, message, unzip=False):
        self.message = message
        self.unzip = unzip


class Var(object):
    tdict = dict()
    upload_as_doc = dict()
    q_link = dict()
