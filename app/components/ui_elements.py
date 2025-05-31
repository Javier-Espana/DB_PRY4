import streamlit as st
import pandas as pd
import plotly.express as px
import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO


def df_to_pdf(df: pd.DataFrame):
    # Crear un buffer en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Convertir el DataFrame a una lista de listas
    data = [df.columns.tolist()] + df.values.tolist()

    # Crear la tabla
    table = Table(data)

    # Estilo de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))

    # Construir el documento
    doc.build([table])

    # Regresar el buffer con el PDF
    buffer.seek(0)
    return buffer.read()

# Descargar Excel
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    return output.getvalue()

def render_table(title: str, data: list[dict]):
    st.subheader(title)
    if not data:
        st.info("No hay datos disponibles.")
        return

    df = pd.DataFrame(data)

    csv = df.to_csv(index=False).encode('utf-8')
    excel = to_excel(df)
    json = df.to_json(orient="records", indent=2)
    pdf_data = df_to_pdf(df)

    # Asegurar que columnas monetarias y porcentajes sean numéricas
    for col in ['monto_total', 'monto_recaudado', 'meta_monetaria']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in ['porcentaje_cumplimiento', 'porcentaje_completado']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') / 100  # si vienen como 75 → 0.75

    # Formatos
    format_dict = {
        'monto_total': "${:,.2f}",
        'monto_recaudado': "${:,.2f}",
        'meta_monetaria': "${:,.2f}",
        'porcentaje_cumplimiento': "{:.2%}",
        'porcentaje_completado': "{:.2%}",
        'edad_promedio': "{:.1f}",
    }

    format_columns = {k: v for k, v in format_dict.items() if k in df.columns}

    st.dataframe(
        df.style.format(format_columns),
        use_container_width=True,
        height=min(35 * len(df) + 3, 500)
    )

    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.download_button(
            label="📄 Descargar CSV",
            data=csv,
            file_name=f"{title.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="📊 Descargar Excel",
            data=excel,
            file_name=f"{title.lower().replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with col3:
        st.download_button(
            label="🗂 Descargar JSON",
            data=json,
            file_name=f"{title.lower().replace(' ', '_')}.json",
            mime="application/json"
        )

    with col4:
        st.download_button(
            label="📄 Descargar PDF",
            data=pdf_data,
            file_name=f"{title.lower().replace(' ', '_')}.pdf",
            mime="application/pdf"
        )



def render_metric(label: str, value: str | int | float, delta: str = ""):
    st.metric(label=label, value=value, delta=delta)

def render_filters(filters: dict):
    """Función para renderizar filtros comunes"""
    with st.expander("Filtros"):
        for key, config in filters.items():
            if config["type"] == "date":
                st.date_input(
                    label=config["label"],
                    value=config["value"],
                    key=key
                )
            elif config["type"] == "number":
                st.number_input(
                    label=config["label"],
                    min_value=config.get("min", 0),
                    max_value=config.get("max", None),
                    value=config["value"],
                    step=config.get("step", 1),
                    key=key
                )
            elif config["type"] == "select":
                st.selectbox(
                    label=config["label"],
                    options=config["options"],
                    key=key
                )