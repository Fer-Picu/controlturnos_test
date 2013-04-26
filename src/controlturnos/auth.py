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
from zope.interface import Invalid

from zope.authentication.interfaces import ILogout
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.authentication.interfaces import IAuthentication
from zope.securitypolicy.interfaces import IPrincipalRoleManager

from zope import component
from zope import schema

from interfaces import IContenido
from js.bootstrap import bootstrap
import resource

from zope.i18nmessageid.message import MessageFactory as _

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


class Login(grok.View):
    grok.context(Interface)
    grok.name('login')
    grok.require('zope.Public')
    grok.template('template')

    def update(self):
        bootstrap.need()
        resource.style.need()
        self.site = grok.getApplication()


class LoginForm(grok.Form):
    grok.context(Interface)
    grok.name("login-form")
    label = "Login"
    prefix = ''
    form_fields = grok.Fields(ILoginFormulario)

    def setUpWidgets(self, ignore_request=False):
        super(LoginForm, self).setUpWidgets(ignore_request)
        self.widgets['camefrom'].type = 'hidden'

    @grok.action('login')
    def handle_login(self, **data):
        authenticated = not IUnauthenticatedPrincipal.providedBy(
            self.request.principal,
        )
        if authenticated:
            camefrom = self.request.form.get('camefrom')
            if camefrom:
                self.redirect(camefrom, self.url(grok.getSite()))
            else:
                self.redirect(self.url(grok.getSite()))
            self.flash(u'Logueado!', type=u'message')
        else:
            self.status = u'Autenticación fallida'
            self.errors += (Invalid(u'Usuario y/o contraseña invalidos'),)
            self.form_reset = False


class LoginContenido(grok.Viewlet):
    grok.viewletmanager(IContenido)
    grok.context(Interface)
    grok.view(Login)

    def update(self):
        self.form = component.getMultiAdapter((self.context, self.request), name='login-form')
        self.form.update_form()
        if self.request.method == 'POST':
#             app = self.context.__parent__
#             self.__parent__.redirect(self.__parent__.url(obj=app))
            self.view.url(name='index')

    def render(self):
        return self.form.render()


class Logout(grok.View):
    grok.context(Interface)
    grok.require('zope.Public')

    def render(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)

        self.flash(_(u'Usted ha deslogueado'), type=u'message')
        return self.redirect(self.application_url())


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
        cuenta = self.obtenerCuenta(credenciales['login'])
        if cuenta is None:
            return None
        if not cuenta.verificarPassword(credenciales['password']):
            return None
        return PrincipalInfo(id=cuenta.usuario,
                             title=cuenta.nombre_real,
                             description=cuenta.nombre_real)

    def principalInfo(self, id):
        cuenta = self.obtenerCuenta(id)
        if cuenta is None:
            return None
        return PrincipalInfo(id=cuenta.usuario,
                             title=cuenta.nombre_real,
                             description=cuenta.nombre_real)

    def obtenerCuenta(self, usuario):
        """Devuelve la cuenta del contenedor_cuentas[usuario]"""
        return usuario in self.contenedor_cuentas\
                        and self.contenedor_cuentas[usuario] or None

    def agregarUsuario(self, usuario, password,
                        confirm_password, nombre_real, rol, seccion):
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
        else:
            return u"El nombre de usuario ya existe"

    def borrarUsuario(self, usuario):
        if usuario in self.contenedor_cuentas:
            role_manager = IPrincipalRoleManager(grok.getSite())
            rol = role_manager.getRolesForPrincipal(usuario)[0]
            role_manager.removeRoleFromPrincipal(rol[0], usuario)
            del self.contenedor_cuentas[usuario]

    def listarUsuarios(self):
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
