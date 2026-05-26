# Script para crear el proceso PROS-DES-09 (Checklist antes de pull request)
from core.models import Area, Proceso, Paso
from django.utils import timezone

def crear_proceso_pros_des_09():
    # 1. Obtener o crear el área 'Desarrollo'
    area, _ = Area.objects.get_or_create(
        nombre='Desarrollo',
        defaults={
            'descripcion': 'Área encargada del desarrollo y mantenimiento de software.',
            'minimo_requerido': 80
        }
    )
    print(f"✅ Área: {area.nombre}")

    nombre_proceso = "PROS-DES-09 Proceso para realizar checklist antes de hacer pull request"
    if Proceso.objects.filter(nombre=nombre_proceso).exists():
        print(f"⚠️ El proceso ya existe. No se creará duplicado.")
        return

    # 2. Crear el proceso
    proceso = Proceso.objects.create(
        nombre=nombre_proceso,
        area=area,
        objetivo="Tener 0 errores postproducción por cada deploy que se haga.",
        video_ayuda="https://wisphubmx.sharepoint.com/sites/WispHub/_layouts/15/stream.aspx?id=%2Fsites%2FWispHub%2FProcesos%2FDesarrollo%2FPROS%2DDES%2D09%20Proceso%20para%20realizar%20checklist%20antes%20de%20hacer%20pull%20request%2Emp4",
        nivel_critico='alta',
        tiempo_estimado=120,
        activo=True
    )
    print(f"✅ Proceso creado: {proceso.nombre}")

    # 3. Datos de los pasos (orden, nombre, descripcion_corta, ayuda_html, puntos, evidencia_tipo)
    pasos_data = [
        {
            "orden": 1,
            "nombre": "PASO 1: Crear issue en github. (Entregable)",
            "descripcion": "Crear un issue en GitHub con el formato PROS-DES-09 - {{Nombre del programador}}.",
            "ayuda_html": """<p><strong>Paso 1.1:</strong> Buscar issues relacionados con la siguiente consulta:</p>
<p><a href="https://github.com/desarrollowh/operacion-wisphub/issues?q=PROS-DES-09%20Proceso%20para%20realizar%20checklist%20antes%20de%20hacer%20pull%20request">https://github.com/desarrollowh/operacion-wisphub/issues?q=PROS-DES-09...</a></p>
<p><strong>Paso 1.2:</strong> Crear issue con el título: <code>PROS-DES-09 Proceso para realizar checklist antes de hacer pull request - {{Nombre del programador}}</code></p>
<p><strong>Entregable:</strong> Link al issue creado.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 2,
            "nombre": "PASO 2: Aplicar migraciones. (Programador) - (Evidencia con foto)",
            "descripcion": "Ejecutar makemigrations y migrate, y adjuntar captura de pantalla.",
            "ayuda_html": """<p>Comandos a ejecutar:</p>
<pre>python manage.py makemigrations<br>python manage.py migrate</pre>
<p><strong>NOTA:</strong> Adjuntar captura de evidencia mostrando la salida de los comandos.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 3,
            "nombre": "PASO 3: Documentar Codigo. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Documentar funciones, clases o métodos con docstrings claros.",
            "ayuda_html": """<p>Explicar qué hace la pieza de código. Usar docstrings con formato:</p>
<pre>def convertir_tiempo_mikrotik(tiempo):
    \"\"\"
    Esta función recibe el tiempo que mikrotik devuelve (1w15h35m16s) y lo formatea como 00d 00:00:00
    \"\"\"
    pass</pre>
<p>Para views, utils y tasks, explicar resumidamente el funcionamiento y las variables.</p>
<p><strong>NOTA:</strong> Adjuntar captura del código documentado (si aplica).</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 4,
            "nombre": "PASO 4: Utilizar el cache correctamente. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Centralizar el acceso a caché en una función específica por módulo.",
            "ayuda_html": """<p>Ejemplo de archivo <code>cache_factura.py</code>:</p>
<pre>def get_cache_facturas(empresa_slug, get_data=True):
    key = 'facturas-v3-' + empresa_slug
    if get_data:
        cache_facturas = cache.get(key)
        return key, cache_facturas if cache_facturas else {}
    return key</pre>
<p><strong>NOTA:</strong> Adjuntar captura del código donde se implementa.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 5,
            "nombre": "PASO 5: Validar desde el Form. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Realizar validaciones en el formulario (clean_*) en lugar de la vista.",
            "ayuda_html": """<p>Usar métodos <code>clean_&lt;campo&gt;</code> en los formularios para mantener la vista limpia.</p>
<p><strong>NOTA:</strong> Adjuntar captura del código del formulario.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 6,
            "nombre": "PASO 6: Evitar usar 'exclude' en los formularios. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Usar 'fields' en ModelForm en lugar de 'exclude'.",
            "ayuda_html": """<p>Ejemplo:</p>
<pre>class ExampleForm(forms.ModelForm):
    class Meta:
        model = Example
        fields = ['first', 'second']</pre>
<p><strong>NOTA:</strong> Adjuntar captura del formulario corregido.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 7,
            "nombre": "PASO 7: Revisar el numero de querys. (Programador) - (Evidencia con foto de django toolbar)",
            "descripcion": "Medir número de consultas usando Django Debug Toolbar o el logger incluido.",
            "ayuda_html": """<p>En vistas usar Django Debug Toolbar. Para tareas, usar el siguiente código:</p>
<pre>from django.db import connection
del connection.queries[:]

query_count = {"total": 0}

class QueryCounterHandler(logging.Handler):
    def emit(self, record):
        query_count["total"] += 1

logger = logging.getLogger("django.db.backends")
logger.addHandler(QueryCounterHandler())
logger.setLevel(logging.DEBUG)

# ... tu código ...

print("Consultas ejecutadas:", query_count["total"])</pre>
<p><strong>NOTA:</strong> Adjuntar captura del resultado.</p>""",
            "puntos": 15,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 8,
            "nombre": "PASO 8: Pruebas con más de 1000 registros. (Programador) - (Evidencia con foto de django toolbar)",
            "descripcion": "Probar listados con 100, 1000, 2000 y 3000 registros y verificar tiempo/respuesta.",
            "ayuda_html": """<p>Generar datos de prueba y medir con Django Debug Toolbar. Capturar el número de consultas y el tiempo de carga.</p>
<p><strong>NOTA:</strong> Adjuntar captura para cada prueba (o al menos la de 3000 registros).</p>""",
            "puntos": 15,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 9,
            "nombre": "PASO 9: Usar defer y only en las querys. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Optimizar consultas usando only() o defer() para traer solo campos necesarios.",
            "ayuda_html": """<p>Ejemplos:</p>
<pre># only: solo ciertos campos
usuarios = Usuario.objects.only('id', 'nombre')

# defer: excluir campos pesados
facturas = Factura.objects.defer('xml_factura')</pre>
<p><strong>NOTA:</strong> Adjuntar captura del código optimizado.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 10,
            "nombre": "PASO 10: Nombrar variables y funciones explícitamente. (Programador) - (Evidencia con foto)",
            "descripcion": "Usar nombres claros, sin abreviaturas ni letras sueltas.",
            "ayuda_html": """<p>Buenas prácticas:</p>
<ul>
<li>Evitar nombres como <code>aux</code>, <code>tmp</code>, <code>i</code> (excepto en bucles cortos).</li>
<li>Usar verbos en funciones: <code>calcular_total()</code>, <code>obtener_usuario()</code>.</li>
<li>Variables descriptivas: <code>lista_usuarios</code> en lugar de <code>l</code>.</li>
</ul>
<p><strong>NOTA:</strong> Adjuntar captura de una parte del código donde se aplique.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 11,
            "nombre": "PASO 11: Task para API RouterOS y cerrar conexión. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Implementar tarea para consultar RouterOS, capturar excepciones y cerrar conexión.",
            "ayuda_html": """<p>Estructura recomendada:</p>
<pre>@shared_task(queue="trafico_mk", time_limit=180)
def get_trafico_task(slug_empresa, ...):
    connection = routeros.connect(...)
    try:
        # consultas
        return resultado
    except RouterOsApiConnectionError as e:
        # manejo
    except RouterOsApiCommunicationError as e:
        # manejo
    finally:
        connection.disconnect()</pre>
<p><strong>NOTA:</strong> Adjuntar captura del código del task.</p>""",
            "puntos": 15,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 12,
            "nombre": "PASO 12: Usar try-except correctamente. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Capturar excepciones específicas, no genéricas.",
            "ayuda_html": """<p>Ejemplo correcto:</p>
<pre>try:
    archivo = open('datos.txt')
except FileNotFoundError as e:
    print("Archivo no encontrado")</pre>
<p>Evitar:</p>
<pre>try:
    ...
except:
    pass</pre>
<p><strong>NOTA:</strong> Adjuntar captura de código donde se aplique.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 13,
            "nombre": "PASO 13: Timeouts y excepciones en APIs. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Agregar timeout a peticiones a APIs y capturar ConnectTimeout y ConnectionError.",
            "ayuda_html": """<p>Ejemplo con <code>requests</code>:</p>
<pre>try:
    response = requests.post(url, data=params, timeout=4)
except requests.ConnectTimeout:
    # manejo
except requests.exceptions.ConnectionError:
    # manejo</pre>
<p>En WispHub se puede usar <code>EXCEPCIONES_CONEXION_ENDPOINT</code>.</p>
<p><strong>NOTA:</strong> Adjuntar captura de código.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 14,
            "nombre": "PASO 14: Verificar TOOLTIP y botón AYUDA. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Agregar tooltips en elementos no intuitivos y completar el botón de ayuda con información.",
            "ayuda_html": """<p>Si el desarrollo añade nuevas funcionalidades que puedan resultar confusas, incluir tooltips (<code>title</code> o librería) y actualizar el contenido del botón de ayuda con una ventana modal que explique el paso.</p>
<p><strong>NOTA:</strong> Adjuntar captura del tooltip y del modal de ayuda.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 15,
            "nombre": "PASO 15: Mensajes claros en pasarelas de pago, SMS, facturación. (Programador) - (Evidencia con foto si aplica)",
            "descripcion": "Mostrar contacto de la pasarela ante errores externos.",
            "ayuda_html": """<p>Ejemplo de mensaje amigable:</p>
<blockquote>No se pudo procesar el pago en este momento. Por favor, contacta a soporte de la pasarela (teléfono: 800-123-4567) o intenta más tarde.</blockquote>
<p><strong>NOTA:</strong> Adjuntar captura del mensaje mostrado al usuario.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 16,
            "nombre": "PASO 16: Comparar código con Sublime Merge. (Programador) - (Evidencia)",
            "descripcion": "Revisar diferencias con la rama base usando una herramienta de diff.",
            "ayuda_html": """<p>Utilizar Sublime Merge, PyCharm Diff o <code>git diff</code> para asegurar que no se incluyen prints, código de prueba o cambios no deseados.</p>
<p><strong>NOTA:</strong> Adjuntar captura de la comparación mostrando solo los cambios relevantes.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 17,
            "nombre": "PASO 17: Ejecutar pruebas unitarias exitosas. (Programador) - (Evidencia con foto)",
            "descripcion": "Ejecutar `python manage.py test` y verificar que todas pasen.",
            "ayuda_html": """<p>Comando: <code>python manage.py test</code></p>
<p>Debe mostrar <code>OK</code> o <code>Ran X tests ... OK</code>.</p>
<p><strong>NOTA:</strong> Adjuntar captura del resultado.</p>""",
            "puntos": 15,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 18,
            "nombre": "PASO 18: Probar en local y servidor de pruebas. (Programador) - (Evidencia con foto)",
            "descripcion": "Probar el cambio en entorno local y en uno de los servidores de pruebas.",
            "ayuda_html": """<p>Servidores de pruebas disponibles:</p>
<ul>
<li><a href="https://nyc.wisphub.net/">https://nyc.wisphub.net/</a></li>
<li><a href="https://server4.wisphub.io/">https://server4.wisphub.io/</a></li>
</ul>
<p>Aplicar migraciones y collectstatic, verificar que no haya errores.</p>
<p><strong>NOTA:</strong> Adjuntar captura de la prueba funcionando en el servidor.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 19,
            "nombre": "PASO 19: Crear ticket para pruebas en local. (Scrum master) - (Evidencia con foto)",
            "descripcion": "Si el issue tiene entre 4 y 14 horas, probar con alguien de ventas; si >14h, con 2 de soporte y 2 de ventas.",
            "ayuda_html": """<p>Crear ticket en el sistema de seguimiento asignando el tiempo de prueba correspondiente (20min o 40min).</p>
<p><strong>NOTA:</strong> Adjuntar captura del ticket creado.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 20,
            "nombre": "PASO 20: Documentar antes de subir o en producción? (Programador)",
            "descripcion": "La documentación debe estar completa antes del despliegue a producción.",
            "ayuda_html": """<p>Documentar en el código (docstrings) y/o en la wiki interna para que el equipo de soporte pueda responder preguntas de clientes.</p>
<p><strong>NOTA:</strong> No requiere evidencia específica.</p>""",
            "puntos": 5,
            "evidencia_tipo": "ninguna"
        },
        {
            "orden": 21,
            "nombre": "PASO 21: Anotar workers a reiniciar. (Programador) - (Evidencia con foto)",
            "descripcion": "Identificar qué workers (Lote A, B o C) deben reiniciarse y notificarlo al líder.",
            "ayuda_html": """<p>Consultar el mapa de servidores:</p>
<ul>
<li><a href="https://wisphub.net/documentacion-staff/articulo/mapa-de-servidores-1-1/#lotea">Lote A</a></li>
<li><a href="https://wisphub.net/documentacion-staff/articulo/mapa-de-servidores-2-2/#loteb">Lote B</a></li>
<li><a href="https://wisphub.net/documentacion-staff/articulo/mapa-de-servidores-lote-3-210/">Lote C</a></li>
</ul>
<p><strong>NOTA:</strong> Adjuntar captura del comentario donde se especifica qué workers reiniciar.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 22,
            "nombre": "PASO 22: Anotar migraciones necesarias. (Programador) - (Evidencia con foto)",
            "descripcion": "Si se hicieron migraciones en modelos críticos, indicar tiempo estimado y mejor hora.",
            "ayuda_html": """<p>Ejemplo: "Migración en modelo Factura, tiempo estimado 5 minutos. Programar para las 7 AM o 8 PM."</p>
<p><strong>NOTA:</strong> Adjuntar captura del comentario.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 23,
            "nombre": "PASO 23: Anotar si se necesita collectstatic. (Programador) - (Evidencia con foto)",
            "descripcion": "Indicar si el cambio requiere ejecutar collectstatic.",
            "ayuda_html": """<p>Si se agregaron o modificaron archivos estáticos (CSS, JS, imágenes), es necesario correr <code>python manage.py collectstatic</code>. Notificarlo al líder.</p>
<p><strong>NOTA:</strong> Adjuntar captura del comentario.</p>""",
            "puntos": 5,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 24,
            "nombre": "PASO 24: Comparar código con líder de proyecto. (Líder y Programador)",
            "descripcion": "Revisión de código en pareja antes del push.",
            "ayuda_html": """<p>Utilizar herramienta de diff (Sublime Merge, PyCharm, VS Code) para comparar los cambios con la rama base. El líder debe aprobar visualmente.</p>
<p><strong>NOTA:</strong> Adjuntar captura de la revisión.</p>""",
            "puntos": 10,
            "evidencia_tipo": "fotografica"
        },
        {
            "orden": 25,
            "nombre": "PASO 25: Comprobar último cambio al hacer merge. (Programador) - (Evidencia con foto)",
            "descripcion": "Asegurar que la rama está actualizada antes del merge.",
            "ayuda_html": """<p>Ejecutar <code>git pull origin main</code> (o rama base) y resolver conflictos si los hay. Luego realizar el merge y adjuntar captura del merge exitoso.</p>
<p><strong>NOTA:</strong> Adjuntar captura del merge realizado.</p>""",
            "puntos": 5,
            "evidencia_tipo": "fotografica"
        }
    ]

    # 4. Crear los pasos
    for data in pasos_data:
        paso, created = Paso.objects.get_or_create(
            proceso=proceso,
            orden=data["orden"],
            defaults={
                "nombre": data["nombre"],
                "descripcion": data["descripcion"],
                "tipo": "normal",
                "puntos": data["puntos"],
                "ayuda_html": data["ayuda_html"],
                "evidencia_tipo": data["evidencia_tipo"],
                "nivel_critico": "media"
            }
        )
        if created:
            print(f"   ✅ Paso {data['orden']}: {data['nombre']}")
        else:
            print(f"   ⚠️ Paso {data['orden']} ya existía, no se modificó.")

    print(f"\n🎉 Proceso '{nombre_proceso}' creado exitosamente con {len(pasos_data)} pasos.")

# Ejecutar la función
crear_proceso_pros_des_09()