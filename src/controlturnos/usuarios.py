# -*- coding: latin-1 -*-
'''
Created on 25/04/2013

@author: sebastiang
'''


import grok
import re
from zope.interface import Interface, invariant, Invalid
from zope import component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope import schema
from zope.password.interfaces import IPasswordManager
from zope.i18nmessageid.message import MessageFactory as _

grok.templatedir("app_templates")


class Usuarios(grok.Container):

    def __init__(self):
        super(Usuarios, self).__init__()


class UsuariosIndex(grok.View):
    grok.context(Usuarios)
    grok.require('ct.admin')
    grok.template('usuarioslista')
    grok.name('index')

    def update(self):
        plugin_auth = component.getUtility(IAuthenticatorPlugin,
                                           'autenticacion')
        self.usuarios = plugin_auth.listarUsuarios()


class IAgregarUsuario(Interface):
    usuario = schema.BytesLine(title=u'Usuario', required=True)
    password = schema.Password(title=u'Contraseña', required=True)
    confirmar_password = schema.Password(title=u'Confirmar contraseña',
                                         required=True)
    nombre_real = schema.BytesLine(title=u'Nombre real', required=True)
    rol = schema.Choice(title=u'Rol del usuario',
                        values=[u'empleado', u'administrador'],
                        required=True)
    seccion = schema.Choice(title=u'Seccion para el empleado',
                            values=[u'seccionejemplo1', u'seccionejemplo2'],
                            required=False)

    @invariant
    def matching_passwords(form):
        if form.confirmar_password != form.password:
            raise Invalid(_('Passwords does not match'))

    @invariant
    def valid_login(form):
        if not re.compile('^[a-z0-9]+$').match(form.usuario):
            raise Invalid(_('Invalid user name, only characters in [a-z0-9] '
                            'are allowed'))


class IEditarUsuario(Interface):
    usuario = schema.BytesLine(title=u'Usuario', required=True)
    password = schema.Password(title=u'Contraseña', required=False)
    confirmar_password = schema.Password(title=u'Confirmar contraseña',
                                         required=False)
    nombre_real = schema.BytesLine(title=u'Nombre real', required=True)
    rol = schema.Choice(title=u'Rol del usuario',
                        values=[u'empleado', u'administrador'],
                        required=False)
    seccion = schema.Choice(title=u'Seccion para el empleado',
                            values=[u'seccionejemplo1', u'seccionejemplo2'],
                            required=False)

    @invariant
    def matching_passwords(form):
        if form.confirmar_password != form.password:
            raise Invalid('Passwords does not match')

    @invariant
    def valid_login(form):
        if not re.compile('^[a-z0-9]+$').match(form.usuario):
            raise Invalid('Invalid user name, only characters in [a-z0-9] '
                          'are allowed')


class Cuenta(grok.Model):

    def __init__(self, usuario, password, nombre_real, rol, seccion=None):
        self.usuario = usuario
        self.nombre_real = nombre_real
        self.rol = rol
        self.seccion = seccion
        self.asignarPassword(password)

    def asignarPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        self.password = passwordmanager.encodePassword(password)

    def verificarPassword(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        return passwordmanager.checkPassword(self.password,
                                             password)


class AgregarUsuario(grok.Form):
    grok.context(Usuarios)
    grok.require('ct.admin')
    grok.name('agregar')
    label = "Agregar usuario"
    form_fields = grok.Fields(IAgregarUsuario)
    template = grok.PageTemplateFile('app_templates/usuarioform.cpt')
    error_color = "red"

    @grok.action('Registrar')
    def handle_add(self, **data):
        plugin_auth = component.getUtility(IAuthenticatorPlugin,
                                           'autenticacion')
        error = plugin_auth.agregarUsuario(data['usuario'], data['password'],
                                            data['confirmar_password'],
                                            data['nombre_real'], data['rol'],
                                            data['seccion'])
        if error:
            self.status = u'Imposible registrar'
            self.errors += (Invalid(error),)
            self.form_reset = False
            return
        self.flash(u'Usuario agregado.', type=u'message')
        self.redirect(self.url(self.context))


class EditarUsuario(grok.Form):
    grok.context(Usuarios)
    grok.require('ct.admin')
    grok.name('editar')
    form_fields = grok.Fields(IEditarUsuario)
    template = grok.PageTemplateFile('app_templates/usuarioform.cpt')
    label = "Editar usuario"

    def setUpWidgets(self, ignore_request=False):
        plugin = component.getUtility(IAuthenticatorPlugin, 'autenticacion')
        usuario = plugin.obtenerCuenta(self.request.get('usuario'))
        super(EditarUsuario, self).setUpWidgets(ignore_request)
        if usuario:
            self.widgets['usuario'].extra = "readonly='true'"
            self.widgets['usuario'].setRenderedValue(usuario.usuario)
            self.widgets['nombre_real'].setRenderedValue(usuario.nombre_real)
            self.widgets['rol'].setRenderedValue(usuario.rol)
            self.widgets['seccion'].setRenderedValue(usuario.seccion)

    @grok.action('Guardar cambios')
    def handle_edit(self, **data):
        plugin = component.getUtility(IAuthenticatorPlugin, 'autenticacion')
        usuario = plugin.obtenerCuenta(self.request.form.get('form.usuario'))
        password = self.request.form.get('form.password')
        if password:
            usuario.asignarPassword(password)
        usuario.nombre_real = self.request.form.get('form.nombre_real')
        usuario.seccion = self.request.form.get('form.seccion')
        usuario.rol = self.request.form.get('form.rol')
        self.flash(u'Cambios guardados.', type=u'message')
        self.redirect(self.url(self.context))

    @grok.action('Cancelar - no funca')
    def handle_cancel(self, ignore_request=True):
        self.redirect(self.url(self.context))


class BorrarUsuario(grok.View):
    """Borra al usuario y vuelve a la lista de usuarios"""

    grok.context(Interface)
    grok.name('borrar')
    grok.require('ct.admin')

    def render(self):
        usuario = self.request.get('usuario', None)
        if usuario:
            plugin = component.getUtility(IAuthenticatorPlugin, 'autenticacion')
            plugin.borrarUsuario(usuario)
            self.flash(_(u'User deleted.'), type=u'message')
        else:
            self.flash(_(u'User not found.'), type=u'error')

        self.redirect(self.url(self.context))

