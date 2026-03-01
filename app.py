import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import io

# ==================================================
# CONFIGURACIÓN
# ==================================================

st.set_page_config(
    page_title="Sistema de Producción - DANISAN",
    layout="wide"
)

st.markdown("""
<style>

body {
    background-color: #0E1117;
}

.block-container {
    padding-top: 2rem;
}

div[data-testid="metric-container"] {
    background-color: #1C1F26;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.4);
}

h1, h2, h3 {
    color: #E8E8E8;
}

</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Sistema de Producción - DANISAN", layout="wide")
st.title("Sistema de Producción - DANISAN")

conn = sqlite3.connect("produccion.db", check_same_thread=False)
cursor = conn.cursor()

# ==================================================
# CREAR TABLAS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    codigo TEXT PRIMARY KEY,
    producto TEXT UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    responsable TEXT,
    fecha TEXT,
    area TEXT,
    producto TEXT,
    lote TEXT,
    cantidad REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS salidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    responsable TEXT,
    fecha TEXT,
    destino TEXT,
    producto TEXT,
    lote TEXT,
    cantidad REAL,
    factura TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS devoluciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT,
    cliente TEXT,
    factura TEXT,
    producto TEXT,
    lote TEXT,
    cantidad REAL,
    motivo TEXT,
    estado_producto TEXT,
    destino TEXT,
    responsable TEXT,
    decision_calidad TEXT,
    fecha_decision TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS equivalencias_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_base TEXT,
    referencia TEXT UNIQUE,
    peso_kg REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS parametros_bache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_base TEXT UNIQUE,
    tamaño_bache REAL
)
""")

