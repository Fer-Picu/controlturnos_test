import grok

from controlturnos import resource

class Controlturnos(grok.Application, grok.Container):
    pass

class Index(grok.View):
    def update(self):
        resource.style.need()
