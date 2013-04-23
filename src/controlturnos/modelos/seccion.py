"""Clase seccion"""

from zope.interface import Interface
from zope import schema
import grok

grok.templatedir('templates')


class ISeccion(Interface):
    """Interfaz de Seccion"""

    nombre = schema.TextLine(
                    title=u"Nombre",
                    description=u"Nombre de la seccion",
                    required=True)

    codigo = schema.TextLine(
                    title=u"Codigo",
                    description=u"Codigo utilizado para abreviar\
                                  el nombre de la seccion. Tiene que\
                                  ser alfanumerico",
                    required=True)

    descripcion = schema.Text(
                    title=u"Descripcion",
                    description=u"Descripcion de la seccion",
                    required=True)


class Seccion(grok.Model):
    """"""

    grok.implements(ISeccion)

    def __init__(self, nombre, descripcion, codigo):
        """"""
        self.nombre = nombre
        self.descripcion = descripcion
        self.codigo = codigo
        self.turno = 0


class SeccionEdit(grok.EditForm):
    grok.context(Seccion)
    grok.name('index')
    form_fields = grok.AutoFields(ISeccion)
    label = 'Editar campos'

    @grok.action('Guardar cambios')
    def edit(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url(self.context.__parent__))


class ContenedorSecciones(grok.Container):

    def __init__(self):
        super(ContenedorSecciones, self).__init__()

    def obtener_lista_secciones(self):
        """Devuelve lista de objetos Seccion creados"""
        return [value for key, value in self.items()]

    def agregar_seccion(self, seccion):
        """Agrega una seccion"""
        self[seccion.codigo] = seccion

    def obtener_seccion_por_nombre(self, nombre):
        """
        Devuelve seccion con el nombre pasado si tal existe
        en otro caso devuelve None
        """
        if nombre in self.keys():
            return self[nombre]
        return None

    def contiene_nombre(self, nombre):
        """Devuelve true si tiene self[nombre]"""
        if nombre in self.keys():
            return True
        return False

    def borrar_seccion(self, seccion):
        self.__delitem__(seccion)


class ContenedorSeccionesIndex(grok.View):
    grok.context(ContenedorSecciones)
    grok.template('seccionesindex')
    grok.name('index')

    def update(self, seccion=None):
        if not seccion:
            return
        self.context.borrar_seccion(seccion)


class AddSeccion(grok.AddForm):
    grok.context(ContenedorSecciones)
    grok.name('agregar')
    form_fields = grok.Fields(ISeccion)
    label = "Agregue seccion nueva"

    @grok.action(u"Guardar seccion")
    def handle_save(self, **data):
        if data['nombre'] is None or data['descripcion'] is None\
           or data['codigo'] is None:
            return
        if not data['codigo'].isalnum():
            return
        self.context.agregar_seccion(Seccion(data['nombre'],
                                            data['descripcion'],
                                            data['codigo']))
        self.redirect(self.url('index'))
