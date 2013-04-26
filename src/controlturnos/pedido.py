import grok
from datetime import datetime
grok.templatedir("app_templates")


"""
Este modelo necesita:
de SECCIONES:
            *un metodo que por un metodo llamado:
                    obtener_lista_de_secciones()
                    En forma de lista
"""


class Pedido(grok.Model):
    title = u''

    def actualizarNombresDeSecciones(self):
        self.lista_secciones = self.__parent__['secciones'].\
                                    obtener_lista_secciones()
        self._p_changed = True

    def __init__(self):
        super(Pedido, self).__init__()
        self.lista_secciones = []

    def pedirUnTicket(self, seccion_codigo):
        seccion = self.traerUnaSeccion(seccion_codigo)
        nuevo_ticket = self.__parent__["tickets"].agregarTicket(\
                                                seccion)
        return nuevo_ticket

    def traerUnaSeccion(self, seccion_codigo):
        seccion = self.__parent__['secciones'].obtener_seccion_por_codigo\
                                                    (seccion_codigo)
        return seccion


class PedidoIndex(grok.View):
    grok.name("index")

    def update(self, seccion_codigo=None, seccion_nombre=None):
        self.context.actualizarNombresDeSecciones()
        if seccion_codigo == None:
            pass
        else:
            nuevo_ticket = self.context.pedirUnTicket(seccion_codigo)
            self.redirect(self.url(self.context.__parent__\
                                ["tickets"][nuevo_ticket], 'index'))
