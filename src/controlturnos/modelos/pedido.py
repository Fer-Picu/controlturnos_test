import grok
from datetime import datetime
grok.templatedir("templates")


class Pedido(grok.Model):
    def __init__(self):
        super(Pedido, self).__init__()
        self.now = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.lista = range(4)


class PedidoIndex(grok.View):
    grok.name("index")

    def update(self):
        self.context.now = datetime.now().strftime('%Y-%m-%d %H:%M')