# ==================================================
# TABLA USUARIOS
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    contraseña TEXT,
    rol TEXT,
    modulos TEXT
)
""")

conn.commit()

# ==================================================
# LISTA COMPLETA DE PRODUCTOS
# ==================================================

productos_lista = [
("ALA-001","ALA AHUMADA X 250G"),
("ALA-002","ALA AHUMADA X 350G"),
("ALA-003","ALA AHUMADA X 500G"),
("ALA-004","ALA AHUMADA X 1000G"),
("BUT-001","BUTIFARRA X 450 GR"),
("CH-002","CHORIZO ARGENTINO X 5"),
("CH-003","CHORIZO COCTEL X 500"),
("CH-004","CHORIZO COCTEL X 250"),
("CH-005","CHORIZO RECORTE X 1000 GR"),
("CH-101","CHORIZO CUNCIA X 5"),
("CH-102","CHORIZO CUNCIA X 10"),
("CH-103","CHORIZO CUNCIA X 4 (MINI)"),
("CH-104","CHORIZO CUNCIA X 8 (MINI)"),
("CH-106","CHORIZO CUNCIA CASERO TRIPA NATURAL X 10"),
("CH-107","CHORIZO CUNCIA CASERO TRIPA NATURAL X 5"),
("CH-113","CHORIZO CUNCIA X 20"),
("CH-115","CHORIZO CUNCIA X 400 GR MINI"),
("CH-203","CHORIZO CERDO X 20"),
("CH-302","CHORIZO PARRILLERO X 10"),
("CH-304","CHORIZO PARRILLERO X 400 GR MINI X10"),
("CH-400","CHORIZO AHUMADO CERDO X 5"),
("CH-401","CHORIZO AHUMADO CERDO X 10"),
("CH-403","CHORIZO DE CERDO AHUMADO X 20"),
("CH-500","CHORIZO MEXICANO CERDO X 5"),
("CH-501","CHORIZO MEXICANO CERDO X 10"),
("CH-502","CHORIZO MEXICANO X 20"),
("CH-506","CHORIZO MEXICANO X 250 G"),
("CH-507","CHORIZO MEXICANO X 400 GR (10MIN)"),
("CH-600","CHORIZO SANTA ROSANO MINI X 4"),
("CH-601","CHORIZO SANTA ROSANO X 8 MINI"),
("CH-602","CHORIZO SANTA ROSANO X 5"),
("CH-603","CHORIZO SANTA ROSANO X 10"),
("CH-604","CHORIZO SANTA ROSANO MINI X 10"),
("CH-605","CHORIZO SANTA ROSANO X 2"),
("CH-606","CHORIZO SANTA ROSANO X 20"),
("CH-608","CHORIZO SANTA ROSANO LLANERO X 12"),
("CH-700","CHORICHUZO X 450 GR"),
("CH-707","CHORIZO RANCHERO FINO X 12"),
("COS-001","COSTILLA AHUMADA X 250GRS"),
("COS-002","COSTILLA AHUMADA X 300GRS"),
("COS-003","COSTILLA AHUMADA X 350GRS"),
("COS-004","COSTILLA AHUMADA X 400GRS"),
("COS-005","COSTILLA AHUMADA X 450GR"),
("COS-006","COSTILLA AHUMADA X 500GRS"),
("COS-007","COSTILLA AHUMADA X 200GRS"),
("COS-008","COSTILLA AHUMADA X 1000GR"),
("HAM-001","HAMBURGUESA X UND"),
("HAM-002","HAMBURGUESA X 5"),
("HAM-003","HAMBURGUESA X 30"),
("HAM-004","HAMBURGUESA X 10"),
("HAM-006","HAMBURGUESA X 30 * 95 GR"),
("JAM-001","JAMÓN X 500 GR"),
("JAM-002","JAMON RECORTE"),
("JAM-003","JAMÓN X 250 GR"),
("SCH-001","SALCHICHA X LB"),
("SCH-002","SALCHICHA X 15"),
("SCH-004","SALCHICHA ESPECIAL X 4"),
("SCH-005","SALCHICHA ESPECIAL X 10"),
("TOC-001","TOCINETA AHUMADA 125GR"),
("TOC-002","TOCINETA AHUMADA 250GR"),
("TOC-003","TOCINETA AHUMADA 500GR"),
("TOC-004","TOCINETA AHUMADA 1000GR")
]

for codigo, producto in productos_lista:
    cursor.execute("INSERT OR IGNORE INTO productos VALUES (?,?)",(codigo,producto))

conn.commit()

MODULOS_SISTEMA = [
    "Entrada",
    "Salida",
    "Dashboard",
    "Trazabilidad",
    "Producción",
    "Planeación Producción",
    "Planeación vacío",
    "Orden Producción PDF",
    "Ordenes por Fecha",
    "Reporte Producción",
    "Devoluciones",
    "Análisis Despachos",
    "Tablero Gerencial",
    "Administración Usuarios"
]

# ==================================================
# LOGIN
# ==================================================

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None
    st.session_state.rol_activo = None
    st.session_state.modulos_activos = []

if st.session_state.usuario_activo is None:

    st.title("🔐 Login Sistema DANISAN")

    usuario = st.text_input("Usuario")
    contraseña = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):

        user = cursor.execute(
            "SELECT * FROM usuarios WHERE usuario=? AND contraseña=?",
            (usuario, contraseña)
        ).fetchone()

        if user:
            st.session_state.usuario_activo = user[1]
            st.session_state.rol_activo = user[3]
            st.session_state.modulos_activos = user[4].split("|")
            st.success("Ingreso correcto")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.stop()

 # ==================================================
# HEADER USUARIO ACTIVO
# ==================================================

if st.session_state.usuario_activo:

    col1, col2 = st.columns([6,1])

    with col1:
        st.write(f"👤 Usuario: {st.session_state.usuario_activo} | Rol: {st.session_state.rol_activo}")

    with col2:
        if st.button("Cerrar sesión"):
            st.session_state.usuario_activo = None
            st.session_state.rol_activo = None
            st.session_state.modulos_activos = []
            st.rerun()

# ==================================================
# MENÚ SEGÚN PERMISOS
# ==================================================

st.sidebar.title("Menú")

menu = st.sidebar.selectbox(
    "Seleccione módulo",
    st.session_state.modulos_activos
)

# ==================================================
# ENTRADA
# ==================================================

if menu == "Entrada":

    st.header("Registro de Entrada")

    with st.form("form_entrada", clear_on_submit=True):

        responsable = st.text_input("Responsable")
        fecha = st.date_input("Fecha", value=date.today())
        area = st.text_input("Área")

        productos = pd.read_sql("SELECT producto FROM productos ORDER BY producto",conn)
        producto = st.selectbox("Producto", productos["producto"])

        lote = st.text_input("Lote")
        cantidad = st.number_input("Cantidad", min_value=0.0)

        submitted = st.form_submit_button("Registrar Entrada")

        if submitted:
            cursor.execute("""
            INSERT INTO entradas (responsable,fecha,area,producto,lote,cantidad)
            VALUES (?,?,?,?,?,?)
            """,(responsable,str(fecha),area,producto,lote,cantidad))
            conn.commit()
            st.success("Entrada registrada correctamente")

# ==================================================
# SALIDA FACTURA MULTIPRODUCTO
# ==================================================

if menu == "Salida":

    st.header("Registro de Salida - Factura")

    if "carrito" not in st.session_state:
        st.session_state.carrito = []

    responsable = st.text_input("Responsable")
    fecha = st.date_input("Fecha", value=date.today())
    cliente = st.text_input("Cliente")
    factura = st.text_input("Número de Factura")

    st.divider()
    st.subheader("Agregar Producto")

    productos = pd.read_sql("SELECT DISTINCT producto FROM entradas", conn)

    if not productos.empty:

        producto = st.selectbox("Producto", productos["producto"])

        inventario = pd.read_sql(f"""
        SELECT e.lote,
        SUM(e.cantidad) -
        IFNULL((SELECT SUM(s.cantidad)
                FROM salidas s
                WHERE s.producto=e.producto
                AND s.lote=e.lote),0) as stock
        FROM entradas e
        WHERE e.producto='{producto}'
        GROUP BY e.lote
        HAVING stock>0
        """, conn)

        if not inventario.empty:

            lote = st.selectbox("Lote Disponible", inventario["lote"])
            stock_lote = inventario[inventario["lote"] == lote]["stock"].values[0]
            st.info(f"Stock disponible: {stock_lote}")

            cantidad = st.number_input("Cantidad", min_value=0.0)

            if st.button("Agregar a Factura"):

                if cantidad <= 0:
                    st.error("Cantidad inválida")
                elif cantidad > stock_lote:
                    st.error("Stock insuficiente")
                else:
                    st.session_state.carrito.append({
                        "producto": producto,
                        "lote": lote,
                        "cantidad": cantidad
                    })
                    st.success("Producto agregado")

    if st.session_state.carrito:

        st.subheader("Detalle Factura")
        df_carrito = pd.DataFrame(st.session_state.carrito)
        st.dataframe(df_carrito)

        if st.button("Confirmar Factura"):

            for item in st.session_state.carrito:
                cursor.execute("""
                INSERT INTO salidas
                (responsable,fecha,destino,producto,lote,cantidad,factura)
                VALUES (?,?,?,?,?,?,?)
                """,(responsable,str(fecha),cliente,item["producto"],
                     item["lote"],item["cantidad"],factura))

            conn.commit()
            st.success("Factura registrada correctamente")
            st.session_state.carrito = []

# ==================================================
# DASHBOARD MEJORADO
# ==================================================

if menu == "Dashboard":

    st.header("Dashboard Inventario")

    # INVENTARIO COMPLETO (BASE)
    inventario_completo = pd.read_sql("""
    SELECT e.producto, e.lote,
    SUM(e.cantidad) -
    IFNULL((SELECT SUM(s.cantidad)
            FROM salidas s
            WHERE s.producto=e.producto
            AND s.lote=e.lote),0) as stock
    FROM entradas e
    GROUP BY e.producto, e.lote
    HAVING stock > 0
    """, conn)

    if inventario_completo.empty:
        st.warning("No hay inventario disponible.")
    else:

        # ==================================================
        # TOP 10 PRODUCTOS CON MAYOR INVENTARIO
        # ==================================================

        resumen_producto = inventario_completo.groupby("producto")["stock"].sum().reset_index()
        top10 = resumen_producto.sort_values(by="stock", ascending=False).head(10)

        st.subheader("Top 10 Productos con Mayor Inventario")
        st.dataframe(top10)

        # ==================================================
        # DESCARGAR INVENTARIO COMPLETO
        # ==================================================

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            inventario_completo.to_excel(writer, index=False)

        st.download_button(
            "Descargar Inventario Completo en Excel",
            data=output.getvalue(),
            file_name="inventario_completo.xlsx"
        )

        st.divider()

        # ==================================================
        # CONSULTAR INVENTARIO POR PRODUCTO
        # ==================================================

        st.subheader("Consultar Inventario por Producto")

        producto_sel = st.selectbox("Seleccionar Producto", resumen_producto["producto"])

        detalle_producto = inventario_completo[inventario_completo["producto"] == producto_sel]

        if not detalle_producto.empty:

            total_producto = detalle_producto["stock"].sum()

            st.write("### Lotes Disponibles")
            st.dataframe(detalle_producto)

            st.success(f"Inventario Total del Producto: {total_producto}")

# ==================================================
# TRAZABILIDAD
# ==================================================

if menu == "Trazabilidad":

    st.header("Trazabilidad")

    productos = pd.read_sql("SELECT DISTINCT producto FROM salidas",conn)

    if not productos.empty:

        producto = st.selectbox("Producto", productos["producto"])

        lotes = pd.read_sql(f"SELECT DISTINCT lote FROM salidas WHERE producto='{producto}'",conn)

        if not lotes.empty:

            lote = st.selectbox("Lote", lotes["lote"])

            trazabilidad = pd.read_sql(f"""
            SELECT fecha,responsable,destino,cantidad,factura
            FROM salidas
            WHERE producto='{producto}'
            AND lote='{lote}'
            ORDER BY fecha ASC
            """,conn)

            if not trazabilidad.empty:

                st.dataframe(trazabilidad)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    trazabilidad.to_excel(writer, index=False)

                st.download_button("Descargar Trazabilidad en Excel",
                                   data=output.getvalue(),
                                   file_name=f"trazabilidad_{producto}_{lote}.xlsx")
# ==================================================
# MODULO PRODUCCION INDUSTRIAL (SEPARADO INVENTARIO)
# ==================================================

if menu == "Producción":

    st.header("Producción Industrial")

    # ==========================================
    # CREAR TABLAS SI NO EXISTEN
    # ==========================================

    # Verificar columnas existentes

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recetas_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_base TEXT,
        insumo TEXT,
        kg_base REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tamanos_bache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_base TEXT,
        kg_bache REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS producciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_base TEXT,
        lote_produccion TEXT,
        fecha TEXT,
        kg_producir REAL,
        responsable TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consumo_materia_prima (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produccion INTEGER,
        insumo TEXT,
        lote_insumo TEXT,
        kg_usados REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS etapas_produccion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produccion INTEGER,
        etapa TEXT,
        temp_inicial REAL,
        hora_inicio TEXT,
        temp_proceso REAL,
        temp_final REAL,
        hora_final TEXT,
        temp_choque REAL,
        peso_inicial REAL,
        peso_final REAL,
        merma_kg REAL,
        merma_pct REAL,
        responsable TEXT
    )
    """)

    conn.commit()

    # ==========================================
    # IMPORTAR FORMULACIONES
    # ==========================================

    st.subheader("Importar Excel de Formulaciones")

    archivo = st.file_uploader(
        "Subir archivo Excel (RECETAS y BACHES)",
        type=["xlsx"]
    )

    if archivo:

        recetas_df = pd.read_excel(archivo, sheet_name="RECETAS")
        baches_df = pd.read_excel(archivo, sheet_name="BACHES")

        cursor.execute("DELETE FROM recetas_base")
        cursor.execute("DELETE FROM tamanos_bache")

        for _, row in recetas_df.iterrows():
            cursor.execute("""
            INSERT INTO recetas_base (producto_base,insumo,kg_base)
            VALUES (?,?,?)
            """,(row["producto_base"],
                 row["insumo"],
                 row["kg_base"]))

        for _, row in baches_df.iterrows():
            cursor.execute("""
            INSERT INTO tamanos_bache (producto_base,kg_bache)
            VALUES (?,?)
            """,(row["producto_base"],
                 row["kg_bache"]))

        conn.commit()
        st.success("Formulaciones cargadas correctamente")

    # ==========================================
    # CONTROL DE PASOS
    # ==========================================

    if "paso_prod" not in st.session_state:
        st.session_state.paso_prod = 1

    # ==========================================
    # PASO 1 CREAR PRODUCCIÓN
    # ==========================================

    if st.session_state.paso_prod == 1:

        productos = pd.read_sql(
            "SELECT DISTINCT producto_base FROM tamanos_bache",
            conn
        )

        if not productos.empty:

            with st.form("crear_produccion", clear_on_submit=True):

                producto = st.selectbox(
                    "Producto Base",
                    productos["producto_base"]
                )

                lote = st.text_input("Lote Producción")
                fecha = st.date_input("Fecha")
                kg_producir = st.number_input(
                    "Kg a producir",
                    min_value=0.0
                )
                responsable = st.text_input("Responsable")

                crear = st.form_submit_button("Crear Producción")

                if crear and lote != "" and kg_producir > 0:

                    cursor.execute("""
                    INSERT INTO producciones
                    (producto_base,lote_produccion,fecha,kg_producir,responsable)
                    VALUES (?,?,?,?,?)
                    """,(producto,lote,str(fecha),
                         kg_producir,responsable))

                    conn.commit()

                    st.session_state.id_prod = cursor.lastrowid
                    st.session_state.producto = producto
                    st.session_state.lote = lote
                    st.session_state.kg = kg_producir
                    st.session_state.paso_prod = 2
                    st.rerun()

    # ==========================================
    # PASO 2 CONSUMO MATERIA PRIMA
    # ==========================================

    elif st.session_state.paso_prod == 2:

        st.subheader("Consumo de Materia Prima")

        receta = pd.read_sql(f"""
        SELECT insumo, kg_base
        FROM recetas_base
        WHERE producto_base='{st.session_state.producto}'
        """, conn)

        tamaño = pd.read_sql(f"""
        SELECT kg_bache FROM tamanos_bache
        WHERE producto_base='{st.session_state.producto}'
        """, conn)

        if not receta.empty and not tamaño.empty:

            tamaño_base = float(tamaño.iloc[0]["kg_bache"])
            factor = st.session_state.kg / tamaño_base

            with st.form("form_insumos"):

                datos = []

                for i, row in receta.iterrows():

                    kg_teorico = row["kg_base"] * factor

                    lote_insumo = st.text_input(
                        f"{row['insumo']} - {kg_teorico:.2f} Kg",
                        key=f"ins_{i}"
                    )

                    datos.append(
                        (row["insumo"], lote_insumo, kg_teorico)
                    )

                guardar = st.form_submit_button("Guardar Consumo")

                if guardar:

                    for insumo, lote_i, kg_u in datos:

                        cursor.execute("""
                        INSERT INTO consumo_materia_prima
                        (id_produccion,insumo,lote_insumo,kg_usados)
                        VALUES (?,?,?,?)
                        """,(st.session_state.id_prod,
                             insumo,lote_i,kg_u))

                    conn.commit()
                    st.session_state.paso_prod = 3
                    st.rerun()

    # ==========================================
    # PASO 3 ETAPAS
    # ==========================================

    elif st.session_state.paso_prod == 3:

        st.subheader("Etapas del Proceso")

        etapas = [
            "Molido","Mezclado","Embutido",
            "Inyectado","Tombleado",
            "Moldeado","Cocción"
        ]

        with st.form("form_etapas"):

            etapa = st.selectbox("Etapa", etapas)

            temp_inicial = st.number_input("T° Inicial")
            hora_inicio = st.time_input("Hora Inicio")
            temp_proceso = st.number_input("T° en Proceso")
            temp_final = st.number_input("T° Final")
            hora_final = st.time_input("Hora Final")
            temp_choque = st.number_input("T° Choque Térmico")

            peso_inicial = st.number_input("Peso Inicial (Kg)")
            peso_final = st.number_input("Peso Final (Kg)")
            responsable = st.text_input("Responsable Etapa")

            guardar = st.form_submit_button("Guardar Etapa")

            if guardar and peso_inicial > 0:

                merma_kg = peso_inicial - peso_final
                merma_pct = (merma_kg / peso_inicial) * 100

                cursor.execute("""
                INSERT INTO etapas_produccion
                (id_produccion,etapa,temp_inicial,hora_inicio,
                 temp_proceso,temp_final,hora_final,temp_choque,
                 peso_inicial,peso_final,merma_kg,merma_pct,responsable)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,(st.session_state.id_prod,
                     etapa,temp_inicial,str(hora_inicio),
                     temp_proceso,temp_final,str(hora_final),
                     temp_choque,peso_inicial,peso_final,
                     merma_kg,merma_pct,responsable))

                conn.commit()

                st.success(
                    f"Merma: {merma_kg:.2f} Kg "
                    f"({merma_pct:.2f}%)"
                )

        if st.button("Finalizar Producción"):

            st.success("Producción finalizada correctamente")

            # 🔥 NO SE INSERTA EN ENTRADAS
            # Producción queda totalmente separada

            st.session_state.paso_prod = 1
            st.rerun()

# ==================================================
# ORDEN DE PRODUCCIÓN PDF FINAL (SIN ERRORES)
# ==================================================

if menu == "Orden Producción PDF":

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    st.header("Orden de Producción Imprimible")

    # ==================================================
    # ASEGURAR QUE EXISTAN LAS COLUMNAS NUEVAS
    # ==================================================

    columnas = pd.read_sql("PRAGMA table_info(producciones)", conn)

    def agregar_columna(nombre):
        if nombre not in columnas["name"].values:
            cursor.execute(f"ALTER TABLE producciones ADD COLUMN {nombre} TEXT")
            conn.commit()

    agregar_columna("firma_produccion")
    agregar_columna("firma_calidad")
    agregar_columna("fecha_liberacion")

    # ==================================================
    # TRAER PRODUCCIONES
    # ==================================================

    producciones = pd.read_sql("""
    SELECT *
    FROM producciones
    ORDER BY id DESC
    """, conn)

    if producciones.empty:
        st.warning("No hay producciones registradas.")
    else:

        producciones["mostrar"] = (
            producciones["producto_base"] +
            " - LOTE: " +
            producciones["lote_produccion"]
        )

        prod_select = st.selectbox(
            "Seleccionar Producción",
            producciones["mostrar"]
        )

        selected = producciones.loc[
            producciones["mostrar"] == prod_select
        ]

        if selected.empty:
            st.error("No se encontró la producción.")
        else:

            info = selected.iloc[0]
            id_prod = int(info["id"])

            # ==================================================
            # CAMPOS DE LIBERACIÓN
            # ==================================================

            st.subheader("Liberación del Lote")

            firma_produccion = st.text_input(
                "Firma Producción",
                value=info["firma_produccion"] if info["firma_produccion"] else ""
            )

            firma_calidad = st.text_input(
                "Firma Calidad",
                value=info["firma_calidad"] if info["firma_calidad"] else ""
            )

            fecha_liberacion = st.date_input("Fecha de Liberación")

            if st.button("Guardar Liberación"):

                cursor.execute("""
                UPDATE producciones
                SET firma_produccion=?,
                    firma_calidad=?,
                    fecha_liberacion=?
                WHERE id=?
                """,(firma_produccion,
                     firma_calidad,
                     str(fecha_liberacion),
                     id_prod))

                conn.commit()
                st.success("Liberación guardada correctamente")

            # ==================================================
            # TRAER INSUMOS
            # ==================================================

            insumos = pd.read_sql(f"""
            SELECT insumo,lote_insumo,kg_usados
            FROM consumo_materia_prima
            WHERE id_produccion={id_prod}
            """, conn)

            # ==================================================
            # TRAER ETAPAS COMPLETAS (CON TIEMPOS)
            # ==================================================

            etapas = pd.read_sql(f"""
            SELECT etapa,temp_inicial,hora_inicio,
                   temp_proceso,temp_final,hora_final,
                   temp_choque,peso_inicial,peso_final,
                   merma_kg,merma_pct,responsable
            FROM etapas_produccion
            WHERE id_produccion={id_prod}
            """, conn)

            # ==================================================
            # GENERAR PDF
            # ==================================================

            if st.button("Generar Orden en PDF"):

                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()

                elements.append(Paragraph("<b>ORDEN DE PRODUCCIÓN</b>", styles["Title"]))
                elements.append(Spacer(1, 0.3 * inch))

                # DATOS GENERALES
                tabla_general = [
                    ["Producto Base:", info["producto_base"]],
                    ["Lote Producción:", info["lote_produccion"]],
                    ["Fecha Producción:", info["fecha"]],
                    ["Kg Programados:", str(info["kg_producir"])],
                    ["Responsable General:", info["responsable"]],
                    ["Fecha Liberación:", str(info["fecha_liberacion"])]
                ]

                t1 = Table(tabla_general, colWidths=[180,300])
                t1.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
                ]))

                elements.append(t1)
                elements.append(Spacer(1, 0.4 * inch))

                # INSUMOS
                elements.append(Paragraph("<b>Consumo Materia Prima</b>", styles["Heading2"]))
                elements.append(Spacer(1, 0.2 * inch))

                tabla_insumos = [["Insumo","Lote","Kg Usados"]]

                if not insumos.empty:
                    for _, row in insumos.iterrows():
                        tabla_insumos.append([
                            str(row["insumo"]),
                            str(row["lote_insumo"]),
                            f"{row['kg_usados']:.2f}"
                        ])
                else:
                    tabla_insumos.append(["Sin registros","",""])

                t2 = Table(tabla_insumos)
                t2.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
                ]))

                elements.append(t2)
                elements.append(Spacer(1, 0.4 * inch))

                # ETAPAS COMPLETAS
                elements.append(Paragraph("<b>Etapas del Proceso</b>", styles["Heading2"]))
                elements.append(Spacer(1, 0.2 * inch))

                tabla_etapas = [[
                    "Etapa","T° Inicial","Hora Inicio",
                    "T° Proceso","T° Final","Hora Final",
                    "T° Choque","Peso Inicial","Peso Final",
                    "Merma Kg","Merma %","Responsable"
                ]]

                if not etapas.empty:
                    for _, row in etapas.iterrows():
                        tabla_etapas.append([
                            str(row["etapa"]),
                            str(row["temp_inicial"]),
                            str(row["hora_inicio"]),
                            str(row["temp_proceso"]),
                            str(row["temp_final"]),
                            str(row["hora_final"]),
                            str(row["temp_choque"]),
                            str(row["peso_inicial"]),
                            str(row["peso_final"]),
                            f"{row['merma_kg']:.2f}",
                            f"{row['merma_pct']:.2f}%",
                            str(row["responsable"])
                        ])
                else:
                    tabla_etapas.append(["Sin registros"] + [""]*11)

                t3 = Table(tabla_etapas, repeatRows=1)
                t3.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
                    ('FONTSIZE',(0,0),(-1,-1),7)
                ]))

                elements.append(t3)
                elements.append(Spacer(1, 0.4 * inch))

                # FIRMAS
                tabla_firmas = [
                    ["Firma Producción:", str(info["firma_produccion"])],
                    ["Firma Calidad:", str(info["firma_calidad"])]
                ]

                t4 = Table(tabla_firmas, colWidths=[180,300])
                t4.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black)
                ]))

                elements.append(t4)

                doc.build(elements)

                pdf = buffer.getvalue()
                buffer.close()

                st.download_button(
                    "Descargar Orden de Producción PDF",
                    data=pdf,
                    file_name=f"Orden_Produccion_{info['lote_produccion']}.pdf",
                    mime="application/pdf"
                )
# ==================================================
# ÓRDENES DE PRODUCCIÓN POR FECHA (PDF CONSOLIDADO)
# ==================================================

if menu == "Ordenes por Fecha":

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    st.header("Órdenes de Producción por Fecha")

    fecha_buscar = st.date_input("Seleccionar Fecha")

    producciones = pd.read_sql(f"""
    SELECT *
    FROM producciones
    WHERE fecha='{fecha_buscar}'
    ORDER BY id ASC
    """, conn)

    if producciones.empty:
        st.warning("No hay órdenes en esa fecha.")
    else:

        st.success(f"Se encontraron {len(producciones)} órdenes")

        st.dataframe(
            producciones[["producto_base","lote_produccion","kg_producir"]]
        )

        if st.button("Generar PDF Consolidado"):

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("<b>ÓRDENES DE PRODUCCIÓN</b>", styles["Title"]))
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph(f"Fecha: {fecha_buscar}", styles["Heading2"]))
            elements.append(Spacer(1, 0.5 * inch))

            for _, info in producciones.iterrows():

                id_prod = int(info["id"])

                elements.append(Paragraph(
                    f"<b>Producto:</b> {info['producto_base']}  |  "
                    f"<b>Lote:</b> {info['lote_produccion']}",
                    styles["Heading3"]
                ))

                elements.append(Spacer(1, 0.2 * inch))

                # ===============================
                # DATOS GENERALES
                # ===============================

                tabla_general = [
                    ["Kg Programados:", str(info["kg_producir"])],
                    ["Responsable:", str(info["responsable"])],
                    ["Fecha Liberación:", str(info["fecha_liberacion"])],
                    ["Firma Producción:", str(info["firma_produccion"])],
                    ["Firma Calidad:", str(info["firma_calidad"])]
                ]

                t1 = Table(tabla_general, colWidths=[200,280])
                t1.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black)
                ]))

                elements.append(t1)
                elements.append(Spacer(1, 0.4 * inch))

                # ===============================
                # INSUMOS
                # ===============================

                insumos = pd.read_sql(f"""
                SELECT insumo,lote_insumo,kg_usados
                FROM consumo_materia_prima
                WHERE id_produccion={id_prod}
                """, conn)

                elements.append(Paragraph("<b>Insumos</b>", styles["Heading4"]))
                elements.append(Spacer(1, 0.2 * inch))

                tabla_insumos = [["Insumo","Lote","Kg"]]

                for _, row in insumos.iterrows():
                    tabla_insumos.append([
                        row["insumo"],
                        row["lote_insumo"],
                        f"{row['kg_usados']:.2f}"
                    ])

                t2 = Table(tabla_insumos)
                t2.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('FONTSIZE',(0,0),(-1,-1),8)
                ]))

                elements.append(t2)
                elements.append(Spacer(1, 0.4 * inch))

                # ===============================
                # ETAPAS
                # ===============================

                etapas = pd.read_sql(f"""
                SELECT etapa,temp_inicial,hora_inicio,
                       temp_proceso,temp_final,hora_final,
                       temp_choque,peso_inicial,peso_final,
                       merma_kg,merma_pct,responsable
                FROM etapas_produccion
                WHERE id_produccion={id_prod}
                """, conn)

                elements.append(Paragraph("<b>Etapas</b>", styles["Heading4"]))
                elements.append(Spacer(1, 0.2 * inch))

                tabla_etapas = [[
                    "Etapa","T° Ini","Hora Ini",
                    "T° Proc","T° Fin","Hora Fin",
                    "T° Choque","Peso Ini","Peso Fin",
                    "Merma Kg","Merma %","Resp."
                ]]

                for _, row in etapas.iterrows():
                    tabla_etapas.append([
                        row["etapa"],
                        row["temp_inicial"],
                        row["hora_inicio"],
                        row["temp_proceso"],
                        row["temp_final"],
                        row["hora_final"],
                        row["temp_choque"],
                        row["peso_inicial"],
                        row["peso_final"],
                        f"{row['merma_kg']:.2f}",
                        f"{row['merma_pct']:.2f}%",
                        row["responsable"]
                    ])

                t3 = Table(tabla_etapas, repeatRows=1)
                t3.setStyle(TableStyle([
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('FONTSIZE',(0,0),(-1,-1),6)
                ]))

                elements.append(t3)
                elements.append(PageBreak())

            doc.build(elements)

            pdf = buffer.getvalue()
            buffer.close()

            st.download_button(
                "Descargar Órdenes del Día en PDF",
                data=pdf,
                file_name=f"Ordenes_{fecha_buscar}.pdf",
                mime="application/pdf"
            )
# ==================================================
# REPORTE AVANZADO DE PRODUCCIÓN
# ==================================================

if menu == "Reporte Producción":

    st.header("Reporte Avanzado de Producción")

    # ===============================
    # FILTROS
    # ===============================

    fecha_inicio = st.date_input("Fecha Inicio")
    fecha_fin = st.date_input("Fecha Fin")

    if fecha_inicio and fecha_fin:

        # ======================================
        # DATOS BASE
        # ======================================

        producciones = pd.read_sql(f"""
        SELECT *
        FROM producciones
        WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        """, conn)

        if producciones.empty:
            st.warning("No hay producciones en ese rango.")
        else:

            etapas = pd.read_sql(f"""
            SELECT *
            FROM etapas_produccion
            WHERE id_produccion IN (
                SELECT id FROM producciones
                WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
            )
            """, conn)

            # ======================================
            # 1️⃣ KG PROCESADOS TOTALES
            # ======================================

            kg_totales = producciones["kg_producir"].sum()

            st.subheader("Kg Procesados Totales")
            st.metric("Total Kg Procesados", f"{kg_totales:,.2f} kg")

            # Por Producto
            resumen_producto = producciones.groupby("producto_base")["kg_producir"].sum().reset_index()

            st.subheader("Kg Procesados por Producto")
            st.dataframe(resumen_producto)

            # ======================================
            # 2️⃣ MERMAS
            # ======================================

            if not etapas.empty:

                total_merma_kg = etapas["merma_kg"].sum()
                total_peso_inicial = etapas["peso_inicial"].sum()

                if total_peso_inicial > 0:
                    total_merma_pct = (total_merma_kg / total_peso_inicial) * 100
                else:
                    total_merma_pct = 0

                st.subheader("Indicador Total de Merma")

                col1, col2 = st.columns(2)

                col1.metric("Merma Total (kg)", f"{total_merma_kg:,.2f} kg")
                col2.metric("Merma Total (%)", f"{total_merma_pct:.2f} %")

                # Merma por Producto
                etapas_merge = etapas.merge(
                    producciones[["id","producto_base"]],
                    left_on="id_produccion",
                    right_on="id"
                )

                merma_producto = etapas_merge.groupby("producto_base").agg({
                    "merma_kg":"sum",
                    "peso_inicial":"sum"
                }).reset_index()

                merma_producto["merma_%"] = (
                    merma_producto["merma_kg"] /
                    merma_producto["peso_inicial"]
                ) * 100

                st.subheader("Merma por Producto")
                st.dataframe(merma_producto)

            # ======================================
            # 3️⃣ REPORTE AUTOMÁTICO MENSUAL
            # ======================================

            producciones["fecha"] = pd.to_datetime(producciones["fecha"])
            producciones["mes"] = producciones["fecha"].dt.to_period("M")

            reporte_mensual = producciones.groupby("mes")["kg_producir"].sum().reset_index()

            st.subheader("Producción Mensual")
            st.dataframe(reporte_mensual)

            # ======================================
            # 4️⃣ PRODUCCIÓN DIARIA Y SEMANAL
            # ======================================

            producciones["dia"] = producciones["fecha"].dt.date
            producciones["semana"] = producciones["fecha"].dt.isocalendar().week

            prod_dia = producciones.groupby("dia")["kg_producir"].sum().reset_index()
            prod_semana = producciones.groupby("semana")["kg_producir"].sum().reset_index()

            st.subheader("Producción Diaria")
            st.dataframe(prod_dia)

            st.subheader("Producción Semanal")
            st.dataframe(prod_semana)

            # ======================================
            # DESCARGA EXCEL COMPLETO
            # ======================================

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:

                producciones.to_excel(writer, sheet_name="Producciones", index=False)
                resumen_producto.to_excel(writer, sheet_name="Kg_por_producto", index=False)
                reporte_mensual.to_excel(writer, sheet_name="Mensual", index=False)
                prod_dia.to_excel(writer, sheet_name="Diario", index=False)
                prod_semana.to_excel(writer, sheet_name="Semanal", index=False)

                if not etapas.empty:
                    merma_producto.to_excel(writer, sheet_name="Merma_producto", index=False)

            st.download_button(
                "Descargar Reporte Completo en Excel",
                data=output.getvalue(),
                file_name="Reporte_Produccion.xlsx"
            )
# ==================================================
# TABLERO GERENCIAL AVANZADO
# ==================================================

if menu == "Tablero Gerencial":

    import plotly.express as px
    import plotly.graph_objects as go

    st.header("📊 TABLERO GERENCIAL – DANISAN")

    fecha_inicio = st.date_input("Fecha Inicio")
    fecha_fin = st.date_input("Fecha Fin")

    if fecha_inicio and fecha_fin:

        producciones = pd.read_sql(f"""
        SELECT *
        FROM producciones
        WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        """, conn)

        if producciones.empty:
            st.warning("No hay datos en ese rango.")
        else:

            etapas = pd.read_sql(f"""
            SELECT *
            FROM etapas_produccion
            WHERE id_produccion IN (
                SELECT id FROM producciones
                WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
            )
            """, conn)

            # ==================================================
            # KPI PRINCIPALES
            # ==================================================

            total_baches = len(producciones)
            total_kg = producciones["kg_producir"].sum()

            total_merma = etapas["merma_kg"].sum() if not etapas.empty else 0
            total_peso_inicial = etapas["peso_inicial"].sum() if not etapas.empty else 0

            merma_pct = (total_merma / total_peso_inicial * 100) if total_peso_inicial > 0 else 0

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Baches Producidos", total_baches)
            col2.metric("Kg Procesados", f"{total_kg:,.2f}")
            col3.metric("Merma Total (kg)", f"{total_merma:,.2f}")
            col4.metric("Merma Total (%)", f"{merma_pct:.2f}%")

            st.divider()

            # ==================================================
            # GRÁFICO 1 – PRODUCCIÓN POR PRODUCTO
            # ==================================================

            prod_producto = producciones.groupby("producto_base")["kg_producir"].sum().reset_index()

            fig1 = px.bar(
                prod_producto,
                x="producto_base",
                y="kg_producir",
                title="Producción por Producto (kg)",
                text_auto=True
            )

            st.plotly_chart(fig1, use_container_width=True)

            # ==================================================
            # GRÁFICO 2 – PRODUCCIÓN DIARIA
            # ==================================================

            producciones["fecha"] = pd.to_datetime(producciones["fecha"])
            prod_dia = producciones.groupby("fecha")["kg_producir"].sum().reset_index()

            fig2 = px.line(
                prod_dia,
                x="fecha",
                y="kg_producir",
                markers=True,
                title="Producción Diaria (kg)"
            )

            st.plotly_chart(fig2, use_container_width=True)

            # ==================================================
            # GRÁFICO 3 – MERMA POR PRODUCTO
            # ==================================================

            if not etapas.empty:

                merge = etapas.merge(
                    producciones[["id","producto_base"]],
                    left_on="id_produccion",
                    right_on="id"
                )

                merma_producto = merge.groupby("producto_base")["merma_kg"].sum().reset_index()

                fig3 = px.bar(
                    merma_producto,
                    x="producto_base",
                    y="merma_kg",
                    title="Merma por Producto (kg)",
                    text_auto=True,
                    color="merma_kg",
                    color_continuous_scale="reds"
                )

                st.plotly_chart(fig3, use_container_width=True)

            st.divider()

            # ==================================================
            # REPORTE TIPO AUDITORÍA INVIMA
            # ==================================================

            st.subheader("📑 REPORTE TIPO AUDITORÍA INVIMA")

            auditoria = producciones[[
                "fecha",
                "producto_base",
                "lote_produccion",
                "kg_producir",
                "responsable",
                "firma_produccion",
                "firma_calidad",
                "fecha_liberacion"
            ]]

            st.dataframe(auditoria)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:

                auditoria.to_excel(writer, sheet_name="Ordenes_Produccion", index=False)

                if not etapas.empty:
                    etapas.to_excel(writer, sheet_name="Etapas_Proceso", index=False)

            st.download_button(
                "Descargar Reporte Auditoría INVIMA",
                data=output.getvalue(),
                file_name="Reporte_Auditoria_INVIMA.xlsx"
            )

# ==================================================
# DEVOLUCIONES – LOGÍSTICA INVERSA INDUSTRIAL
# ==================================================

if menu == "Devoluciones":

    st.header("📦 DEVOLUCIONES / LOGÍSTICA INVERSA")
    st.divider()

    # ==================================================
    # REGISTRO DE DEVOLUCIÓN
    # ==================================================

    with st.form("form_devolucion_logistica_unico", clear_on_submit=True):

        fecha = st.date_input("Fecha Devolución", value=date.today())
        cliente = st.text_input("Cliente")
        factura = st.text_input("Factura Relacionada")

        productos_df = pd.read_sql("""
        SELECT DISTINCT producto 
        FROM salidas 
        ORDER BY producto
        """, conn)

        if productos_df.empty:
            st.warning("No hay productos registrados en salidas.")
            st.stop()

        producto = st.selectbox("Producto", productos_df["producto"])

        lotes_df = pd.read_sql(f"""
        SELECT DISTINCT lote
        FROM salidas
        WHERE producto='{producto}'
        """, conn)

        if lotes_df.empty:
            st.warning("No hay lotes disponibles para este producto.")
            st.stop()

        lote = st.selectbox("Lote", lotes_df["lote"])

        cantidad = st.number_input("Cantidad Devuelta", min_value=0.0)

        motivo = st.selectbox("Motivo Devolución",[
            "Fecha vencida",
            "Empaque defectuoso",
            "Error despacho",
            "Problema calidad",
            "Cliente no recibió",
            "Otro"
        ])

        estado_producto = st.selectbox("Estado Físico",[
            "Sellado intacto",
            "Empaque dañado",
            "Abierto",
            "Caducado",
            "Contaminado"
        ])

        destino = st.selectbox("Destino Inicial",[
            "Cuarentena",
            "Reproceso",
            "Destrucción",
            "Reingreso Inventario"
        ])

        responsable = st.text_input("Responsable Recepción")

        submitted = st.form_submit_button("Registrar Devolución")

        if submitted:

            cursor.execute("""
            INSERT INTO devoluciones
            (fecha,cliente,factura,producto,lote,cantidad,
             motivo,estado_producto,destino,responsable)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,(str(fecha),cliente,factura,producto,lote,
                 cantidad,motivo,estado_producto,destino,responsable))

            conn.commit()
            st.success("Devolución registrada correctamente")

    # ==================================================
    # DECISIÓN DE CALIDAD
    # ==================================================

    st.divider()
    st.subheader("🔎 Decisión de Calidad")

    devoluciones_pendientes = pd.read_sql("""
    SELECT * FROM devoluciones
    WHERE decision_calidad IS NULL
    ORDER BY id DESC
    """, conn)

    if devoluciones_pendientes.empty:
        st.info("No hay devoluciones pendientes.")
    else:

        devolucion_id = st.selectbox(
            "Seleccionar Devolución",
            devoluciones_pendientes["id"]
        )

        decision = st.selectbox("Decisión Final",[
            "Aprobado Reingreso",
            "Enviar a Reproceso",
            "Destrucción Autorizada",
            "Ajuste Inventario"
        ])

        if st.button("Guardar Decisión Calidad"):

            devolucion_data = pd.read_sql(f"""
            SELECT * FROM devoluciones
            WHERE id={devolucion_id}
            """, conn)

            if not devolucion_data.empty:

                producto = devolucion_data.iloc[0]["producto"]
                lote = devolucion_data.iloc[0]["lote"]
                cantidad = devolucion_data.iloc[0]["cantidad"]

                # Actualizar decisión
                cursor.execute("""
                UPDATE devoluciones
                SET decision_calidad=?,
                    fecha_decision=DATE('now')
                WHERE id=?
                """,(decision,devolucion_id))

                # ==================================================
                # REINGRESO AUTOMÁTICO A INVENTARIO
                # ==================================================
                if decision == "Aprobado Reingreso":

                    cursor.execute("""
                    INSERT INTO entradas
                    (responsable,fecha,area,producto,lote,cantidad)
                    VALUES (?,?,?,?,?,?)
                    """,(
                        "LOGISTICA INVERSA",
                        str(date.today()),
                        "DEVOLUCION CLIENTE",
                        producto,
                        lote,
                        cantidad
                    ))

                conn.commit()

                st.success("Decisión guardada correctamente")

                if decision == "Aprobado Reingreso":
                    st.info("Producto reingresado automáticamente al inventario.")

