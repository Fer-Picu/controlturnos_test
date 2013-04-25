# -*- coding: latin-1 -*-
'''
Created on 25/04/2013

@author: sebastiang
'''

import grok


from zope.pluggableauth.plugins.session import SessionCredentialsPlugin
from zope.pluggableauth.interfaces import ICredentialsPlugin
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.pluggableauth.interfaces import IPrincipalInfo

from zope.interface import Interface

from zope.authentication.interfaces import ILogout
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import IAuthentication
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope import component
from zope import schema

from controlturnos.usuarios import Cuenta

grok.templatedir('app_templates')


def instalar_autentificacion(pau):
    """Instalacion del PAU"""
    pau.credentialsPlugins = ['credenciales']
    pau.authenticatorPlugins = ['autenticacion']


class PluginCredenciales(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credenciales')
    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'


class ILoginFormulario(Interface):
    login = schema.BytesLine(title=u'Usuario', required=True)
    camefrom = schema.BytesLine(title=u'', required=False)
    password = schema.Password(title=u'Contraseña', required=True)


class Login(grok.Form):
    grok.context(Interface)
    grok.require('zope.Public')
    label = "Login"
    prefix = ''
    form_fields = grok.Fields(ILoginFormulario)

    def setUpWidgets(self, ignore_request=False):
        super(Login, self).setUpWidgets(ignore_request)
        self.widgets['camefrom'].type = 'hidden'

    @grok.action('login')
    def handle_login(self, **data):
        camefrom = self.request.form.get('camefrom')
        if camefrom:
            self.redirect(camefrom)
            return
        self.redirect(self.application_url())


class Logout(grok.View):
    grok.context(Interface)
    grok.template('logout')
    grok.require('zope.Public')

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
        ILogout(auth).logout(self.request)


class PluginAuthenticacion(grok.LocalUtility):
    grok.implements(IAuthenticatorPlugin)
    grok.name('autenticacion')

    def __init__(self):
        self.contenedor_cuentas = ContenedorCuentas()

    def authenticateCredentials(self, credenciales):
        if not isinstance(credenciales, dict):
            return None
        if not ('login' in credenciales and 'password' in credenciales):
            return None
        cuenta = self.obtener_cuenta(credenciales['login'])
        if cuenta is None:
            return None
        if not cuenta.verificar_password(credenciales['password']):
            return None
        return PrincipalInfo(id=cuenta.nombre,
                             title=cuenta.nombre_real,
                             description=cuenta.nombre_real)

    def principalInfo(self, id):
        cuenta = self.obtener_cuenta(id)
        if cuenta is None:
            return None
        return PrincipalInfo(id=cuenta.nombre,
                             title=cuenta.nombre_real,
                             description=cuenta.description)

    def obtener_cuenta(self, usuario):
        """Devuelve la cuenta del contenedor_cuentas[usuario]"""
        return usuario in self.contenedor_cuentas\
                        and self.contenedor_cuentas[usuario] or None

    def agregar_usuario(self, usuario, password,
                        confirm_password, nombre_real, rol, seccion):
        error = self.verificar_campos(usuario, password, confirm_password)
        if error:
            return error
        if usuario not in self.contenedor_cuentas:
            user = Cuenta(usuario, password, nombre_real, rol, seccion)
            self.contenedor_cuentas[usuario] = user
            role_manager = IPrincipalRoleManager(grok.getSite())
            if rol == u'empleado':
                role_manager.assignRoleToPrincipal('ct.empleadorol',
                                                   usuario)
            if rol == u'administrador':
                role_manager.assignRoleToPrincipal('ct.adminrol',
                                                   usuario)

    def verificar_campos(self, nombre, password, confirm_password):
        if not nombre.isalnum():
            return "usuario solamente puede contener numeros y letras"
        elif not password.isalnum():
            return "password solamente puede contener numeros y letras"
        elif not password == confirm_password:
            return "las passwords no coinciden"
        elif len(nombre) > 20:
            return "usuario muy largo"
        else:
            return None

    def listar_usuarios(self):
        """Devuelve lista de cuentas creadas"""
        return [usuario for usuario in self.contenedor_cuentas.values()]


class ContenedorCuentas(grok.Container):
    pass


class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None
