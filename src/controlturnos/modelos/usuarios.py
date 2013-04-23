# -*- coding: latin-1 -*-

import grok
from zope.interface import Interface
from zope import component
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope import schema

grok.templatedir("templates")


class ContenedorUsuarios(grok.Container):

    def __init__(self):
        super(ContenedorUsuarios, self).__init__()


class ContenedorUsuariosIndex(grok.View):
    grok.context(ContenedorUsuarios)
    grok.require('ct.admin')
    grok.template('usuarioslista')
    grok.name('index')

    def update(self):
        usuarios = component.getUtility(IAuthenticatorPlugin,
                                        'usuarios_plugin')
        self.usuarios = usuarios.listUsers()


class IAddUserForm(Interface):
    usuario = schema.BytesLine(title=u'Usuario', required=True)
    password = schema.Password(title=u'Contraseña', required=True)
    confirmar_password = schema.Password(title=u'Confirmar contraseña',
                                         required=True)
    nombre_real = schema.BytesLine(title=u'Nombre real', required=True)
    rol = schema.Choice(title=u'Rol del usuario',
                         values=[u'empleado', u'administrador'],
                         required=True)


class AddUser(grok.Form):
    grok.context(ContenedorUsuarios)
    grok.require('ct.admin')
    grok.name('agregar')
    label = "Add user"
    form_fields = grok.Fields(IAddUserForm)
    error_color = "red"

    @grok.action('add')
    def handle_add(self, **data):
        usuarios = component.getUtility(IAuthenticatorPlugin,
                                        'usuarios_plugin')
        error = usuarios.addUser(data['usuario'], data['password'],
                            data['confirmar_password'],
                            data['nombre_real'], data['rol'])
        if error:
            self.label = "error: " + error
            self.redirect(self.url(self.context), 'agregar')
            return
        self.redirect(self.url(self.context))
