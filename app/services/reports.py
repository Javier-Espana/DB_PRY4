from datetime import datetime
from db.connection import get_connection
from utils.helpers import safe_divide
from typing import Optional


# TODO: Reescribir todos los métodos de reporte usando solo SQLAlchemy ORM.
# Eliminar SQL crudo y usar consultas ORM sobre los modelos definidos en models.py


def get_donaciones_por_campana(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    monto_minimo: Optional[float] = None,
    monto_maximo: Optional[float] = None
) -> list[dict]:
    query = """
    SELECT 
        c.campana_id,
        c.nombre AS campana, 
        COUNT(d.donacion_id) AS total_donaciones, 
        COALESCE(SUM(d.monto), 0) AS monto_total,
        c.fecha_inicio,
        c.fecha_fin,
        c.meta_monetaria,
        CASE 
            WHEN c.meta_monetaria > 0 THEN COALESCE(SUM(d.monto), 0) / c.meta_monetaria 
            ELSE 0 
        END AS porcentaje_cumplimiento
    FROM campana c
    LEFT JOIN donacion d ON c.campana_id = d.campana_id
    WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        query += " AND (d.fecha IS NULL OR d.fecha >= %s)"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND (d.fecha IS NULL OR d.fecha <= %s)"
        params.append(fecha_fin)
    if monto_minimo:
        query += " AND (d.monto IS NULL OR d.monto >= %s)"
        params.append(monto_minimo)
    if monto_maximo:
        query += " AND (d.monto IS NULL OR d.monto <= %s)"
        params.append(monto_maximo)
    
    query += """
    GROUP BY c.campana_id, c.nombre, c.fecha_inicio, c.fecha_fin, c.meta_monetaria
    ORDER BY monto_total DESC;
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def get_voluntarios_por_actividad(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    edad_minima: Optional[int] = None,
    edad_maxima: Optional[int] = None
) -> list[dict]:
    query = """
    SELECT 
        a.actividad_id,
        a.nombre AS actividad, 
        COUNT(DISTINCT va.voluntario_id) AS total_voluntarios,
        a.fecha_inicio,
        a.fecha_fin,
        AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento))) AS edad_promedio
    FROM actividad a
    LEFT JOIN voluntario_actividad va ON a.actividad_id = va.actividad_id
    LEFT JOIN voluntario v ON va.voluntario_id = v.voluntario_id
    WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        query += " AND a.fecha_inicio >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND a.fecha_fin <= %s"
        params.append(fecha_fin)
    if edad_minima:
        query += " AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) >= %s"
        params.append(edad_minima)
    if edad_maxima:
        query += " AND EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) <= %s"
        params.append(edad_maxima)
    
    query += """
    GROUP BY a.actividad_id, a.nombre, a.fecha_inicio, a.fecha_fin
    ORDER BY total_voluntarios DESC NULLS LAST;
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def get_donaciones_por_donante(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    tipo_donante: Optional[str] = None,
    monto_minimo: Optional[float] = None
) -> list[dict]:
    query = """
    SELECT 
        d.donante_id,
        CASE 
            WHEN dn.tipo = 'individual' THEN CONCAT(dn.nombre, ' ', dn.apellido)
            ELSE dn.empresa
        END AS donante,
        dn.tipo AS tipo_donante,
        COUNT(d.donacion_id) AS total_donaciones,
        SUM(d.monto) AS monto_total,
        MAX(d.fecha) AS ultima_donacion
    FROM donacion d
    JOIN donante dn ON d.donante_id = dn.donante_id
    WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        query += " AND d.fecha >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND d.fecha <= %s"
        params.append(fecha_fin)
    if tipo_donante:
        query += " AND dn.tipo = %s"
        params.append(tipo_donante)
    if monto_minimo:
        query += " AND d.monto >= %s"
        params.append(monto_minimo)
    
    query += """
    GROUP BY d.donante_id, dn.nombre, dn.apellido, dn.empresa, dn.tipo
    ORDER BY monto_total DESC NULLS LAST
    LIMIT 50;
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def get_distribucion_voluntarios_por_edad(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    genero: Optional[str] = None,
    actividad_id: Optional[int] = None
) -> list[dict]:
    query = """
    SELECT 
        CASE
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) < 18 THEN 'Menor de 18'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 18 AND 25 THEN '18-25'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 26 AND 35 THEN '26-35'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 36 AND 50 THEN '36-50'
            ELSE 'Mayor de 50'
        END AS grupo_edad,
        COUNT(DISTINCT v.voluntario_id) AS total_voluntarios,
        ROUND(AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)))) AS edad_promedio
    FROM voluntario v
    JOIN voluntario_actividad va ON v.voluntario_id = va.voluntario_id
    JOIN actividad a ON va.actividad_id = a.actividad_id
    WHERE 1=1
    """
    params = []

    if fecha_inicio:
        query += " AND a.fecha_inicio >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND a.fecha_fin <= %s"
        params.append(fecha_fin)
    if genero:
        query += " AND v.genero = %s"
        params.append(genero)
    if actividad_id:
        query += " AND a.actividad_id = %s"
        params.append(actividad_id)

    query += """
    GROUP BY 
        CASE
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) < 18 THEN 'Menor de 18'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 18 AND 25 THEN '18-25'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 26 AND 35 THEN '26-35'
            WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, v.fecha_nacimiento)) BETWEEN 36 AND 50 THEN '36-50'
            ELSE 'Mayor de 50'
        END
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def get_efectividad_campanas(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    monto_objetivo_min: Optional[float] = None,
    monto_objetivo_max: Optional[float] = None,
    estado: Optional[str] = None
) -> list[dict]:
    query = """
    SELECT 
        c.campana_id,
        c.nombre AS campana,
        c.fecha_inicio,
        c.fecha_fin,
        c.meta_monetaria,
        c.estado,
        COALESCE(SUM(d.monto), 0) AS monto_recaudado,
        CASE 
            WHEN c.meta_monetaria > 0 THEN COALESCE(SUM(d.monto), 0) / c.meta_monetaria
            ELSE 0
        END AS porcentaje_cumplimiento,
        COUNT(d.donacion_id) AS total_donaciones,
        (SELECT COUNT(DISTINCT va.voluntario_id)
          FROM voluntario_actividad va
          JOIN actividad a ON va.actividad_id = a.actividad_id
          WHERE a.campana_id = c.campana_id) AS total_voluntarios
    FROM campana c
    LEFT JOIN donacion d ON c.campana_id = d.campana_id
    WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        query += " AND c.fecha_inicio >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND (c.fecha_fin IS NULL OR c.fecha_fin <= %s)"
        params.append(fecha_fin)
    if monto_objetivo_min:
        query += " AND c.meta_monetaria >= %s"
        params.append(monto_objetivo_min)
    if monto_objetivo_max:
        query += " AND c.meta_monetaria <= %s"
        params.append(monto_objetivo_max)
    if estado:
        query += " AND c.estado = %s"
        params.append(estado)
    
    query += """
    GROUP BY c.campana_id, c.nombre, c.fecha_inicio, c.fecha_fin, c.meta_monetaria, c.estado
    ORDER BY porcentaje_cumplimiento DESC NULLS LAST;
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()   

def get_recurso_utilizado_por_campana(
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None,
    tipo_recurso: Optional[str] = None,
    porcentaje_minimo: Optional[float] = None
) -> list[dict]:
    """NUEVO REPORTE 5: Recursos utilizados por campaña"""
    query = """
    SELECT 
        c.campana_id,
        c.nombre AS campana,
        r.nombre AS recurso,
        r.cantidad_requerida,
        r.cantidad_actual,
        safe_divide(r.cantidad_actual, r.cantidad_requerida) AS porcentaje_completado,
        r.unidad_medida
    FROM campana c
    JOIN recurso r ON c.campana_id = r.campana_id
    JOIN actividad a ON c.campana_id = a.campana_id
    WHERE 1=1
    """
    params = []
    
    if fecha_inicio:
        query += " AND a.fecha_inicio >= %s"
        params.append(fecha_inicio)
    if fecha_fin:
        query += " AND a.fecha_fin <= %s"
        params.append(fecha_fin)
    if tipo_recurso:
        query += " AND r.nombre ILIKE %s"
        params.append(f'%{tipo_recurso}%')
    if porcentaje_minimo:
        query += " AND (r.cantidad_actual / r.cantidad_requerida) >= %s"
        params.append(porcentaje_minimo/100)
    
    query += """
    GROUP BY c.campana_id, c.nombre, r.recurso_id, r.nombre, r.cantidad_requerida, 
             r.cantidad_actual, r.unidad_medida
    ORDER BY porcentaje_completado DESC;
    """
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()