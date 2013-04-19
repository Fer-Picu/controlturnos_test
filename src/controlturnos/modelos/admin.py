import grok

grok.templatedir("templates")


class Admin(grok.Model):
    pass


class AdminIndex(grok.View):
    grok.name("index")