# ==================================================
# DEVOLUCIONES
# ==================================================

if menu == "Devoluciones":

    st.header("📦 DEVOLUCIONES")
    st.divider()

    # ===== HISTÓRICO CON FILTRO =====

    st.subheader("📋 Histórico de Devoluciones")

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio_hist = st.date_input("Desde", key="dev_desde")

    with col2:
        fecha_fin_hist = st.date_input("Hasta", key="dev_hasta")

    if fecha_inicio_hist and fecha_fin_hist:

        historico = pd.read_sql(f"""
        SELECT *
        FROM devoluciones
        WHERE fecha BETWEEN '{fecha_inicio_hist}' AND '{fecha_fin_hist}'
        ORDER BY fecha DESC
        """, conn)

        if not historico.empty:

            st.success(f"Se encontraron {len(historico)} devoluciones")
            st.dataframe(historico)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                historico.to_excel(writer, index=False)

            st.download_button(
                "📥 Descargar Histórico Filtrado en Excel",
                data=output.getvalue(),
                file_name=f"Devoluciones_{fecha_inicio_hist}_a_{fecha_fin_hist}.xlsx"
            )
        else:
            st.warning("No hay devoluciones en ese rango de fechas.")

# ==================================================
# MODULO ANALISIS DE DESPACHOS
# ==================================================

