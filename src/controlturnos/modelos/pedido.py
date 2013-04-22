import grok
from datetime import datetime
from zope import schema
from zope.interface import Interface
from ticket import ContenedorTickets
grok.templatedir("templates")


class Ipedido(Interface):
    nombre = schema.TextLine(
                    title=u"SOLICITAR TURNO",
                    required=True)


class Pedido(grok.Model):
    grok.implements(Ipedido)
    title = u''

    def traer_nombres_de_secciones(self):
        self.lista = []
        lista_aux = self.__parent__['secciones'].obtener_lista_secciones()
        if not lista_aux:
            return
        for cada_seccion in lista_aux:
            self.lista.append(cada_seccion)
        self._p_changed = True

    def __init__(self):
        super(Pedido, self).__init__()
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.lista = []


class PedidoForm(grok.Form):
    grok.context(Pedido)
    grok.name('pedido_test_field')
    form_field = grok.AutoFields(Ipedido)
    pass


class RetireTicket(grok.Model):
    def __init__(self):
        super(RetireTicket, self).__init__()


class RetireTicketIndex(grok.View):
    grok.name("retireticketindex")

class PedidoIndex(grok.View):
    grok.name("index")

    def update(self, seccion_codigo=None, seccion_nombre=None):
#         self.context.now = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.context.traer_nombres_de_secciones()
        if seccion_codigo == None:
            pass
        else:
            ContenedorTickets.agregar_ticket(seccion_nombre)
            self.redirect(self.context.RetireTicket, None, False )
            # AGREGAR un ticket a la lista de tickets y mostrar mensaje en pantalla
            pass
    