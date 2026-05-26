from django.contrib import admin
from .models import *

admin.site.register(StaffProfile)
admin.site.register(Area)
admin.site.register(Proceso)
admin.site.register(Paso)
admin.site.register(EjecucionProceso)
admin.site.register(EjecucionPaso)