if menu == "Análisis Despachos":

    st.header("📊 ANALISIS DE PRODUCTO TERMINADO DESPACHADO")

    from datetime import datetime
    hoy = datetime.today()

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input("Desde", hoy.replace(day=1))

    with col2:
        fecha_fin = st.date_input("Hasta", hoy)

    # =========================
    # FILTRO BASE
    # =========================

    df = pd.read_sql(f"""
        SELECT *
        FROM salidas
        WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    """, conn)

    if df.empty:
        st.warning("No hay despachos en el período seleccionado.")
        st.stop()

    # =========================
    # KPI GENERALES
    # =========================

    st.subheader("📌 RESUMEN GENERAL")

    total_und = df["cantidad"].sum()
    total_facturas = df["factura"].nunique()
    total_clientes = df["destino"].nunique()
    total_lotes = df["lote"].nunique()

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total UND Despachadas", f"{total_und:,.0f}")
    k2.metric("Facturas", total_facturas)
    k3.metric("Clientes", total_clientes)
    k4.metric("Lotes", total_lotes)

    st.divider()

    # =========================
    # DESPACHO POR CLIENTE
    # =========================

    st.subheader("👥 Despacho por Cliente")

    por_cliente = df.groupby("destino")["cantidad"].sum().reset_index()
    por_cliente = por_cliente.sort_values(by="cantidad", ascending=False)

    st.dataframe(por_cliente)

    st.divider()

    # =========================
    # DESPACHO POR FACTURA
    # =========================

    st.subheader("🧾 Despacho por Factura")

    por_factura = df.groupby("factura")["cantidad"].sum().reset_index()
    st.dataframe(por_factura.sort_values(by="cantidad", ascending=False))

    st.divider()

    # =========================
    # DESPACHO POR LOTE
    # =========================

    st.subheader("🏷️ Despacho por Lote")

    por_lote = df.groupby("lote")["cantidad"].sum().reset_index()
    st.dataframe(por_lote.sort_values(by="cantidad", ascending=False))

    st.divider()

    # =========================
    # DESPACHO POR PRODUCTO
    # =========================

    st.subheader("📦 Despacho por Producto")

    por_producto = df.groupby("producto")["cantidad"].sum().reset_index()
    st.dataframe(por_producto.sort_values(by="cantidad", ascending=False))

    st.divider()

    # =========================
    # DESCARGAR REPORTE
    # =========================

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Detalle", index=False)
        por_cliente.to_excel(writer, sheet_name="Por_Cliente", index=False)
        por_factura.to_excel(writer, sheet_name="Por_Factura", index=False)
        por_lote.to_excel(writer, sheet_name="Por_Lote", index=False)
        por_producto.to_excel(writer, sheet_name="Por_Producto", index=False)

    st.download_button(
        "📥 Descargar Reporte Completo en Excel",
        data=output.getvalue(),
        file_name="Reporte_Despachos.xlsx"
    )

