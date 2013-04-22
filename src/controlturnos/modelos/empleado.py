import grok

grok.templatedir("templates")


class Empleado(grok.Model):
    pass


class EmpleadoIndex(grok.View):
    grok.name("index")
    grok.require('ct.empleado')
