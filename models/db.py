# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL('postgres://SisPIO:SisPIO@localhost/SisPIO')
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.settings.table_user_name = 'usuario'

auth.define_tables(username = True, signature = False, migrate='db.usuario')

db.usuario.username.length = 8
db.usuario.password.requires = CRYPT()
db.usuario.username.requires = IS_MATCH('^([0-9]{1,8})?(admin)?$', error_message='Numero de Cedula Invalido.')

auth.settings.create_user_groups = None

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = 'proppio@usb.ve'
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

auth.settings.login_url = URL('index')
auth.settings.login_next = URL('redireccionando')

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
db.define_table(
    'liceo',
    Field('nombre', type='string', notnull=True),
    Field('tipo', type='string', notnull=True, requires=IS_IN_SET(['Publico', 'Subsidiado'])),
    Field('zona', type='string', notnull=True, requires=IS_IN_SET(['Sartenejas', 'Litoral', 'Higuerote', 'Guarenas'])),

    migrate='db.liceo'
    )


db.define_table(
    'cohorte',
    Field('identificador', type='string', requires=IS_MATCH('^[0-9]{4}/[0-9]{4}$', error_message='Formato de Cohorte Invalido.')),
    Field('activo', type='boolean', default=False),

    migrate='db.cohorte'
    )