# ==================================================
# MODULO PLANEACION PRODUCTO TERMINADO
# ==================================================

if menu == "Planeación vacio":

    st.header("📈 PLANEACIÓN DE PRODUCTO TERMINADO")

    from datetime import datetime
    hoy = datetime.today()

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input("Analizar desde", hoy.replace(day=1))

    with col2:
        fecha_fin = st.date_input("Hasta", hoy)

    # =========================
    # DEMANDA HISTORICA
    # =========================

    df_salidas = pd.read_sql(f"""
        SELECT producto, SUM(cantidad) as total
        FROM salidas
        WHERE fecha BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
        GROUP BY producto
    """, conn)

    if df_salidas.empty:
        st.warning("No hay datos de salidas en el período.")
        st.stop()

    dias_periodo = (fecha_fin - fecha_inicio).days + 1
    df_salidas["demanda_diaria"] = df_salidas["total"] / dias_periodo

    # =========================
    # INVENTARIO ACTUAL
    # =========================

    inventario = pd.read_sql("""
        SELECT e.producto,
        SUM(e.cantidad) -
        IFNULL((SELECT SUM(s.cantidad)
                FROM salidas s
                WHERE s.producto=e.producto
                AND s.lote=e.lote),0) as stock
        FROM entradas e
        GROUP BY e.producto, e.lote
        HAVING stock > 0
    """, conn)

    inventario_total = inventario.groupby("producto")["stock"].sum().reset_index()

    # =========================
    # UNIR DEMANDA + INVENTARIO
    # =========================

    df_planeacion = df_salidas.merge(inventario_total, on="producto", how="left")
    df_planeacion["stock"] = df_planeacion["stock"].fillna(0)

    # =========================
    # PARAMETROS
    # =========================

    st.subheader("⚙️ Parámetros de Planeación")

    dias_reposicion = st.number_input("Días de reposición", value=7)
    stock_seguridad = st.number_input("Stock de seguridad (UND)", value=100)

    # =========================
    # CALCULOS
    # =========================

    df_planeacion["punto_reposicion"] = (
        df_planeacion["demanda_diaria"] * dias_reposicion
        + stock_seguridad
    )

    df_planeacion["dias_cobertura"] = (
        df_planeacion["stock"] / df_planeacion["demanda_diaria"]
    )

    df_planeacion["produccion_sugerida"] = (
        df_planeacion["punto_reposicion"] - df_planeacion["stock"]
    )

    df_planeacion["produccion_sugerida"] = df_planeacion["produccion_sugerida"].apply(
        lambda x: x if x > 0 else 0
    )

    # =========================
    # MOSTRAR RESULTADO
    # =========================

    st.subheader("📊 Resultado Planeación")

    st.dataframe(
        df_planeacion[
            [
                "producto",
                "total",
                "demanda_diaria",
                "stock",
                "dias_cobertura",
                "punto_reposicion",
                "produccion_sugerida",
            ]
        ].sort_values(by="produccion_sugerida", ascending=False)
    )

    # =========================
    # ALERTAS
    # =========================

    st.subheader("🚨 Productos en Riesgo")

    riesgo = df_planeacion[df_planeacion["dias_cobertura"] < dias_reposicion]

    if not riesgo.empty:
        st.warning("Estos productos deben producirse:")
        st.dataframe(riesgo[["producto","produccion_sugerida"]])
    else:
        st.success("No hay productos críticos.")

    # =========================
    # DESCARGAR REPORTE
    # =========================

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_planeacion.to_excel(writer, index=False)

    st.download_button(
        "📥 Descargar Planeación en Excel",
        data=output.getvalue(),
        file_name="Planeacion_Producto_Terminado.xlsx"
    )

