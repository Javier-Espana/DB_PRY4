-- DDL generado automáticamente
CREATE TYPE estado_campana AS ENUM ('planificada', 'activa', 'pausada', 'finalizada');
CREATE TYPE tipo_donante AS ENUM ('individual', 'empresa');
CREATE TYPE tipo_donacion AS ENUM ('monetaria', 'especie');
CREATE TYPE nivel_habilidad AS ENUM ('básico', 'intermedio', 'avanzado');
CREATE TYPE tipo_contacto AS ENUM ('email', 'teléfono', 'correo', 'sms', 'whatsapp');
CREATE TYPE dia_semana AS ENUM ('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo');

--tablas

CREATE TABLE categoria (
	categoria_id SERIAL NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	descripcion TEXT, 
	PRIMARY KEY (categoria_id), 
	UNIQUE (nombre)
);

CREATE TABLE donante (
	donante_id SERIAL NOT NULL, 
	tipo tipo_donante NOT NULL, 
	nombre VARCHAR(50), 
	apellido VARCHAR(50), 
	empresa VARCHAR(100), 
	email VARCHAR(100), 
	telefono VARCHAR(20), 
	direccion TEXT, 
	fecha_registro DATE DEFAULT CURRENT_DATE NOT NULL, 
	PRIMARY KEY (donante_id), 
	CONSTRAINT chk_tipo_donante CHECK ((tipo = 'individual' AND apellido IS NOT NULL AND nombre IS NOT NULL AND empresa IS NULL) OR (tipo = 'empresa' AND empresa IS NOT NULL AND nombre IS NULL AND apellido IS NULL)), 
	UNIQUE (email)
);

CREATE TABLE habilidad (
	habilidad_id SERIAL NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	descripcion TEXT, 
	categoria VARCHAR(50), 
	PRIMARY KEY (habilidad_id), 
	UNIQUE (nombre)
);

CREATE TABLE organizacion (
	organizacion_id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion TEXT, 
	email VARCHAR(100) NOT NULL, 
	telefono VARCHAR(20), 
	direccion TEXT, 
	sitio_web VARCHAR(100), 
	fecha_registro DATE DEFAULT CURRENT_DATE NOT NULL, 
	activa BOOLEAN DEFAULT TRUE, 
	PRIMARY KEY (organizacion_id), 
	CONSTRAINT chk_email_org CHECK (email ~* '^[A-Za-z0-9._%%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'), 
	UNIQUE (email)
);

CREATE TABLE sede (
	sede_id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	direccion TEXT NOT NULL, 
	ciudad VARCHAR(50) NOT NULL, 
	region VARCHAR(50), 
	codigo_postal VARCHAR(10), 
	telefono VARCHAR(20), 
	email VARCHAR(100), 
	horario_apertura TIME WITHOUT TIME ZONE, 
	horario_cierre TIME WITHOUT TIME ZONE, 
	PRIMARY KEY (sede_id), 
	CONSTRAINT chk_horario CHECK (horario_cierre > horario_apertura)
);

CREATE TABLE voluntario (
	voluntario_id SERIAL NOT NULL, 
	nombre VARCHAR(50) NOT NULL, 
	apellido VARCHAR(50) NOT NULL, 
	email VARCHAR(100) NOT NULL, 
	telefono VARCHAR(20), 
	direccion TEXT, 
	fecha_nacimiento DATE NOT NULL, 
	fecha_registro DATE DEFAULT CURRENT_DATE NOT NULL, 
	activo BOOLEAN DEFAULT TRUE, 
	PRIMARY KEY (voluntario_id), 
	CONSTRAINT chk_edad CHECK (fecha_nacimiento <= CURRENT_DATE - INTERVAL '16 years'), 
	CONSTRAINT chk_email_voluntario CHECK (email ~* '^[A-Za-z0-9._%%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'), 
	UNIQUE (email)
);

CREATE TABLE campana (
	campana_id SERIAL NOT NULL, 
	organizacion_id INTEGER NOT NULL, 
	categoria_id INTEGER, 
	sede_principal_id INTEGER, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion TEXT, 
	fecha_inicio DATE NOT NULL, 
	fecha_fin DATE, 
	meta_monetaria DECIMAL(12, 2) CHECK (meta_monetaria > 0), 
	estado estado_campana DEFAULT 'planificada' NOT NULL, 
	PRIMARY KEY (campana_id), 
	CONSTRAINT chk_fechas CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio), 
	CONSTRAINT fk_campana_organizacion_id_1 FOREIGN KEY(organizacion_id) REFERENCES organizacion (organizacion_id), 
	CONSTRAINT fk_campana_categoria_id_2 FOREIGN KEY(categoria_id) REFERENCES categoria (categoria_id), 
	CONSTRAINT fk_campana_sede_principal_id_3 FOREIGN KEY(sede_principal_id) REFERENCES sede (sede_id)
);

