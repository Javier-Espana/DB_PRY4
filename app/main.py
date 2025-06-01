# main.py (actualizado)
import streamlit as st
from db.connection import get_session
from services.crud_organization import (
    get_organizaciones, 
    get_organizacion,  # <-- Agrega esta importación
    create_organizacion,
    update_organizacion,
    delete_organizacion
)

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
            "Activa": o.activa
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
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with tab3:
        org_id = st.number_input("ID Organización", min_value=1)
        if org_id:
            org = get_organizacion(db, org_id)
            if org:
                with st.form("editar_org"):
                    nombre = st.text_input("Nombre", value=org.nombre)
                    email = st.text_input("Email", value=org.email)
                    activa = st.checkbox("Activa", value=org.activa)
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

# Vista de reporte
def reporte_donaciones():
    st.header("Reporte de Donaciones por Campaña (Vista SQL)")
    st.info("La vista 'VistaDonacionesCampana' aún no está implementada en models.py. Agrega la clase o ajusta el reporte aquí.")

def main():
    st.set_page_config(page_title="ONG ORM", layout="wide")
    organizacion_crud()
    reporte_donaciones()

if __name__ == "__main__":
    main()