# ==================================================
# 🧠 PLANEACIÓN PRODUCCIÓN INTELIGENTE (MRP)
# ==================================================

if menu == "Planeación Producción":

    st.header("🧠 Planeación Producción Inteligente")

    from datetime import datetime, timedelta
    import math

    hoy = datetime.today()

    # ==================================================
    # 1️⃣ PERÍODOS AUTOMÁTICOS
    # ==================================================

    fecha_fin = hoy
    fecha_inicio = hoy - timedelta(days=30)
    fecha_inicio_anterior = fecha_inicio - timedelta(days=30)

    # ==================================================
    # 2️⃣ DEMANDA ÚLTIMOS 30 DÍAS
    # ==================================================

    df_actual = pd.read_sql(f"""
        SELECT producto, SUM(cantidad) as total_und
        FROM salidas
        WHERE fecha BETWEEN '{fecha_inicio.date()}' AND '{fecha_fin.date()}'
        GROUP BY producto
    """, conn)

    df_anterior = pd.read_sql(f"""
        SELECT producto, SUM(cantidad) as total_und
        FROM salidas
        WHERE fecha BETWEEN '{fecha_inicio_anterior.date()}' AND '{fecha_inicio.date()}'
        GROUP BY producto
    """, conn)

    if df_actual.empty:
        st.warning("No hay datos suficientes para análisis.")
        st.stop()

    # ==================================================
    # 3️⃣ CALCULAR VARIACIÓN REAL
    # ==================================================

    df_tendencia = df_actual.merge(
        df_anterior,
        on="producto",
        how="left",
        suffixes=("_actual","_anterior")
    )

    df_tendencia["total_und_anterior"] = df_tendencia["total_und_anterior"].fillna(0)

    df_tendencia["variacion_%"] = df_tendencia.apply(
        lambda row: (
            ((row["total_und_actual"] - row["total_und_anterior"]) 
             / row["total_und_anterior"]) * 100
            if row["total_und_anterior"] > 0 else 0
        ),
        axis=1
    )

    crecimiento_promedio = df_tendencia["variacion_%"].mean()

    st.subheader("📈 Tendencia Detectada")
    st.write(f"Variación promedio demanda: **{round(crecimiento_promedio,2)} %**")

    # ==================================================
    # 4️⃣ CONVERTIR A KG BASE
    # ==================================================

    df_equiv = pd.read_sql("SELECT * FROM equivalencias_base", conn)

    df_merge = df_actual.merge(
        df_equiv,
        left_on="producto",
        right_on="referencia",
        how="left"
    )

    df_merge["peso_kg"] = df_merge["peso_kg"].fillna(0)
    df_merge["kg_base"] = df_merge["total_und"] * df_merge["peso_kg"]

    df_planeacion = df_merge.groupby("producto_base")["kg_base"].sum().reset_index()

    # ==================================================
    # 5️⃣ PROYECCIÓN AUTOMÁTICA
    # ==================================================

    stock_seguridad = st.number_input("Stock de seguridad (kg)", value=0.0)

    df_planeacion["kg_proyectado"] = df_planeacion["kg_base"] * (1 + crecimiento_promedio/100)
    df_planeacion["kg_total"] = df_planeacion["kg_proyectado"] + stock_seguridad

    # ==================================================
    # 6️⃣ TAMAÑO DE BACHE
    # ==================================================

    df_param = pd.read_sql("SELECT * FROM parametros_bache", conn)

    df_planeacion = df_planeacion.merge(
        df_param,
        on="producto_base",
        how="left"
    )

    df_planeacion["baches_sugeridos"] = df_planeacion.apply(
        lambda row: math.ceil(row["kg_total"] / row["tamaño_bache"])
        if row["tamaño_bache"] > 0 else 0,
        axis=1
    )

    st.divider()
    st.subheader("📊 Planeación Inteligente")
    st.dataframe(df_planeacion)

    # ==================================================
    # 7️⃣ PLAN SEMANAL LUNES A VIERNES
    # ==================================================

    st.divider()
    st.subheader("📅 Plan Semanal (Sábado Aseo General)")

    dias_produccion = ["Lunes","Martes","Miércoles","Jueves","Viernes"]
    dias_completo = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"]

    planeacion = []

    for _, row in df_planeacion.iterrows():

        total_kg = float(row["kg_total"])
        distribucion = {dia: 0 for dia in dias_completo}

        if total_kg > 0:
            kg_diario = total_kg / 5
            for dia in dias_produccion:
                distribucion[dia] = kg_diario

        fila = {"Producto Base": row["producto_base"]}
        fila.update(distribucion)
        planeacion.append(fila)

    df_semana = pd.DataFrame(planeacion)

    st.dataframe(df_semana, use_container_width=True)

    # ==================================================
    # 8️⃣ KPI GERENCIAL
    # ==================================================

    st.divider()
    st.subheader("📊 KPI Gerencial")

    total_kg_mes = df_planeacion["kg_total"].sum()
    total_baches = df_planeacion["baches_sugeridos"].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total KG Proyectados Mes", round(total_kg_mes,2))

    with col2:
        st.metric("Total Baches Sugeridos", int(total_baches))

