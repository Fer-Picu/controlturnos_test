"""Clase seccion"""
 

from zope.interface import Interface
from zope import schema
import grok

grok.templatedir('app_templates')


class ISeccion(Interface):
    """Interfaz de Seccion"""

    nombre = schema.TextLine(
                    title=u"Nombre de la seccion",
                    description=u"Nombre de la seccion",
                    required=True)

    codigo = schema.TextLine(
                    title=u"Codigo",
                    description=u"Codigo de la seccion\
                                    para mostrar en la pantalla",
                    required=True)


    descripcion = schema.TextLine(
                    title=u"Lugar",
                    description=u"Lugar de la seccion",
                    required=True)


class Seccion(grok.Model):
    """"""
    
    grok.implements(ISeccion)
    
    def __init__(self, nombre, descripcion, codigo):
        """"""
        self.nombre = nombre
        self.descripcion = descripcion
        self.codigo = codigo

class ContenedorSecciones(grok.Container):
    
    def __init__(self):
        super(ContenedorSecciones, self).__init__()

    def obtener_lista_secciones(self):
        """Devuelve lista de objetos Seccion creados"""
        return [value for key, value in self.items()]

    def agregar_seccion(self, seccion):
        """Agrega una seccion"""
        self[seccion.codigo] = seccion

    def contiene_seccion(self, nombre):
        """Devuelve true si existe un nombre igual al ingresado"""
        if nombre in [seccion.nombre for seccion in self.values()]:
            return True
        return None
    
    def contiene_codigo(self, codigo):
        """Devuelve true si existe un codigo igual al ingresado"""
        if codigo in [seccion.codigo for seccion in self.values()]:
            return True
        return False
    

class ContenedorSeccionesIndex(grok.View):
    grok.context(ContenedorSecciones)
    grok.require('ct.admin')
    grok.template('seccion')
    grok.name('index')

    def update(self, seccion=None):
        if not seccion:
            return
        self.context.borrar_seccion(seccion)


class AddSeccion(grok.AddForm):
    grok.context(ContenedorSecciones)
    grok.name('agregar')
    grok.require('ct.admin')
    form_fields = grok.Fields(ISeccion)
    label = "Seccion"

    @grok.action(u"Agregar") # Boton agregar
    def handle_save(self, **data):
        # Si no se ingresan los datos pedidos, no agrega seccion
        if data['nombre'] is None or data['descripcion'] is None\
           or data['codigo'] is None:
            return
        if not data['codigo'].isalnum():
            return
        # No agrega la seccion si se repite el nombre de la seccion
        # o el codigo
        if self.context.contiene_seccion(data['nombre']) == True\
            or self.context.contiene_codigo(data['codigo']) == True:
            pass
        else:        
            self.context.agregar_seccion(Seccion(data['nombre'],
                                                 data['descripcion'],
                                                 data['codigo']))

        self.redirect(self.url('index'))
