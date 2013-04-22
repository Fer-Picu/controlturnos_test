import grok

grok.templatedir("templates")


class Lista(grok.Model):
    pass


class ListaIndex(grok.View):
    grok.name("index")
    grok.require('zope.View')
