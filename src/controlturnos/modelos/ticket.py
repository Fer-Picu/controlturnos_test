import grok
from datetime import datetime
grok.templatedir("templates")


class ContenedorTickets(grok.Container):
    def __init__(self):
        super(ContenedorTickets, self).__init__()
        self.contadores = {}

    def incrementar_contador(self, codigo_seccion):
        if codigo_seccion in self.contadores:
            self.contadores[codigo_seccion] += 1
        else:
            self.contadores[codigo_seccion] = 1
        self._p_changed = True

    def agregar_ticket(self, seccion):
        self.incrementar_contador(seccion.codigo)
        ticket = Ticket(seccion, self.contadores[seccion.codigo])
        self[ticket.codigo()] = ticket
        return ticket.codigo()


class ContenedorTicketsIndex(grok.View):
    grok.context(ContenedorTickets)
    grok.template("contenedorticketsindex")
    grok.name("index")


class Ticket(grok.Model):
    def __init__(self, seccion, numero):
        super(Ticket, self).__init__()
        self.seccion = seccion
        self.hora_emision = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.codigo_seccion = seccion.codigo
        self.numero = numero
        self.atendido = False
        pass

    def codigo(self):
        a = self.codigo_seccion + str(self.numero).zfill(5)
        return a


class TicketIndex(grok.View):
    grok.context(Ticket)
    grok.template("ticketindex")
    grok.name("index")
