import streamlit as st
import pandas as pd
import login
import datetime

# Cargar datos desde el CSV
@st.cache_data
def cargar_usuarios():
    return pd.read_csv("usuarios.csv")

# Función para filtrar usuarios
def filtrar_usuarios(df, filtro_nombre, filtro_rol):
    if filtro_nombre:
        df = df[df["Nombre"].str.contains(filtro_nombre, case=False, na=False)]
    if filtro_rol and filtro_rol != "Todos":
        df = df[df["rol"] == filtro_rol]
    return df

# Guardar cambios en el CSV
def guardar_usuarios(df):
    df.to_csv("usuarios.csv", index=False)

archivo = __file__.split("\\")[-1]
st.set_page_config(page_title='Inicio', layout='wide', initial_sidebar_state='auto')
login.generarLogin(archivo)

if 'usuario' in st.session_state:
    st.header('Página :orange[principal]')
    st.subheader('Información página principal')
    
    # Crear pestañas
    tab1, tab2, tab3 = st.tabs(["Usuarios Registrados", "Gestión de Roles", "Registro de Auditoría"])

    # Sección 1: Usuarios Registrados
    with tab1:
        st.header("👤 Usuarios Registrados")
        
        # Cargar los usuarios
        df_usuarios = cargar_usuarios()

        # Opciones de filtrado
        col1, col2 = st.columns([2, 1])
        with col1:
            filtro_nombre = st.text_input("🔍 Buscar por nombre", "")
        with col2:
            filtro_rol = st.selectbox("📌 Filtrar por rol", ["Todos"] + df_usuarios["rol"].unique().tolist())

        # Filtrar los datos
        df_filtrado = filtrar_usuarios(df_usuarios, filtro_nombre, filtro_rol)
        st.dataframe(df_filtrado.drop(columns=["clave"]), use_container_width=True)

    # Sección 2: Gestión de Roles
    with tab2:
        st.header("🔧 Gestión de Roles")
        df_usuarios = cargar_usuarios()
        
        # Mostrar la tabla de usuarios con roles actuales
        st.subheader("📌 Usuarios y sus Roles")
        st.dataframe(df_usuarios[['nombre', 'rol']], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        # Sección: Crear un nuevo usuario con rol
        with col1:
            st.subheader("➕ Crear Nuevo Usuario")
            usuario= st.text_input("Nombre de Usuario:")
            nuevo_nombre = st.text_input("Nombre Completo:")
            nuevo_rol = st.text_input("Rol del usuario:")
            nueva_clave = st.text_input("Clave del usuario:", type="password")
            
            if st.button("Crear Usuario"):
                if usuario and nuevo_nombre and nuevo_rol and nueva_clave:
                    nuevo_usuario = pd.DataFrame([{"usuario":usuario,"nombre": nuevo_nombre, "rol": nuevo_rol, "clave": nueva_clave}])
                    df_usuarios = pd.concat([df_usuarios, nuevo_usuario], ignore_index=True)
                    guardar_usuarios(df_usuarios)
                    st.success(f"✅ Usuario '{nuevo_nombre}' creado con rol '{nuevo_rol}'")
                    st.rerun()
                else:
                    st.warning("⚠️ Todos los campos son obligatorios.")
        
        # Sección: Editar el rol de un usuario
        with col2:
            st.subheader("📝 Editar Rol de Usuario")
            usuario_seleccionado = st.selectbox("Selecciona un usuario", df_usuarios["nombre"].tolist())
            nuevo_rol_usuario = st.text_input("Nuevo rol para el usuario:")
            
            if st.button("Actualizar Rol"):
                df_usuarios.loc[df_usuarios["nombre"] == usuario_seleccionado, "rol"] = nuevo_rol_usuario
                guardar_usuarios(df_usuarios)
                st.success(f"✅ Rol actualizado para {usuario_seleccionado}")
                st.rerun()
        
        st.markdown("---")
        
        # Sección: Eliminar un usuario
        st.subheader("❌ Eliminar Usuario")
        usuario_a_eliminar = st.selectbox("Selecciona un usuario para eliminar", df_usuarios["nombre"].tolist())
        
        if st.button("Eliminar Usuario"):
            df_usuarios = df_usuarios[df_usuarios["nombre"] != usuario_a_eliminar]
            guardar_usuarios(df_usuarios)
            st.success(f"✅ Usuario '{usuario_a_eliminar}' eliminado correctamente")
            st.rerun()

    # Sección 3: Registro de Auditoría
    with tab3:
        st.header("📜 Registro de Auditoría")

        # Cargar datos de auditoría
        AUDITORIA_CSV = "auditoria.csv"

        @st.cache_data
        def cargar_auditoria():
            try:
                return pd.read_csv(AUDITORIA_CSV)
            except FileNotFoundError:
                return pd.DataFrame(columns=["Usuario", "Acción", "Fecha"])

        def guardar_auditoria(usuario, accion):
            df_auditoria = cargar_auditoria()
            nuevo_registro = pd.DataFrame([[usuario, accion, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]], 
                                        columns=["Usuario", "Acción", "Fecha"])
            df_auditoria = pd.concat([df_auditoria, nuevo_registro], ignore_index=True)
            df_auditoria.to_csv(AUDITORIA_CSV, index=False)

        df_auditoria = cargar_auditoria()

        if not df_auditoria.empty:
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                filtro_usuario = st.selectbox("📌 Filtrar por usuario", ["Todos"] + df_auditoria["Usuario"].unique().tolist())
            with col2:
                filtro_accion = st.selectbox("🔍 Filtrar por acción", ["Todas"] + df_auditoria["Acción"].unique().tolist())

            # Aplicar filtros
            if filtro_usuario != "Todos":
                df_auditoria = df_auditoria[df_auditoria["Usuario"] == filtro_usuario]
            if filtro_accion != "Todas":
                df_auditoria = df_auditoria[df_auditoria["Acción"] == filtro_accion]

            st.dataframe(df_auditoria, use_container_width=True)

            # Descargar historial
            st.download_button("⬇ Descargar Registro", df_auditoria.to_csv(index=False), "registro_auditoria.csv")
        else:
            st.write("📭 No hay registros de auditoría.")