CREATE TABLE disponibilidad_voluntario (
	disponibilidad_id SERIAL NOT NULL, 
	voluntario_id INTEGER, 
	dia dia_semana NOT NULL, 
	hora_inicio TIME WITHOUT TIME ZONE NOT NULL, 
	hora_fin TIME WITHOUT TIME ZONE NOT NULL, 
	PRIMARY KEY (disponibilidad_id), 
	CONSTRAINT chk_horas CHECK (hora_fin > hora_inicio), 
	CONSTRAINT uq_disponibilidad UNIQUE (voluntario_id, dia, hora_inicio, hora_fin), 
	CONSTRAINT fk_disponibilidad_voluntario_voluntario_id_1 FOREIGN KEY(voluntario_id) REFERENCES voluntario (voluntario_id)
);

CREATE TABLE preferencia_contacto (
	preferencia_id SERIAL NOT NULL, 
	donante_id INTEGER, 
	tipo tipo_contacto NOT NULL, 
	valor VARCHAR(100), 
	permitido BOOLEAN DEFAULT TRUE, 
	prioridad INTEGER, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	PRIMARY KEY (preferencia_id), 
	CONSTRAINT uq_preferencia_contacto UNIQUE (donante_id, tipo), 
	CONSTRAINT fk_preferencia_contacto_donante_id_1 FOREIGN KEY(donante_id) REFERENCES donante (donante_id)
);

CREATE TABLE voluntario_habilidad (
	voluntario_id INTEGER NOT NULL, 
	habilidad_id INTEGER NOT NULL, 
	nivel nivel_habilidad DEFAULT 'básico' NOT NULL, 
	anios_experiencia INTEGER CHECK (anios_experiencia >= 0), 
	certificado BOOLEAN DEFAULT FALSE, 
	PRIMARY KEY (voluntario_id, habilidad_id), 
	CONSTRAINT fk_voluntario_habilidad_voluntario_id_1 FOREIGN KEY(voluntario_id) REFERENCES voluntario (voluntario_id), 
	CONSTRAINT fk_voluntario_habilidad_habilidad_id_2 FOREIGN KEY(habilidad_id) REFERENCES habilidad (habilidad_id)
);

CREATE TABLE actividad (
	actividad_id SERIAL NOT NULL, 
	campana_id INTEGER NOT NULL, 
	sede_id INTEGER, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion TEXT, 
	fecha_inicio TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	fecha_fin TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	capacidad_max INTEGER CHECK (capacidad_max > 0), 
	PRIMARY KEY (actividad_id), 
	CONSTRAINT chk_fechas_actividad CHECK (fecha_fin > fecha_inicio), 
	CONSTRAINT fk_actividad_campana_id_1 FOREIGN KEY(campana_id) REFERENCES campana (campana_id), 
	CONSTRAINT fk_actividad_sede_id_2 FOREIGN KEY(sede_id) REFERENCES sede (sede_id)
);

CREATE TABLE donacion (
	donacion_id SERIAL NOT NULL, 
	donante_id INTEGER NOT NULL, 
	campana_id INTEGER NOT NULL, 
	tipo tipo_donacion NOT NULL, 
	monto DECIMAL(12, 2) CHECK (monto > 0), 
	descripcion_especie TEXT, 
	fecha TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	anonima BOOLEAN DEFAULT FALSE, 
	mensaje TEXT, 
	PRIMARY KEY (donacion_id), 
	CONSTRAINT chk_tipo_donacion CHECK ((tipo = 'monetaria' AND monto IS NOT NULL AND descripcion_especie IS NULL) OR (tipo = 'especie' AND descripcion_especie IS NOT NULL)), 
	CONSTRAINT fk_donacion_donante_id_1 FOREIGN KEY(donante_id) REFERENCES donante (donante_id) ON DELETE CASCADE ON UPDATE CASCADE, 
	CONSTRAINT fk_donacion_campana_id_2 FOREIGN KEY(campana_id) REFERENCES campana (campana_id)
);

CREATE TABLE estadisticas_campana (
	campana_id INTEGER NOT NULL, 
	monto_recaudado DECIMAL(12, 2) DEFAULT 0, 
	porcentaje_meta DECIMAL(5, 2) DEFAULT 0, 
	num_donaciones INTEGER DEFAULT 0, 
	num_voluntarios INTEGER DEFAULT 0, 
	ultima_actualizacion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (campana_id), 
	CONSTRAINT fk_estadisticas_campana_campana_id_1 FOREIGN KEY(campana_id) REFERENCES campana (campana_id)
);

