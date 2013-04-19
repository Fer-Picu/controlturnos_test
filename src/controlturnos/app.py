import grok

from controlturnos import resource

# imports de modelos
from modelos.pedido import Pedido
from modelos.admin import Admin
from modelos.empleado import Empleado
from modelos.lista import Lista

# imports de clases
from ticket import ContenedorTickets
from seccion import ContenedorSecciones
from usuario import ContenedorUsuarios


class Controlturnos(grok.Application, grok.Container):
    def __init__(self):
        self["pedido"] = Pedido()
        self["admin"] = Admin()
        self["empleado"] = Empleado()
        self["lista"] = Lista()
        self["tickets"] = ContenedorTickets()
        self["secciones"] = ContenedorSecciones()
        self["usuarios"] = ContenedorUsuarios()
        


class Index(grok.View):
    def update(self):
        resource.style.need()
