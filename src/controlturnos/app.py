import grok

from controlturnos import resource
from controlturnos.usuarios import Usuarios

# imports de modelos

from zope.pluggableauth import PluggableAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.authentication.interfaces import IAuthentication
from auth import instalar_autentificacion, PluginAuthenticacion


class Controlturnos(grok.Application, grok.Container):
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=instalar_autentificacion)
    grok.local_utility(PluginAuthenticacion,
                       provides=IAuthenticatorPlugin,
                       name='autenticacion')

    def __init__(self):
        super(Controlturnos, self).__init__()
        self['usuarios'] = Usuarios


class Index(grok.View):
    grok.require('zope.Public')


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
