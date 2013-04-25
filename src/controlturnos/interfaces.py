from zope.interface import Interface


class IHead(Interface):
    """Interfaz para el Viewlet manager de head"""


class ICabecera(Interface):
    """Interfaz para el Viewlet manager de la cabecera"""


class IBarra(Interface):
    """Interfaz para el Viewlet manager de la barra"""


class IContenido(Interface):
    """Interfaz para el Viewlet manager del contenido"""
