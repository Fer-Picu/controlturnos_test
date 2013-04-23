# -*- coding: latin-1 -*-
'''
Created on 19/04/2013

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

from zope.password.interfaces import IPasswordManager

grok.templatedir('app_templates')


def setup_authentication(pau):
    """Instalacion del PAU"""
    pau.credentialsPlugins = ['credenciales']
    pau.authenticatorPlugins = ['usuarios_plugin']


class MySessionCredentialsPlugin(grok.GlobalUtility,
                                 SessionCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credenciales')
    loginpagename = 'login'
    loginfield = 'login'
    passwordfield = 'password'


class ILoginForm(Interface):
    login = schema.BytesLine(title=u'Usuario', required=True)
    camefrom = schema.BytesLine(title=u'', required=False)
    password = schema.Password(title=u'Contraseña', required=True)


class Login(grok.Form):
    grok.context(Interface)
    grok.require('zope.Public')
    label = "Login"
    prefix = ''
    form_fields = grok.Fields(ILoginForm)

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


class UserAuthenticatorPlugin(grok.LocalUtility):
    grok.implements(IAuthenticatorPlugin)
    grok.name('usuarios_plugin')

    def __init__(self):
        self.user_folder = UserFolder()

    def authenticateCredentials(self, credenciales):
        if not isinstance(credenciales, dict):
            return None
        if not ('login' in credenciales and 'password' in credenciales):
            return None
        cuenta = self.getAccount(credenciales['login'])
        if cuenta is None:
            return None
        if not cuenta.checkPassword(credenciales['password']):
            return None
        return PrincipalInfo(id=cuenta.nombre,
                             title=cuenta.nombre_real,
                             description=cuenta.nombre_real)

    def principalInfo(self, id):
        cuenta = self.getAccount(id)
        if cuenta is None:
            return None
        return PrincipalInfo(id=cuenta.nombre,
                             title=cuenta.nombre_real,
                             description=cuenta.description)

    def getAccount(self, usuario):
        """Devuelve la cuenta del """
        return usuario in self.user_folder and self.user_folder[usuario] or None

    def addUser(self, nombre, password, confirm_password, nombre_real, rol):
        error = self.checkFields(nombre, password, confirm_password)
        if error:
            return error
        if nombre not in self.user_folder:
            user = Cuenta(nombre, password, nombre_real, rol)
            self.user_folder[nombre] = user
            role_manager = IPrincipalRoleManager(grok.getSite())
            if rol == u'empleado':
                role_manager.assignRoleToPrincipal('ct.empleadorol',
                                                   nombre)
            if rol == u'administrador':
                role_manager.assignRoleToPrincipal('ct.adminrol',
                                                   nombre)

    def checkFields(self, nombre, password, confirm_password):
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

    def listUsers(self):
        return [user for user in self.user_folder.values()]


class UserFolder(grok.Container):
    pass


class PrincipalInfo(object):
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None


class Cuenta(grok.Model):

    def __init__(self, nombre, password, nombre_real, rol):
        self.nombre = nombre
        self.nombre_real = nombre_real
        self.rol = rol
        self.setPassword(password)

    def setPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        self.password = passwordmanager.encodePassword(password)

    def checkPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        return passwordmanager.checkPassword(self.password,
                                             password)
