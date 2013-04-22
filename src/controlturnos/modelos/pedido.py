import grok
from datetime import datetime
from zope import schema
from zope.interface import Interface

grok.templatedir("templates")


class Ipedido(Interface):
    nombre = schema.TextLine(
                    title=u"Nombre",
                    description=u"Nombre de la seccion",
                    required=True)
    pass


class Pedido(grok.Model):
    grok.implements(Ipedido)
    title = u''
    description = u''

    def __init__(self):
        super(Pedido, self).__init__()
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.lista = range(4)


class PedidoForm(grok.Form):
    grok.context(Pedido)
    grok.name('index')
    form_field = grok.AutoFields(Pedido)
    pass


class PedidoIndex(grok.View):
    grok.name("index")

    def update(self):
        self.context.now = datetime.now().strftime('%Y-%m-%d %H:%M')
