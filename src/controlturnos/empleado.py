# -*- coding: latin-1 -*-
'''
Created on 26/04/2013

@author: developer
'''

import grok
from controlturnos.interfaces import IContenido
from js.bootstrap import bootstrap
from controlturnos import resource

grok.templatedir('app_templates')


class Empleado(grok.Model):
    pass


class EmpleadoIndex(grok.View):
    grok.template('template')
    grok.require('ct.empleado')
    grok.name('index')

    def update(self):
        bootstrap.need()
        resource.style.need()


class EmpleadoIndexContenido(grok.Viewlet):
    grok.template('contenido_empleado')
    grok.viewletmanager(IContenido)
    grok.context(Empleado)
    grok.view(EmpleadoIndex)
