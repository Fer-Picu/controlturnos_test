"""Clase seccion"""

from js.bootstrap import bootstrap
from controlturnos import resource
from zope.interface import Interface
from zope import schema
from interfaces import IContenido
from zope import component
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

    def obtener_titulo(self):
        return self.__parent__.obtener_titulo()
    
    def app(self):
        return self.__parent__.app()


class ContenedorSecciones(grok.Container):

    def __init__(self):
        super(ContenedorSecciones, self).__init__()
        self.titulo = "Secciones"

    def app(self):
        return self.__parent__.app()

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
    
    def borrar_seccion(self, seccion):
        """Borrar seccion seleccionada"""
        self.__delitem__(seccion)


class ContenedorSeccionesIndex(grok.View):
    grok.context(ContenedorSecciones)
    grok.require('ct.admin')
    grok.template('template')
    grok.name('index')

    def update(self, seccion=None):
        bootstrap.need()
        resource.style.need()
        if not seccion:
            return
        self.context.borrar_seccion(seccion)


class ContenedorSeccionesIndexContenido(grok.Viewlet):
    grok.viewletmanager(IContenido)
    grok.context(ContenedorSecciones)
    grok.view(ContenedorSeccionesIndex)
    grok.template("contenido_seccion")
    grok.order(0)


class AddSeccion(grok.AddForm):
    grok.context(ContenedorSecciones)
    grok.require('ct.admin')
    form_fields = grok.Fields(ISeccion)
    label = "Seccion"

    @grok.action(u"Agregar")  # Boton agregar
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
        
class SeccionEdit(grok.EditForm):
    grok.context(Seccion)
    grok.require('ct.admin')
    grok.name('index')
    form_fields = grok.AutoFields(ISeccion)
    label = 'Editar campos'

    @grok.action('Guardar cambios')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context.__parent__))

class AddSeccionView(grok.View):
    grok.context(ContenedorSecciones)
    grok.name('agregar')
    grok.require('ct.admin')
    grok.template('template')

    def update(self):
        bootstrap.need()
        resource.style.need()


class AddSeccionContenido(grok.Viewlet):
    grok.viewletmanager(IContenido)
    grok.context(ContenedorSecciones)
    grok.view(AddSeccionView)

    def update(self):
        self.form = component.getMultiAdapter((self.context, self.request), name='addseccion')
        self.form.update_form()
        if self.request.method == 'POST':
#             app = self.context.__parent__
#             self.__parent__.redirect(self.__parent__.url(obj=app))
            self.view.url(name='index')

    def render(self):
        return self.form.render()
