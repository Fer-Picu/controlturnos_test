import grok

grok.templatedir("templates")


class Admin(grok.Model):

    def __init__(self):
        pass


class AdminIndex(grok.View):
    grok.require('ct.admin')
    grok.name("index")