CREATE TABLE recurso (
	recurso_id SERIAL NOT NULL, 
	campana_id INTEGER NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	descripcion TEXT, 
	cantidad_requerida INTEGER NOT NULL CHECK (cantidad_requerida > 0), 
	cantidad_actual INTEGER DEFAULT 0 NOT NULL CHECK (cantidad_actual >= 0), 
	unidad_medida VARCHAR(20), 
	PRIMARY KEY (recurso_id), 
	CONSTRAINT fk_recurso_campana_id_1 FOREIGN KEY(campana_id) REFERENCES campana (campana_id)
);

CREATE TABLE voluntario_actividad (
	voluntario_id INTEGER NOT NULL, 
	actividad_id INTEGER NOT NULL, 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL, 
	horas_dedicadas DECIMAL(5, 2) DEFAULT 0, 
	comentarios TEXT, 
	estado VARCHAR(20) DEFAULT 'pendiente', 
	PRIMARY KEY (voluntario_id, actividad_id), 
	CONSTRAINT fk_voluntario_actividad_voluntario_id_1 FOREIGN KEY(voluntario_id) REFERENCES voluntario (voluntario_id), 
	CONSTRAINT fk_voluntario_actividad_actividad_id_2 FOREIGN KEY(actividad_id) REFERENCES actividad (actividad_id)
);

--TRIGGERS
CREATE OR REPLACE FUNCTION actualizar_estadisticas_donacion()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo = 'monetaria' THEN
        UPDATE estadisticas_campana
        SET monto_recaudado = monto_recaudado + NEW.monto,
            num_donaciones = num_donaciones + 1,
            porcentaje_meta = (
                SELECT CASE WHEN meta_monetaria > 0 
                       THEN ((monto_recaudado + NEW.monto) / meta_monetaria) * 100
                       ELSE 0 
                       END
                FROM campana WHERE campana_id = NEW.campana_id
            ),
            ultima_actualizacion = CURRENT_TIMESTAMP
        WHERE campana_id = NEW.campana_id;
    ELSE
        UPDATE estadisticas_campana
        SET num_donaciones = num_donaciones + 1,
            ultima_actualizacion = CURRENT_TIMESTAMP
        WHERE campana_id = NEW.campana_id;
    END IF;
    
    IF NOT FOUND THEN
        INSERT INTO estadisticas_campana (
            campana_id, 
            monto_recaudado, 
            porcentaje_meta,
            num_donaciones
        ) VALUES (
            NEW.campana_id, 
            CASE WHEN NEW.tipo = 'monetaria' THEN NEW.monto ELSE 0 END,
            (
                SELECT CASE WHEN meta_monetaria > 0 
                       THEN (CASE WHEN NEW.tipo = 'monetaria' THEN NEW.monto ELSE 0 END / meta_monetaria) * 100
                       ELSE 0 
                       END
                FROM campana WHERE campana_id = NEW.campana_id
            ),
            1
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_donacion_insert
AFTER INSERT ON donacion
FOR EACH ROW
EXECUTE FUNCTION actualizar_estadisticas_donacion();

CREATE OR REPLACE FUNCTION actualizar_estadisticas_voluntario()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE estadisticas_campana
    SET num_voluntarios = (
            SELECT COUNT(DISTINCT va.voluntario_id) 
            FROM voluntario_actividad va
            JOIN actividad a ON va.actividad_id = a.actividad_id
            WHERE a.campana_id = (
                SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id
            )
        ),
        ultima_actualizacion = CURRENT_TIMESTAMP
    WHERE campana_id = (
        SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id
    );
    
    IF NOT FOUND THEN
        INSERT INTO estadisticas_campana (
            campana_id,
            num_voluntarios
        ) VALUES (
            (SELECT campana_id FROM actividad WHERE actividad_id = NEW.actividad_id),
            1
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_voluntario_actividad_insert
AFTER INSERT ON voluntario_actividad
FOR EACH ROW
EXECUTE FUNCTION actualizar_estadisticas_voluntario();

CREATE OR REPLACE FUNCTION actualizar_estado_campana()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE campana
    SET estado = 
        CASE
            WHEN fecha_inicio > CURRENT_DATE THEN 'planificada'
            WHEN fecha_fin IS NULL AND fecha_inicio <= CURRENT_DATE THEN 'activa'
            WHEN fecha_fin <= CURRENT_DATE THEN 'finalizada'
            WHEN fecha_inicio <= CURRENT_DATE AND fecha_fin > CURRENT_DATE THEN 'activa'
            ELSE estado
        END
    WHERE campana_id = NEW.campana_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_campana_date_update
BEFORE INSERT OR UPDATE OF fecha_inicio, fecha_fin ON campana
FOR EACH ROW
EXECUTE FUNCTION actualizar_estado_campana();
