import grok
from controlturnos.interfaces import IHead, ICabecera, IBarra, IContenido
from zope.interface import Interface

grok.templatedir("app_templates")


class SlotHead(grok.ViewletManager):
    grok.implements(IHead)
    grok.context(Interface)
    grok.name("slothead")


class SlotCabecera(grok.ViewletManager):
    grok.implements(ICabecera)
    grok.context(Interface)
    grok.name("slotcabecera")


class SlotBarra(grok.ViewletManager):
    grok.implements(IBarra)
    grok.context(Interface)
    grok.name("slotbarra")


class SlotContenido(grok.ViewletManager):
    grok.implements(IContenido)
    grok.context(Interface)
    grok.name("slotcontenido")


#==============================================================================
# Viewlets genericos de la aplicacion
#==============================================================================

class ViewletHead(grok.Viewlet):
    grok.viewletmanager(IHead)
    grok.context(Interface)
    grok.template("viewlet_head")
    grok.order(2)


class ViewletCabecera(grok.Viewlet):
    grok.viewletmanager(ICabecera)
    grok.context(Interface)
    grok.template("viewlet_cabecera")
    grok.order(2)


class ViewletLogin(grok.Viewlet):
    grok.viewletmanager(IBarra)
    grok.context(Interface)
    grok.template("viewlet_login")
    grok.order(2)


class ViewletLogout(grok.Viewlet):
    grok.viewletmanager(IBarra)
    grok.context(Interface)
    grok.template("viewlet_logout")
    grok.order(3)
