# -*- coding: latin-1 -*-
'''
Created on 25/04/2013

@author: sebastiang
'''


import grok
from zope.interface import Interface
from zope import component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope import schema
from zope.password.interfaces import IPasswordManager

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
        self.usuarios = plugin_auth.listar_usuarios()


class Cuenta(grok.Model):

    def __init__(self, nombre, password, nombre_real, rol, seccion=None):
        self.nombre = nombre
        self.nombre_real = nombre_real
        self.rol = rol
        self.seccion = seccion
        self.asignar_password(password)

    def asignar_password(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        self.password = passwordmanager.encodePassword(password)

    def verificar_password(self, password):
        passwordmanager = component.getUtility(IPasswordManager,
                                               'SHA1')
        return passwordmanager.checkPassword(self.password,
                                             password)


class ICuenta(Interface):
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


class AgregarUsuario(grok.Form):
    grok.context(Usuarios)
    grok.require('ct.admin')
    grok.name('agregar')
    label = "Add user"
    form_fields = grok.Fields(ICuenta)
    template = grok.PageTemplateFile('app_templates/usuarioform.cpt')
    error_color = "red"

    @grok.action('add')
    def handle_add(self, **data):
        plugin_auth = component.getUtility(IAuthenticatorPlugin,
                                           'autenticacion')
        error = plugin_auth.agregar_usuario(data['usuario'], data['password'],
                                            data['confirmar_password'],
                                            data['nombre_real'], data['rol'],
                                            data['seccion'])
        if error:
            self.label = "error: " + error
            self.redirect(self.url(self.context), 'agregar')
            return
        self.redirect(self.url(self.context))