db.define_table(
    'estudiante',
    Field('Nombre', type='string', notnull=True),
    Field('Apellido', type='string', notnull=True),
    Field('ci', type='string', length=8, notnull=True, unique=True, requires=[IS_IN_DB(db, db.usuario.username), IS_MATCH('^[0-9]{1,8}$', error_message='Numero de Cedula Invalido.')]),
    Field('promedio', type='double', notnull=True, requires=IS_FLOAT_IN_RANGE(minimum=0.01,maximum=20, error_message='Promedio no valido.')),
    Field('correo', type='string', length=128, required=True, default='', requires=IS_EMPTY_OR(IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'))),
    Field('direccion', type='text', default=''),
    Field('telefono_habitacion', type ='string', length=12, requires=IS_EMPTY_OR(IS_MATCH('^((0)?2[0-9]{2}(-)?)?[0-9]{7}$', error_message='Telefono Habitación Invalido.'))),
    Field('telefono_otro', type ='string', length=12, requires=IS_EMPTY_OR(IS_MATCH('^((0)?[0-9]{3}(-)?)?[0-9]{7}$', error_message='Telefono Invalido.'))),
    Field('fecha_nacimiento', type='date', requires=IS_EMPTY_OR(IS_DATE(format=T('%d/%m/%Y'), error_message='Debe ser del siguiente formato: dd/mm/yyyy'))),
    Field('sexo', type='string', default= 'Masculino', requires=IS_IN_SET(['Masculino', 'Femenino'])),
    Field('nombre_liceo', type='string', required=True, requires=IS_IN_DB(db, db.liceo.nombre)),
    Field('estatus', type='string', default='Pre-inscrito', requires=IS_IN_SET(['Pre-inscrito', 'Seleccionado', 'Activo', 'Inactivo', 'Finalizado'])),
    Field('cohorte', type='string', default='', requires=IS_IN_DB(db, db.cohorte.identificador)),

    Field('ci_representante', type='string', length=8, default='', requires=IS_EMPTY_OR(IS_MATCH('^[0-9]{1,8}$', error_message='Numero de Cedula Invalido.'))),
    Field('nombre_representante', type='string', default=''),
    Field('apellido_representante', type='string', default=''),
    Field('sexo_representante', type='string', default='Masculino', requires=IS_IN_SET(['Masculino', 'Femenino'])),
    Field('correo_representante', type='string', length=128, required=True, default='', requires=IS_EMPTY_OR(IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'))),
    Field('direccion_representante', type='text', default=''),
    Field('telefono_representante_oficina', type ='string', length=12, requires=IS_EMPTY_OR(IS_MATCH('^((0)?2[0-9]{2}(-)?)?[0-9]{7}$', error_message='Telefono Oficina Invalido.'))),
    Field('telefono_representante_otro', type ='string', length=12, requires=IS_EMPTY_OR(IS_MATCH('^((0)?[0-9]{3}(-)?)?[0-9]{7}$', error_message='Telefono Invalido.'))),

    Field('sufre_enfermedad', type='boolean', default=False),
    Field('enfermedad', type='string'),
    Field('indicaciones_enfermedad', type='text'),

    migrate="db.estudiante"
    )

db.define_table(
    'profesor',
    Field('Nombre', type='string', notnull=True),
    Field('Apellido', type='string', notnull=True),
    Field('ci', type='string', length=8, notnull=True, unique=True, requires=[IS_IN_DB(db, db.usuario.username), IS_MATCH('^[0-9]{1,8}$', error_message='Numero de Cedula Invalido.')]),
    Field('correo', type='string', length=128, required=True, default='', requires=IS_EMPTY_OR(IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'))),

    migrate="db.profesor"
    )

db.define_table(
    'representante_sede',
    Field('Nombre', type='string', notnull=True),
    Field('Apellido', type='string', notnull=True),
    Field('ci', type='string', length=8, notnull=True, unique=True, requires=[IS_IN_DB(db, db.usuario.username), IS_MATCH('^[0-9]{1,8}$', error_message='Numero de Cedula Invalido.')]),
    Field('correo', type='string', length=128, required=True, default='', requires=IS_EMPTY_OR(IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'))),
    Field('sede', type='string', requires=IS_IN_SET(['Sartenejas', 'Litoral', 'Higuerote', 'Guarenas'])),

    migrate="db.representante_sede"
    )

db.define_table(
    'representante_liceo',
    Field('Nombre', type='string'), #notnull=True
    Field('Apellido', type='string'),
    Field('ci', type='string', length=8, notnull=True, unique=True, requires=[IS_IN_DB(db, db.usuario.username), IS_MATCH('^[0-9]{1,8}$', error_message='Numero de Cedula Invalido.')]),
    Field('correo', type='string', length=128, required=True, default='', requires=IS_EMPTY_OR(IS_EMAIL(error_message='Debe tener un formato válido. EJ: example@org.com'))),
    Field('nombre_liceo', type='string', required=True, requires=IS_IN_DB(db, db.liceo.nombre)),

    migrate="db.representante_liceo"
    )

db.define_table(
    'materia',
    Field('nombre', type='string', notnull=True),
    Field('ci_profesor', type='string', requires=IS_IN_DB(db, db.profesor.ci)),

    migrate='db.materia'
    )

db.define_table(
    'cursa',
    Field('ci_estudiante', type='string', requires=IS_IN_DB(db, db.estudiante.ci)),
    Field('nombre_materia', type='string', requires=IS_IN_DB(db, db.materia.nombre)),
    Field('notas', type='list:integer'),

    migrate='db.cursa'
    )

db.define_table(
    'asistencia',
    Field('ci_estudiante', type='string', requires=IS_IN_DB(db, db.estudiante.ci)),
    Field('nombre_materia', type='string', requires=IS_IN_DB(db, db.materia.nombre)),
    Field('fecha_clase', type='date', requires=IS_DATE(format=T('%d/%m/%Y'), error_message='Debe ser del siguiente formato: dd/mm/yyyy')),

    migrate='db.asistencia'
    )

db.define_table(
    'carrera',
    Field('id', type='integer', unique=True, notnull=True),
    Field('nombre', type='string'),

    migrate='db.carrera'
    )

db.define_table(
    'exime',
    Field('ci_estudiante', type='string', length=8, notnull=True, requires=IS_IN_DB(db, db.estudiante.ci)),
    Field('ci_representante_liceo', type='string', length=8, notnull=True, requires=IS_IN_DB(db, db.representante_liceo.ci)),
    Field('cohorte', type='string', notnull=True, requires=IS_IN_DB(db, db.cohorte.identificador)),

    migrate='db.exime'
    )

db.define_table(
    'periodos',
    Field('nombre', type='string'),
    Field('fecha_inicio', type='date', requires=IS_DATE(format=T('%d/%m/%Y'), error_message='Debe ser del siguiente formato: dd/mm/yyyy')),
    Field('fecha_fin', type='date', requires=IS_DATE(format=T('%d/%m/%Y'), error_message='Debe ser del siguiente formato: dd/mm/yyyy')),

    migrate='db.periodos'
    )

db.define_table(
    'noticias',
    Field('titulo', type='string'),
    Field('contenido', type='text'),
    Field('fecha_publicacion', type='date', requires=IS_DATE(format=T('%d/%m/%Y'), error_message='Debe ser del siguiente formato: dd/mm/yyyy')),

    migrate='db.noticias'
    )




if not db(db.usuario.username == 'admin').select():
    id_usuario = db.usuario.insert(username='admin', password=CRYPT()('admin')[0], first_name='SisPIO', last_name='Admin', email='admin@usb.ve')

    estudiante = auth.add_group(role='Estudiante', description='description')
    profesor = auth.add_group(role='Profesor', description='description')
    representante_liceo = auth.add_group(role='Representante_liceo', description='description')
    representante_sede = auth.add_group(role='Representante_sede', description='description')
    admin = auth.add_group(role='Administrador', description='description')

    auth.add_permission(estudiante, 'Estudiante')

    auth.add_permission(profesor, 'Estudiante')
    auth.add_permission(profesor, 'Profesor')

    auth.add_permission(representante_liceo, 'Estudiante')
    auth.add_permission(representante_liceo, 'Representante_liceo')

    auth.add_permission(representante_sede, 'Estudiante')
    auth.add_permission(representante_sede, 'Representante_sede')

    auth.add_permission(admin, 'Estudiante')
    auth.add_permission(admin, 'Representante_liceo')
    auth.add_permission(admin, 'Profesor')
    auth.add_permission(admin, 'Representante_sede')
    auth.add_permission(admin, 'Administrador')

    auth.add_membership(admin, id_usuario)

    db.cohorte.insert(identificador='2017/2018',activo=True)
