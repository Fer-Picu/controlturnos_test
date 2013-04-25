import grok
from js.bootstrap import bootstrap
from controlturnos import resource

from controlturnos.interfaces import IContenido

import secciones
import usuarios
import tickets


class Controlturnos(grok.Application, grok.Container):

    def __init__(self):
        super(Controlturnos, self).__init__()
        self.titulo = "Control de Turnos"


class Index(grok.View):
    grok.template("template")

    def update(self):
        bootstrap.need()
        resource.style.need()


class IndexContenido(grok.Viewlet):
    grok.viewletmanager(IContenido)
    grok.context(Controlturnos)
    grok.view(Index)
    grok.template("contenido_index")
    grok.order(0)
