import grok

grok.templatedir("templates")


class Pedido(grok.Model):
    pass


class PedidoIndex(grok.View):
    grok.name("index")
    pass