# ==================================================
# CREAR ADMINISTRADOR PRINCIPAL
# ==================================================

admin_modulos = "|".join([
    "Entrada","Salida","Dashboard","Trazabilidad",
    "Producción","Planeación Producción","Planeación vacío",
    "Orden Producción PDF","Órdenes por Fecha",
    "Reporte Producción","Devoluciones",
    "Análisis Despachos","Tablero Gerencial",
    "Administración Usuarios"
])

cursor.execute("""
INSERT OR IGNORE INTO usuarios (usuario,contraseña,rol,modulos)
VALUES (?,?,?,?)
""", ("admin","admin123","Administrador",admin_modulos))

conn.commit()

# ==================================================
# 👑 ADMINISTRACIÓN DE USUARIOS
# ==================================================

if menu == "Administración Usuarios":

    st.header("👑 Administración de Usuarios")

    # ----------------------------------------------
    # CREAR USUARIO
    # ----------------------------------------------

    st.subheader("➕ Crear Nuevo Usuario")

    with st.form("form_crear_usuario", clear_on_submit=True):

        nuevo_usuario = st.text_input("Usuario")
        nueva_contraseña = st.text_input("Contraseña", type="password")

        rol_nuevo = st.selectbox(
            "Rol",
            ["Producción","Logistica","Calidad","Gerencia"]
        )

        modulos_asignados = st.multiselect(
            "Asignar Módulos",
            MODULOS_SISTEMA
        )

        crear = st.form_submit_button("Crear Usuario")

        if crear:

            if not nuevo_usuario or not nueva_contraseña:
                st.error("Complete todos los campos")
            elif not modulos_asignados:
                st.error("Debe asignar al menos un módulo")
            else:
                modulos_str = "|".join(modulos_asignados)

                try:
                    cursor.execute("""
                        INSERT INTO usuarios (usuario,contraseña,rol,modulos)
                        VALUES (?,?,?,?)
                    """,(nuevo_usuario,nueva_contraseña,rol_nuevo,modulos_str))
                    conn.commit()
                    st.success("Usuario creado correctamente")
                except:
                    st.error("Ese usuario ya existe")

    st.divider()

    # ----------------------------------------------
    # LISTADO
    # ----------------------------------------------

    st.subheader("📋 Usuarios Registrados")

    df_users = pd.read_sql(
        "SELECT id,usuario,rol FROM usuarios",
        conn
    )

    st.dataframe(df_users, use_container_width=True)

    st.divider()

    # ----------------------------------------------
    # ELIMINAR USUARIO
    # ----------------------------------------------

    usuario_eliminar = st.selectbox(
        "Seleccionar Usuario a Eliminar",
        df_users["usuario"].tolist()
    )

    if st.button("Eliminar Usuario"):

        if usuario_eliminar == "admin":
            st.error("No se puede eliminar el administrador principal")
        else:
            cursor.execute(
                "DELETE FROM usuarios WHERE usuario=?",
                (usuario_eliminar,)
            )
            conn.commit()
            st.success("Usuario eliminado correctamente")
            st.rerun()
