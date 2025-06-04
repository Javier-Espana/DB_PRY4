# main.py (actualizado)
import streamlit as st
import pandas as pd
from db.connection import get_session
from services.crud_organization import (
    get_organizaciones, 
    get_organizacion,  # <-- Agrega esta importación
    create_organizacion,
    update_organizacion,
    delete_organizacion
)
import datetime

# CRUD Organización
def organizacion_crud():
    st.header("CRUD Organizaciones")
    db = get_session()
    
    # Operaciones CRUD
    tab1, tab2, tab3 = st.tabs(["Ver", "Crear", "Editar/Eliminar"])
    
    with tab1:
        orgs = get_organizaciones(db)
        st.table([{
            "ID": o.organizacion_id,
            "Nombre": o.nombre,
            "Email": o.email,
            "Activa": "✅" if o.activa else "❌"
        } for o in orgs])
    
    with tab2:
        with st.form("crear_org"):
            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            activa = st.checkbox("Activa", value=True)
            if st.form_submit_button("Crear"):
                try:
                    org = create_organizacion(db, {
                        "nombre": nombre,
                        "email": email,
                        "activa": activa
                    })
                    st.success(f"Organización {org.nombre} creada!")
                except ValueError as ve:
                    st.error(f"Error al crear organización: {str(ve)}")
                except Exception as e:
                    st.error(f"Error al crear organización: {str(e)}")
                    db.rollback()
    
    with tab3:
        org_id = st.number_input("ID Organización", min_value=1, key="edit_org_id")
        if org_id:
            org = get_organizacion(db, org_id)
            if org:
                with st.form("editar_org"):
                    nombre = st.text_input("Nombre", value=org.nombre, key="edit_org_nombre")
                    email = st.text_input("Email", value=org.email, key="edit_org_email")
                    activa = st.checkbox("Activa", value=org.activa, key="edit_org_activa")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            update_organizacion(db, org_id, {
                                "nombre": nombre,
                                "email": email,
                                "activa": activa
                            })
                            st.success("Organización actualizada!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_organizacion(db, org_id):
                                st.success("Organización eliminada!")
                            else:
                                st.error("Error al eliminar")
                        except Exception as e:
                            st.error(f"Error: {e}")

def resumen_donaciones_por_campana():
    from services.reports import get_donaciones_por_campana
    from components.ui_elements import render_table, render_filters
    from db.connection import get_session
    from services.crud_donacion import get_donaciones, create_donacion, update_donacion, delete_donacion
    from services.crud_campana import get_campanas, create_campana, update_campana, delete_campana, get_campana
    st.header("Resumen de Donaciones por Campaña")

    # Filtros
    today = datetime.date.today()
    filters = {
        "fecha_inicio_campana": {"type": "date", "label": "Fecha inicio", "value": today.replace(day=1).replace(year=today.year - 3)},
        "fecha_fin_campana": {"type": "date", "label": "Fecha fin", "value": today.replace(month=today.month + 1)},
        "monto_minimo_campana": {"type": "number", "label": "Monto mínimo", "value": 0, "min": 0},
        "monto_maximo_campana": {"type": "number", "label": "Monto máximo", "value": 10000, "min": 0},
    }
    render_filters(filters)
    fecha_inicio = st.session_state.get("fecha_inicio_campana")
    fecha_fin = st.session_state.get("fecha_fin_campana")
    monto_minimo = st.session_state.get("monto_minimo_campana")
    monto_maximo = st.session_state.get("monto_maximo_campana")

    db = get_session()
    # Consultar datos
    data = get_donaciones_por_campana(
        db,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        monto_minimo=monto_minimo,
        monto_maximo=monto_maximo
    )
    render_table("Donaciones por Campaña", data)

    st.subheader("CRUD Donaciones")
    tab1, tab2, tab3 = st.tabs(["Ver Donaciones", "Crear Donación", "Editar/Eliminar Donación"])
    with tab1:
        donaciones = get_donaciones(db)
        df = pd.DataFrame([
            {
                k: getattr(d, k).value if hasattr(getattr(d, k), "value") else getattr(d, k)
                for k in d.__table__.columns.keys()
            }
            for d in donaciones
        ])
        st.dataframe(df, height=400)
    with tab2:
        # Importar create_donante de forma segura para usarlo más adelante
        try:
            from services.crud_donante import create_donante
        except ImportError:
            create_donante = None
        # Obtener campañas existentes para sugerencias
        campanas_existentes = get_campanas(db)
        campana_options = [
            (f"{c.campana_id} - {c.nombre}", c.campana_id) for c in campanas_existentes
        ]
        campana_labels = [label for label, _ in campana_options]
        campana_ids = [cid for _, cid in campana_options]

        # Obtener donantes existentes para sugerencias
        try:
            from services.crud_donante import get_donantes
            donantes_existentes = get_donantes(db)
            donante_options = [
                (f"{d.donante_id} - {getattr(d, 'nombre', str(d.donante_id))}", d.donante_id) for d in donantes_existentes
            ]
            donante_labels = [label for label, _ in donante_options]
            donante_ids = [did for _, did in donante_options]
        except ImportError:
            donante_labels = []
            donante_ids = []
        with st.form("crear_donacion"):
            campana_idx = st.selectbox(
                "Campaña ID",
                options=range(len(campana_ids)),
                format_func=lambda i: campana_labels[i] if i < len(campana_labels) else "",
                key="donacion_campana_id"
            ) if campana_ids else None
            campana_id = campana_ids[campana_idx] if campana_idx is not None else None

            donante_mode = st.radio("¿Donante existente o nuevo?", ["Existente", "Nuevo"], key="donacion_donante_mode")
            donante_id = None
            if donante_mode == "Existente":
                if donante_ids:
                    donante_idx = st.selectbox(
                        "Donante ID",
                        options=range(len(donante_ids)),
                        format_func=lambda i: donante_labels[i] if i < len(donante_labels) else "",
                        key="donacion_donante_id"
                    )
                    donante_id = donante_ids[donante_idx]
                else:
                    st.info("No hay donantes registrados. Por favor, agregue un nuevo donante.")
            else:
                nombre = st.text_input("Nombre Donante", key="nuevo_donante_nombre")
                apellido = st.text_input("Apellido Donante", key="nuevo_donante_apellido")
                email = st.text_input("Email Donante", key="nuevo_donante_email")
                tipo_donante = st.selectbox("Tipo Donante", ["individual", "empresa"], key="nuevo_donante_tipo")
                # donante_id se asignará tras crear el donante

            tipo = st.selectbox("Tipo", ["monetaria", "especie"])
            monto = st.number_input("Monto", min_value=0.0, step=0.01, key="donacion_monto") if tipo == "monetaria" else None
            descripcion_especie = st.text_input("Descripción Especie", key="donacion_desc_especie") if tipo == "especie" else None
            fecha = st.date_input("Fecha", value=today, key="donacion_fecha")
            if st.form_submit_button("Crear"):
                try:
                    if donante_mode == "Existente":
                        if not donante_ids:
                            st.error("Debe agregar un donante primero.")
                            raise Exception("No hay donantes existentes")
                        if donante_id is None:
                            st.error("Debe seleccionar un donante válido.")
                            raise Exception("Donante no seleccionado")
                    else:
                        if not nombre or not apellido or not email:
                            st.error("Debe completar los datos del nuevo donante.")
                            raise Exception("Datos de donante incompletos")
                        if create_donante is None:
                            st.error("La función para crear donantes no está disponible.")
                            raise Exception("create_donante no importado")
                        nuevo_donante = create_donante(db, {
                            "nombre": nombre,
                            "apellido": apellido,
                            "email": email,
                            "tipo": tipo_donante
                        })
                        donante_id = nuevo_donante.donante_id

                    if tipo == "monetaria" and (monto is None or monto <= 0):
                        st.error("No se ingresó monto")
                    else:
                        data = {
                            "campana_id": campana_id,
                            "donante_id": donante_id,
                            "tipo": tipo,
                            "monto": monto if tipo == "monetaria" else None,
                            "descripcion_especie": descripcion_especie if tipo == "especie" else None,
                            "fecha": fecha
                        }
                        create_donacion(db, data)
                        st.success("Donación creada!")
                except ValueError as ve:
                    st.error(f"Error al crear donación: {str(ve)}")
                except Exception as e:
                    st.error(f"Error al crear donación: {str(e)}")
                    db.rollback()
    with tab3:
        donacion_id = st.number_input("ID Donación", min_value=1, key="edit_donacion_id")
        if donacion_id:
            from services.crud_donacion import get_donacion
            donacion = get_donacion(db, donacion_id)
            if donacion:
                with st.form("editar_donacion"):
                    campana_id = st.number_input("Campaña ID", min_value=1, value=donacion.campana_id, key="edit_donacion_campana_id")
                    donante_id = st.number_input("Donante ID", min_value=1, value=donacion.donante_id, key="edit_donacion_donante_id")
                    tipo = st.selectbox("Tipo", ["monetaria", "especie"], index=0 if donacion.tipo == "monetaria" else 1, key="edit_donacion_tipo")
                    monto = st.number_input("Monto", min_value=0.0, step=0.01, value=float(donacion.monto) if donacion.monto else 0.0, key="edit_donacion_monto") if tipo == "monetaria" else None
                    descripcion_especie = st.text_input("Descripción Especie", value=donacion.descripcion_especie or "", key="edit_donacion_desc_especie") if tipo == "especie" else None
                    fecha = st.date_input("Fecha", value=donacion.fecha.date() if donacion.fecha else today, key="edit_donacion_fecha")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {
                                "campana_id": campana_id,
                                "donante_id": donante_id,
                                "tipo": tipo,
                                "monto": monto if tipo == "monetaria" else None,
                                "descripcion_especie": descripcion_especie if tipo == "especie" else None,
                                "fecha": fecha
                            }
                            update_donacion(db, donacion_id, data)
                            st.success("Donación actualizada!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_donacion(db, donacion_id):
                                st.success("Donación eliminada!")
                            else:
                                st.error("Error al eliminar")
                        except Exception as e:
                            st.error(f"Error: {e}")
    # CRUD Campañas (opcional, similar a donaciones)
    st.subheader("CRUD Campañas")
    tabc1, tabc2, tabc3 = st.tabs(["Ver Campañas", "Crear Campaña", "Editar/Eliminar Campaña"])
    with tabc1:
        campanas = get_campanas(db)
        df = pd.DataFrame([
            {
                k: getattr(c, k).value if hasattr(getattr(c, k), "value") else getattr(c, k)
                for k in c.__table__.columns.keys()
            }
            for c in campanas
        ])
        st.dataframe(df, height=400)
    with tabc2:
        # Obtener organizaciones existentes para sugerencias
        organizaciones_existentes = get_organizaciones(db)
        org_options = [
            (f"{o.organizacion_id} - {o.nombre}", o.organizacion_id) for o in organizaciones_existentes
        ]
        org_labels = [label for label, _ in org_options]
        org_ids = [oid for _, oid in org_options]

        # Obtener categorías existentes para sugerencias
        try:
            from services.crud_categoria import get_categorias
            categorias_existentes = get_categorias(db)
            cat_options = [
                (f"{c.categoria_id} - {getattr(c, 'nombre', str(c.categoria_id))}", c.categoria_id) for c in categorias_existentes
            ]
            cat_labels = [label for label, _ in cat_options]
            cat_ids = [cid for _, cid in cat_options]
        except ImportError:
            cat_labels = []
            cat_ids = []

        # Obtener sedes existentes para sugerencias
        try:
            from services.crud_sede import get_sedes
            sedes_existentes = get_sedes(db)
            sede_options = [
                (f"{s.sede_id} - {getattr(s, 'nombre', str(s.sede_id))}", s.sede_id) for s in sedes_existentes
            ]
            sede_labels = [label for label, _ in sede_options]
            sede_ids = [sid for _, sid in sede_options]
        except ImportError:
            sede_labels = []
            sede_ids = []

        with st.form("crear_campana"):
            nombre = st.text_input("Nombre", key="crear_campana_nombre")
            descripcion = st.text_area("Descripción", key="crear_campana_desc")
            fecha_inicio = st.date_input("Fecha inicio", value=today, key="crear_campana_fecha_inicio")
            fecha_fin = st.date_input("Fecha fin", value=today, key="crear_campana_fecha_fin")
            meta_monetaria = st.number_input("Meta monetaria", min_value=0.0, step=0.01, key="crear_campana_meta")
            estado = st.selectbox("Estado", ["planificada", "activa", "pausada", "finalizada"], key="crear_campana_estado")
            # Usar selectbox para sugerir organizaciones válidas
            org_idx = st.selectbox(
                "Organización ID",
                options=range(len(org_ids)),
                format_func=lambda i: org_labels[i] if i < len(org_labels) else "",
                key="crear_campana_org_id"
            ) if org_ids else None
            organizacion_id = org_ids[org_idx] if org_idx is not None else None

            # Usar selectbox para sugerir categorías válidas solo si hay categorías
            cat_idx = st.selectbox(
                "Categoría ID",
                options=range(len(cat_ids)),
                format_func=lambda i: cat_labels[i] if i < len(cat_labels) else "",
                key="crear_campana_cat_id"
            ) if cat_ids else None
            categoria_id = cat_ids[cat_idx] if cat_idx is not None else None

            # Usar selectbox para sugerir sedes válidas
            sede_idx = st.selectbox(
                "Sede Principal ID",
                options=range(len(sede_ids)),
                format_func=lambda i: sede_labels[i] if i < len(sede_labels) else "",
                key="crear_campana_sede_id"
            ) if sede_ids else None
            sede_principal_id = sede_ids[sede_idx] if sede_idx is not None else None
            if st.form_submit_button("Crear"):
                try:
                    if organizacion_id is None:
                        st.error("Debe seleccionar una organización válida.")
                    elif not cat_ids or categoria_id is None:
                        st.error("Debe seleccionar una categoría válida.")
                    elif not sede_ids or sede_principal_id is None:
                        st.error("Debe seleccionar una sede válida.")
                    else:
                        data = {
                            "nombre": nombre,
                            "descripcion": descripcion,
                            "fecha_inicio": fecha_inicio,
                            "fecha_fin": fecha_fin,
                            "meta_monetaria": meta_monetaria,
                            "estado": estado,
                            "organizacion_id": organizacion_id,
                            "categoria_id": categoria_id,
                            "sede_principal_id": sede_principal_id
                        }
                        create_campana(db, data)
                        st.success("Campaña creada!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with tabc3:
        campana_id = st.number_input("ID Campaña", min_value=1, key="resumen_edit_campana_id")
        if campana_id:
            campana = get_campana(db, campana_id)
            if campana:
                with st.form("editar_campana"):
                    nombre = st.text_input("Nombre", value=campana.nombre, key="edit_campana_nombre")
                    descripcion = st.text_area("Descripción", value=campana.descripcion or "", key="edit_campana_desc")
                    fecha_inicio = st.date_input("Fecha inicio", value=campana.fecha_inicio or today, key="edit_campana_fecha_inicio")
                    fecha_fin = st.date_input("Fecha fin", value=campana.fecha_fin or today, key="edit_campana_fecha_fin")
                    meta_monetaria = st.number_input("Meta monetaria", min_value=0.0, step=0.01, value=float(campana.meta_monetaria) if campana.meta_monetaria else 0.0, key="edit_campana_meta")
                    estado_list = ["planificada", "activa", "pausada", "finalizada"]
                    estado_value = campana.estado.value if hasattr(campana.estado, 'value') else str(campana.estado) if campana.estado else None
                    estado = st.selectbox("Estado", estado_list, index=estado_list.index(estado_value) if estado_value in estado_list else 0)
                    organizacion_id = st.number_input("Organización ID", min_value=1, value=campana.organizacion_id, key="edit_campana_org_id")
                    categoria_id = st.number_input("Categoría ID", min_value=1, value=campana.categoria_id, key="edit_campana_cat_id")
                    sede_principal_id = st.number_input("Sede Principal ID", min_value=1, value=campana.sede_principal_id, key="edit_campana_sede_id")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {
                                "nombre": nombre,
                                "descripcion": descripcion,
                                "fecha_inicio": fecha_inicio,
                                "fecha_fin": fecha_fin,
                                "meta_monetaria": meta_monetaria,
                                "estado": estado,
                                "organizacion_id": organizacion_id,
                                "categoria_id": categoria_id,
                                "sede_principal_id": sede_principal_id
                            }
                            update_campana(db, campana_id, data)
                            st.success("Campaña actualizada!")
                        except ValueError as ve:
                            st.error(f"Error: {str(ve)}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_campana(db, campana_id):
                                st.success("Campaña eliminada!")
                            else:
                                st.error("No se encontró la campaña para eliminar.")
                        except ValueError as ve:
                            st.error(f"Error al eliminar campaña: {str(ve)}")
                        except Exception as e:
                            st.error(f"Error inesperado: {str(e)}")
def participacion_voluntarios_por_actividad():
    from components.ui_elements import render_table, render_filters
    from db.connection import get_session
    from services.crud_voluntario_actividad import (
        get_voluntario_actividades, create_voluntario_actividad, update_voluntario_actividad, delete_voluntario_actividad, get_voluntario_actividad
    )
    st.header("Participación de Voluntarios por Actividad")

    # Filtros con keys únicos para este segmento
    today = datetime.date.today()
    filters = {
        "fecha_inicio_voluntarios": {"type": "date", "label": "Fecha inicio", "value": today.replace(day=1).replace(year=today.year - 3).replace(year=today.year - 3)},
        "fecha_fin_voluntarios": {"type": "date", "label": "Fecha fin", "value": today.replace(month=today.month + 1)},
        "edad_minima_voluntarios": {"type": "number", "label": "Edad mínima", "value": 16, "min": 0},
        "edad_maxima_voluntarios": {"type": "number", "label": "Edad máxima", "value": 99, "min": 0},
    }
    render_filters(filters)
    fecha_inicio = st.session_state.get("fecha_inicio_voluntarios")
    fecha_fin = st.session_state.get("fecha_fin_voluntarios")
    edad_minima = int(st.session_state.get("edad_minima_voluntarios") or 0)
    edad_maxima = int(st.session_state.get("edad_maxima_voluntarios") or 99)

    # Reporte (requiere función get_voluntarios_por_actividad en services.reports)
    try:
        from services.reports import get_voluntarios_por_actividad
        db = get_session()
        data = get_voluntarios_por_actividad(
            db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            edad_minima=edad_minima,
            edad_maxima=edad_maxima
        )
    except Exception:
        data = []
    render_table("Voluntarios por Actividad", data)

    st.subheader("CRUD Participación Voluntario-Actividad")
    db = get_session()
    tab1, tab2, tab3 = st.tabs(["Ver Participaciones", "Crear Participación", "Editar/Eliminar Participación"])
    with tab1:
        participaciones = get_voluntario_actividades(db)
        df = pd.DataFrame([{k: getattr(v, k) for k in v.__table__.columns.keys()} for v in participaciones])
        st.dataframe(df, height=400)
    with tab2:
        with st.form("crear_va"):
            voluntario_id = st.number_input("Voluntario ID", min_value=1, key="va_voluntario_id")
            actividad_id = st.number_input("Actividad ID", min_value=1, key="va_actividad_id")
            horas_dedicadas = st.number_input("Horas dedicadas", min_value=0.0, step=0.5, key="va_horas")
            comentarios = st.text_area("Comentarios", key="va_comentarios")
            estado = st.selectbox("Estado", ["pendiente", "aprobado", "rechazado"], key="va_estado")
            if st.form_submit_button("Crear"):
                try:
                    data = {
                        "voluntario_id": voluntario_id,
                        "actividad_id": actividad_id,
                        "horas_dedicadas": horas_dedicadas,
                        "comentarios": comentarios,
                        "estado": estado
                    }
                    create_voluntario_actividad(db, data)
                    st.success("Participación creada!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with tab3:
        voluntario_id = st.number_input("Voluntario ID (editar/eliminar)", min_value=1, key="va_edit_vol")
        actividad_id = st.number_input("Actividad ID (editar/eliminar)", min_value=1, key="va_edit_act")
        va = get_voluntario_actividad(db, voluntario_id, actividad_id)
        if va:
            with st.form("editar_va"):
                horas_dedicadas = st.number_input("Horas dedicadas", min_value=0.0, step=0.5, value=float(va.horas_dedicadas) if va.horas_dedicadas else 0.0, key="va_edit_horas")
                comentarios = st.text_area("Comentarios", value=va.comentarios or "", key="va_edit_comentarios")
                estado = st.selectbox("Estado", ["pendiente", "aprobado", "rechazado"], index=["pendiente", "aprobado", "rechazado"].index(va.estado) if va.estado else 0, key="va_edit_estado")
                submitted_update = st.form_submit_button("Actualizar")
                submitted_delete = st.form_submit_button("Eliminar")
                if submitted_update:
                    try:
                        data = {
                            "horas_dedicadas": horas_dedicadas,
                            "comentarios": comentarios,
                            "estado": estado
                        }
                        update_voluntario_actividad(db, voluntario_id, actividad_id, data)
                        st.success("Participación actualizada!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                if submitted_delete:
                    try:
                        if delete_voluntario_actividad(db, voluntario_id, actividad_id):
                            st.success("Participación eliminada!")
                        else:
                            st.error("Error al eliminar")
                    except Exception as e:
                        st.error(f"Error: {e}")
    # CRUD Actividad (opcional, similar a campañas)
    # ...Puedes agregar aquí CRUD para Actividad si lo deseas...

def donaciones_por_donante():
    import datetime
    import streamlit as st
    from components.ui_elements import render_table, render_filters
    from db.connection import get_session
    from services.crud_donacion import get_donaciones, create_donacion, update_donacion, delete_donacion, get_donacion
    # Se asume que existe un CRUD de donante similar
    try:
        from services.crud_donante import get_donantes, create_donante, update_donante, delete_donante, get_donante
        donante_crud = True
    except ImportError:
        donante_crud = False
    st.header("Donaciones por Donante")

    # Filtros
    today = datetime.date.today()
    filters = {
        "fecha_inicio_donante": {"type": "date", "label": "Fecha inicio", "value": today.replace(day=1).replace(year=today.year - 3)},
        "fecha_fin_donante": {"type": "date", "label": "Fecha fin", "value": today.replace(month=today.month + 1)},
        "monto_minimo_donante": {"type": "number", "label": "Monto mínimo", "value": 0, "min": 0},
        "monto_maximo_donante": {"type": "number", "label": "Monto máximo", "value": 10000, "min": 0},
    }
    render_filters(filters)
    fecha_inicio = st.session_state.get("fecha_inicio_donante")
    fecha_fin = st.session_state.get("fecha_fin_donante")
    monto_minimo = st.session_state.get("monto_minimo_donante")
    monto_maximo = st.session_state.get("monto_maximo_donante")

    # Reporte (requiere función get_donaciones_por_donante en services.reports)
    try:
        from services.reports import get_donaciones_por_donante
        db = get_session()
        data = get_donaciones_por_donante(
            db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            monto_minimo=monto_minimo,
            monto_maximo=monto_maximo
        )
    except Exception:
        data = []
    render_table("Donaciones por Donante", data)

    st.subheader("CRUD Donaciones")
    db = get_session()
    tab1, tab2, tab3 = st.tabs(["Ver Donaciones", "Crear Donación", "Editar/Eliminar Donación"])
    with tab1:
        donaciones = get_donaciones(db)
        df = pd.DataFrame([
            {
                k: getattr(d, k).value if hasattr(getattr(d, k), "value") else getattr(d, k)
                for k in d.__table__.columns.keys()
            }
            for d in donaciones
        ])
        st.dataframe(df, height=400)
    with tab2:
        with st.form("crear_donacion_donante"):
            donante_id = st.number_input("Donante ID", min_value=1, key="donante_donante_id")
            campana_id = st.number_input("Campaña ID", min_value=1, key="donante_campana_id")
            tipo = st.selectbox("Tipo", ["monetaria", "especie"], key="donante_tipo")
            monto = st.number_input("Monto", min_value=0.0, step=0.01, key="donante_monto") if tipo == "monetaria" else None
            descripcion_especie = st.text_input("Descripción Especie", key="donante_desc_especie") if tipo == "especie" else None
            fecha = st.date_input("Fecha", value=today, key="donante_fecha")
            if st.form_submit_button("Crear"):
                try:
                    data = {
                        "donante_id": donante_id,
                        "campana_id": campana_id,
                        "tipo": tipo,
                        "monto": monto if tipo == "monetaria" else None,
                        "descripcion_especie": descripcion_especie if tipo == "especie" else None,
                        "fecha": fecha
                    }
                    create_donacion(db, data)
                    st.success("Donación creada!")
                except Exception as e:
                    st.error(f"Error: {e}")
    with tab3:
        donacion_id = st.number_input("ID Donación", min_value=1, key="edit_donacion_donante")
        if donacion_id:
            donacion = get_donacion(db, donacion_id)
            if donacion:
                with st.form("editar_donacion_donante"):
                    donante_id = st.number_input("Donante ID", min_value=1, value=donacion.donante_id, key="edit_donante_donante_id")
                    campana_id = st.number_input("Campaña ID", min_value=1, value=donacion.campana_id, key="edit_donante_campana_id")
                    tipo = st.selectbox("Tipo", ["monetaria", "especie"], index=0 if donacion.tipo == "monetaria" else 1, key="edit_donante_tipo")
                    monto = st.number_input("Monto", min_value=0.0, step=0.01, value=float(donacion.monto) if donacion.monto else 0.0, key="edit_donante_monto") if tipo == "monetaria" else None
                    descripcion_especie = st.text_input("Descripción Especie", value=donacion.descripcion_especie or "", key="edit_donante_desc_especie") if tipo == "especie" else None
                    fecha = st.date_input("Fecha", value=donacion.fecha.date() if donacion.fecha else today, key="edit_donante_fecha")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {
                                "donante_id": donante_id,
                                "campana_id": campana_id,
                                "tipo": tipo,
                                "monto": monto if tipo == "monetaria" else None,
                                "descripcion_especie": descripcion_especie if tipo == "especie" else None,
                                "fecha": fecha
                            }
                            update_donacion(db, donacion_id, data)
                            st.success("Donación actualizada!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_donacion(db, donacion_id):
                                st.success("Donación eliminada!")
                            else:
                                st.error("Error al eliminar")
                        except Exception as e:
                            st.error(f"Error: {e}")
    # CRUD Donantes (opcional, si existe CRUD de donante)
    if donante_crud:
        st.subheader("CRUD Donantes")
        tabd1, tabd2, tabd3 = st.tabs(["Ver Donantes", "Crear Donante", "Editar/Eliminar Donante"])
        with tabd1:
            donantes = get_donantes(db)
            df = pd.DataFrame([
                {
                    k: getattr(d, k).value if hasattr(getattr(d, k), "value") else getattr(d, k)
                    for k in d.__table__.columns.keys()
                }
                for d in donantes
            ])
            st.dataframe(df, height=400)
        with tabd2:
            with st.form("crear_donante"):
                nombre = st.text_input("Nombre", key="crear_donante_nombre")
                apellido = st.text_input("Apellido", key="crear_donante_apellido")
                email = st.text_input("Email", key="crear_donante_email")
                tipo = st.selectbox("Tipo", ["individual", "empresa"], key="crear_donante_tipo")
                if st.form_submit_button("Crear"):
                    try:
                        data = {"nombre": nombre, "apellido": apellido, "email": email, "tipo": tipo}
                        create_donante(db, data)
                        st.success("Donante creado!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tabd3:
            donante_id = st.number_input("ID Donante", min_value=1, key="edit_donante_id")
            donante = get_donante(db, donante_id)
            if donante:
                with st.form("editar_donante"):
                    nombre = st.text_input("Nombre", value=donante.nombre, key="edit_donante_nombre")
                    apellido = st.text_input("Apellido", value=donante.apellido, key="edit_donante_apellido")
                    email = st.text_input("Email", value=donante.email, key="edit_donante_email")
                    tipo = st.selectbox("Tipo", ["individual", "empresa"], index=0 if donante.tipo == "individual" else 1, key="edit_donante_tipo")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {"nombre": nombre, "apellido": apellido, "email": email, "tipo": tipo}
                            update_donante(db, donante_id, data)
                            st.success("Donante actualizado!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_donante(db, donante_id):
                                st.success("Donante eliminado!")
                            else:
                                st.error("Error al eliminar")
                        except Exception as e:
                            st.error(f"Error: {e}")

def distribucion_voluntarios_por_edad():
    import datetime
    import streamlit as st
    import pandas as pd
    from components.ui_elements import render_table, render_filters
    from db.connection import get_session
    try:
        from services.reports import get_distribucion_voluntarios_por_edad
    except ImportError:
        get_distribucion_voluntarios_por_edad = None
    try:
        from services.crud_voluntario import get_voluntarios, create_voluntario, update_voluntario, delete_voluntario, get_voluntario
        voluntario_crud = True
    except ImportError:
        voluntario_crud = False
    st.header("Distribución de Voluntarios por Edad")

    # Filtros
    today = datetime.date.today()
    filters = {
        "fecha_inicio_edad": {"type": "date", "label": "Fecha inicio", "value": today.replace(day=1).replace(year=today.year - 3)},
        "fecha_fin_edad": {"type": "date", "label": "Fecha fin", "value": today.replace(month=today.month + 1)},
        "genero_edad": {"type": "select", "label": "Género", "options": ["Todos", "M", "F"]},
        "actividad_id_edad": {"type": "number", "label": "ID Actividad", "value": 1, "min": 1},
    }
    render_filters(filters)
    fecha_inicio = st.session_state.get("fecha_inicio_edad")
    fecha_fin = st.session_state.get("fecha_fin_edad")
    genero = st.session_state.get("genero_edad")
    actividad_id = st.session_state.get("actividad_id_edad")
    if genero == "Todos":
        genero = None

    # Reporte (requiere función get_distribucion_voluntarios_por_edad en services.reports)
    if get_distribucion_voluntarios_por_edad:
        try:
            db = get_session()
            data = get_distribucion_voluntarios_por_edad(
                db,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                genero=genero,
                actividad_id=actividad_id
            )
        except Exception:
            data = []
    else:
        data = []
    render_table("Distribución por Edad", data)

    # Gráfica
    if data:
        import plotly.express as px
        df = pd.DataFrame(data)
        if 'grupo_edad' in df.columns and 'total_voluntarios' in df.columns:
            fig = px.bar(df, x='grupo_edad', y='total_voluntarios', title='Distribución de Voluntarios por Edad', labels={'grupo_edad': 'Grupo de Edad', 'total_voluntarios': 'Total Voluntarios'})
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("CRUD Voluntarios")
    db = get_session()
    if voluntario_crud:
        tab1, tab2, tab3 = st.tabs(["Ver Voluntarios", "Crear Voluntario", "Editar/Eliminar Voluntario"])
        with tab1:
            voluntarios = get_voluntarios(db)
            df = pd.DataFrame([
                {
                    k: getattr(v, k).value if hasattr(getattr(v, k), "value") else getattr(v, k)
                    for k in v.__table__.columns.keys()
                }
                for v in voluntarios
            ])
            st.dataframe(df, height=400)
        with tab2:
            with st.form("crear_voluntario"):
                nombre = st.text_input("Nombre", key="crear_voluntario_nombre")
                apellido = st.text_input("Apellido", key="crear_voluntario_apellido")
                email = st.text_input("Email", key="crear_voluntario_email")
                fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=today.replace(year=today.year-20), key="crear_voluntario_fecha_nac")
                if st.form_submit_button("Crear"):
                    try:
                        data = {"nombre": nombre, "apellido": apellido, "email": email, "fecha_nacimiento": fecha_nacimiento}
                        create_voluntario(db, data)
                        st.success("Voluntario creado!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab3:
            voluntario_id = st.number_input("ID Voluntario", min_value=1, key="edit_voluntario_id")
            voluntario = get_voluntario(db, voluntario_id)
            if voluntario:
                with st.form("editar_voluntario"):
                    nombre = st.text_input("Nombre", value=voluntario.nombre, key="edit_voluntario_nombre")
                    apellido = st.text_input("Apellido", value=voluntario.apellido, key="edit_voluntario_apellido")
                    email = st.text_input("Email", value=voluntario.email, key="edit_voluntario_email")
                    fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=voluntario.fecha_nacimiento, key="edit_voluntario_fecha_nac")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {"nombre": nombre, "apellido": apellido, "email": email, "fecha_nacimiento": fecha_nacimiento}
                            update_voluntario(db, voluntario_id, data)
                            st.success("Voluntario actualizado!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_voluntario(db, voluntario_id):
                                st.success("Voluntario eliminado!")
                            else:
                                st.error("Error al eliminar")
                        except Exception as e:
                            st.error(f"Error: {e}")
def efectividad_campanas():
    import datetime
    import streamlit as st
    import pandas as pd
    from components.ui_elements import render_table, render_filters
    from db.connection import get_session
    try:
        from services.reports import get_efectividad_campanas
    except ImportError:
        get_efectividad_campanas = None
    try:
        from services.crud_campana import get_campanas, create_campana, update_campana, delete_campana, get_campana
        campana_crud = True
    except ImportError:
        campana_crud = False
    st.header("Efectividad de Campañas")

    # Filtros
    today = datetime.date.today()
    filters = {
        "fecha_inicio_efectividad": {"type": "date", "label": "Fecha inicio", "value": today.replace(day=1).replace(year=today.year - 3)},
        "fecha_fin_efectividad": {"type": "date", "label": "Fecha fin", "value": today.replace(month=today.month + 1).replace(month=today.month + 1)},
        "estado_efectividad": {"type": "select", "label": "Estado", "options": ["Todos", "planificada", "activa", "pausada", "finalizada"]},
    }
    render_filters(filters)
    fecha_inicio = st.session_state.get("fecha_inicio_efectividad")
    fecha_fin = st.session_state.get("fecha_fin_efectividad")
    estado = st.session_state.get("estado_efectividad")
    if estado == "Todos":
        estado = None

    # Reporte (requiere función get_efectividad_campanas en services.reports)
    if get_efectividad_campanas:
        try:
            db = get_session()
            data = get_efectividad_campanas(
                db,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado
            )
        except Exception:
            data = []
    else:
        data = []
    render_table("Efectividad de Campañas", data)

    # Gráfica 1: Campañas más efectivas (por porcentaje de cumplimiento)
    if data:
        import pandas as pd
        import plotly.express as px
        df = pd.DataFrame(data)
        if 'nombre' in df.columns and 'porcentaje_cumplimiento' in df.columns:
            top = df.sort_values('porcentaje_cumplimiento', ascending=False).head(10)
            fig1 = px.bar(top, x='nombre', y='porcentaje_cumplimiento', title='Campañas más efectivas', labels={'nombre': 'Campaña', 'porcentaje_cumplimiento': 'Porcentaje Cumplimiento'})
            st.plotly_chart(fig1, use_container_width=True)
        # Gráfica 2: Recaudación por campaña
        if 'nombre' in df.columns and 'monto_recaudado' in df.columns:
            fig2 = px.bar(df, x='nombre', y='monto_recaudado', title='Recaudación por Campaña', labels={'nombre': 'Campaña', 'monto_recaudado': 'Monto Recaudado'})
            st.plotly_chart(fig2, use_container_width=True)

    st.subheader("CRUD Campañas")
    db = get_session()
    if campana_crud:
        tab1, tab2, tab3 = st.tabs(["Ver Campañas", "Crear Campaña", "Editar/Eliminar Campaña"])
        with tab1:
            campanas = get_campanas(db)
            df = pd.DataFrame([
                {
                    k: getattr(c, k).value if hasattr(getattr(c, k), "value") else getattr(c, k)
                    for k in c.__table__.columns.keys()
                }
                for c in campanas
            ])
            st.dataframe(df, height=400)
        with tab2:
            with st.form("crear_campana_efectividad"):
                nombre = st.text_input("Nombre", key="efectividad_crear_campana_nombre")
                descripcion = st.text_area("Descripción", key="efectividad_crear_campana_desc")
                fecha_inicio = st.date_input("Fecha inicio", value=today, key="efectividad_crear_campana_fecha_inicio")
                fecha_fin = st.date_input("Fecha fin", value=today, key="efectividad_crear_campana_fecha_fin")
                meta_monetaria = st.number_input("Meta monetaria", min_value=0.0, step=0.01, key="efectividad_crear_campana_meta")
                estado = st.selectbox("Estado", ["planificada", "activa", "pausada", "finalizada"], key="efectividad_crear_campana_estado")
                organizacion_id = st.number_input("Organización ID", min_value=1, key="efectividad_crear_campana_org_id")
                categoria_id = st.number_input("Categoría ID", min_value=1, key="efectividad_crear_campana_cat_id")
                sede_principal_id = st.number_input("Sede Principal ID", min_value=1, key="efectividad_crear_campana_sede_id")
                if st.form_submit_button("Crear"):
                    try:
                        data = {
                            "nombre": nombre,
                            "descripcion": descripcion,
                            "fecha_inicio": fecha_inicio,
                            "fecha_fin": fecha_fin,
                            "meta_monetaria": meta_monetaria,
                            "estado": estado,
                            "organizacion_id": organizacion_id,
                            "categoria_id": categoria_id,
                            "sede_principal_id": sede_principal_id
                        }
                        create_campana(db, data)
                        st.success("Campaña creada!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab3:
            campana_id = st.number_input("ID Campaña", min_value=1, key="efectividad_edit_campana_id")
            campana = get_campana(db, campana_id)
            if campana:
                with st.form("editar_campana_efectividad"):
                    nombre = st.text_input("Nombre", value=campana.nombre, key="efectividad_edit_campana_nombre")
                    descripcion = st.text_area("Descripción", value=campana.descripcion or "", key="efectividad_edit_campana_desc")
                    fecha_inicio = st.date_input("Fecha inicio", value=campana.fecha_inicio or today, key="efectividad_edit_campana_fecha_inicio")
                    fecha_fin = st.date_input("Fecha fin", value=campana.fecha_fin or today, key="efectividad_edit_campana_fecha_fin")
                    meta_monetaria = st.number_input("Meta monetaria", min_value=0.0, step=0.01, value=float(campana.meta_monetaria) if campana.meta_monetaria else 0.0, key="efectividad_edit_campana_meta")
                    # CORRECCIÓN: Convertir Enum a string para el índice
                    estado_list = ["planificada", "activa", "pausada", "finalizada"]
                    estado_value = campana.estado.value if hasattr(campana.estado, 'value') else str(campana.estado) if campana.estado else None
                    estado = st.selectbox("Estado", estado_list, index=estado_list.index(estado_value) if estado_value in estado_list else 0)
                    organizacion_id = st.number_input("Organización ID", min_value=1, value=campana.organizacion_id, key="efectividad_edit_campana_org_id")
                    categoria_id = st.number_input("Categoría ID", min_value=1, value=campana.categoria_id, key="efectividad_edit_campana_cat_id")
                    sede_principal_id = st.number_input("Sede Principal ID", min_value=1, value=campana.sede_principal_id, key="efectividad_edit_campana_sede_id")
                    submitted_update = st.form_submit_button("Actualizar")
                    submitted_delete = st.form_submit_button("Eliminar")
                    if submitted_update:
                        try:
                            data = {
                                "nombre": nombre,
                                "descripcion": descripcion,
                                "fecha_inicio": fecha_inicio,
                                "fecha_fin": fecha_fin,
                                "meta_monetaria": meta_monetaria,
                                "estado": estado,
                                "organizacion_id": organizacion_id,
                                "categoria_id": categoria_id,
                                "sede_principal_id": sede_principal_id
                            }
                            update_campana(db, campana_id, data)
                            st.success("Campaña actualizada!")
                        except ValueError as ve:
                            st.error(f"Error: {str(ve)}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if submitted_delete:
                        try:
                            if delete_campana(db, campana_id):
                                st.success("Campaña eliminada!")
                            else:
                                st.error("No se encontró la campaña para eliminar.")
                        except ValueError as ve:
                            st.error(f"Error al eliminar campaña: {str(ve)}")
                        except Exception as e:
                            st.error(f"Error inesperado: {str(e)}")
def main():
    st.set_page_config(page_title="ONG ORM", layout="wide")
    #organizacion_crud()
    resumen_donaciones_por_campana()
    #participacion_voluntarios_por_actividad()
    #donaciones_por_donante()
    #distribucion_voluntarios_por_edad()
    #efectividad_campanas()

if __name__ == "__main__":
    main()