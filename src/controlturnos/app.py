import grok
from js.bootstrap import bootstrap
from controlturnos import resource
from controlturnos.usuarios import Usuarios
from controlturnos.seccion import ContenedorSecciones
from controlturnos.ticket import ContenedorTickets
#from controlturnos.pedido import 

# imports de modelos

from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from auth import instalar_autentificacion, PluginAuthenticacion


from controlturnos.interfaces import IContenido
from controlturnos.empleado import Empleado


class Controlturnos(grok.Application, grok.Container):
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=instalar_autentificacion)
    grok.local_utility(PluginAuthenticacion,
                       provides=IAuthenticatorPlugin,
                       name='autenticacion')

    def __init__(self):
        super(Controlturnos, self).__init__()
        self['usuarios'] = Usuarios()
        self.titulo = "Control de Turnos"
        self["seccion"] = ContenedorSecciones()
        self["empleado"] = Empleado()
        self["ticket"] = ContenedorTickets()

    def app(self):
        return self


class Index(grok.View):
    grok.require('zope.Public')
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


class PermisosEmpleado(grok.Permission):
    """Permisos para empleado"""
    grok.name('ct.empleado')


class RolEmpleado(grok.Role):
    """Rol de empleado"""
    grok.name('ct.empleadorol')
    grok.permissions('ct.empleado', 'ct.logueado')


class PermisosAdmin(grok.Permission):
    """Permisos para administrador"""
    grok.name('ct.admin')


class RolAdmin(grok.Role):
    """Rol de administrador"""
    grok.name('ct.adminrol')
    grok.permissions('ct.admin', 'ct.logueado')


class PermisosLogueado(grok.Permission):
    grok.name('ct.logueado')
