import grok

from controlturnos import resource
from js.bootstrap import bootstrap

# imports de modelos

from modelos.admin import Admin
from modelos.pedido import Pedido
from modelos.empleado import Empleado
from modelos.lista import Lista
from modelos.ticket import ContenedorTickets
from modelos.seccion import ContenedorSecciones

from controlturnos.modelos.usuarios import ContenedorUsuarios
from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from auth import setup_authentication
from auth import UserAuthenticatorPlugin


class Controlturnos(grok.Application, grok.Container):
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_authentication)
    grok.local_utility(UserAuthenticatorPlugin,
                       provides=IAuthenticatorPlugin,
                       name='usuarios_plugin')

    def __init__(self):
        print grok.templatedir.__doc__
        super(Controlturnos, self).__init__()
        self["admin"] = Admin()
        self["empleado"] = Empleado()
        self["lista"] = Lista()
        self["tickets"] = ContenedorTickets()
        self["secciones"] = ContenedorSecciones()
        self["usuarios"] = ContenedorUsuarios()
        self["pedido"] = Pedido()


class Index(grok.View):
    grok.require('zope.Public')

    def update(self):
        bootstrap.need()


class PermisosEmpleado(grok.Permission):
    """Permisos para empleado"""
    grok.name('ct.empleado')


class RolEmpleado(grok.Role):
    """Rol de empleado"""
    grok.name('ct.empleadorol')
    grok.permissions('ct.empleado')


class PermisosAdmin(grok.Permission):
    """Permisos para administrador"""
    grok.name('ct.admin')


class RolAdmin(grok.Role):
    """Rol de administrador"""
    grok.name('ct.adminrol')
    grok.permissions('ct.admin')
