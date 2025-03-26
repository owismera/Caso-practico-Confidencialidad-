import streamlit as st
import pandas as pd

def validarUsuario(usuario,clave):
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario
    
    Returns:
        bool: True usuario valido, False usuario invalido
    """
    dfusuarios = pd.read_csv('usuarios.csv')
    if len(dfusuarios[(dfusuarios['usuario']==usuario) & (dfusuarios['clave']==clave)])>0:
        return True
    else:
        return False

def generarMenu(usuario): # Genera el menú dependiendo del usuario
    with st.sidebar:
        # Carga la tabla usuarios
        dfusuarios = pd.read_csv('usuarios.csv')
        # Filtremos la tabla de usuarios
        dfusuarios = dfusuarios[(dfusuarios['usuario']==usuario)]
        # Cargamos el nombre del usuario
        nombre = dfusuarios['nombre'].values[0]
        # Cargamos el rol
        rol = dfusuarios['rol'].values[0]
        # Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        st.caption(f"Rol: {rol}") # Mostramos el rol del usuario
        # Mostramos los enlaces de páginas
        st.page_link('inicio.py', label="Inicio", icon="🏠")
        st.subheader("Tableros") # Subtitulo para los tableros
        # Mostramos los enlaces a las páginas según el rol del usuario
        if rol in ['ventas','admin','comercial']:
            st.page_link('pages/pagina1.py', label="Ventas", icon="📋")
        if rol in ['compras','admin','comercial']:
            st.page_link('pages/pagina2.py', label="Compras", icon="📋")
        if rol in ['personal','admin']:
            st.page_link('pages/pagina3.py', label="Personal", icon="📋")
        # Botón para cerrar la sesión
        btnSalir = st.button("Salir")
        if btnSalir:
            st.session_state.clear()
            # Luego de borrar el session state reiniciamos la app para mostrar el login de nuevo
            st.rerun()

# Validación de acceso a la página según los roles del usuario
def validarPagina(pagina,usuario):
    """Valida si el usuario tiene permiso para acceder a la página

    Args:
        pagina (str): página a validar
        usuario (str): usuario a validar

    Returns:
        bool: True si tiene permiso, False si no tiene permiso
    """
    # Cargamos la información de usuarios y roles
    dfusuarios = pd.read_csv('usuarios.csv')
    dfPaginas = pd.read_csv('rol_paginas.csv')
    dfUsuario =dfusuarios[(dfusuarios['usuario']==usuario)]
    rol= dfUsuario['rol'].values[0]
    dfPagina =dfPaginas[(dfPaginas['pagina'].str.contains(pagina))]
    # Validamos si el rol del usuario tiene acceso a la página
    if len(dfPagina)>0:
        if rol in dfPagina['roles'].values[0] or rol == "admin" or st.secrets["tipoPermiso"]=="rol":
            return True # El usuario tiene permiso
        else:
            return False # El usuario no tiene permiso
    else:
        return False # La página no existe en el archivo de permisos

def generarMenuRoles(usuario):
    """Genera el menú dependiendo del usuario y el rol asociado a la página

    Args:
        usuario (str): usuario utilizado para generar el menú
    """        
    with st.sidebar: # Menú lateral
        # Cargamos la tabla de usuarios y páginas
        dfusuarios = pd.read_csv('usuarios.csv')
        dfPaginas = pd.read_csv('rol_paginas.csv')
        # Filtramos la tabla de usuarios por el usuario actual
        dfUsuario =dfusuarios[(dfusuarios['usuario']==usuario)]
        # Obtenemos el nombre y rol del usuario
        nombre= dfUsuario['nombre'].values[0]
        rol= dfUsuario['rol'].values[0]
     
        #Mostramos el nombre del usuario
        st.write(f"Hola **:blue-background[{nombre}]** ")
        st.caption(f"Rol: {rol}")
        # Mostramos los enlaces de páginas        
        st.subheader("Opciones")
        # Verificamos si se deben ocultar o deshabilitar las opciones del menú
        if st.secrets["ocultarOpciones"]=="True": # Verificamos el valor del secreto "ocultarOpciones"
            if rol!='admin': # Si el rol no es admin
                # Filtramos la tabla de páginas por el rol actual
                dfPaginas = dfPaginas[dfPaginas['roles'].str.contains(rol)]                   
            # Ocultamos las páginas que no tiene permiso
            for index, row in dfPaginas.iterrows():
                icono=row['icono']            
                st.page_link(row['pagina'], label=row['nombre'], icon=f":material/{icono}:")  # Mostramos la página  
        else: # Si no se ocultan las opciones
            # Deshabilitamo las páginas que no tiene permiso            
            for index, row in dfPaginas.iterrows():
                deshabilitarOpcion = True  # Valor por defecto para deshabilitar las opciones
                if rol in row["roles"] or rol == "admin": # Verificamos el rol
                    deshabilitarOpcion = False # Habilitamos la página si el usuario tiene permiso
                
                icono=row['icono']            
                # Mostramos el enlace de la página, deshabilitado o no según el permiso.
                st.page_link(row['pagina'], label=row['nombre'], icon=f":material/{icono}:",disabled=deshabilitarOpcion)         
        # Botón para cerrar la sesión
        btnSalir=st.button("Salir")
        if btnSalir:
            st.session_state.clear()
            st.rerun()

def generarLogin(archivo):
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state: # Verificamos si la variable usuario esta en el session state
        
        # Si ya hay usuario cargamos el menu
        if st.secrets["tipoPermiso"]=="rolpagina":
            generarMenuRoles(st.session_state['usuario']) # Generamos el menú para la página
        else:
            generarMenu(st.session_state['usuario']) # Generamos el menú del usuario       
        if validarPagina(archivo,st.session_state['usuario'])==False: # Si el usuario existe, verificamos la página        
            st.error(f"No tiene permisos para acceder a esta página {archivo}",icon=":material/gpp_maybe:")
            st.stop() # Detenemos la ejecución de la página
    else: # Si no hay usuario
        # Inicializamos session_state para controlar la navegación
        if 'pagina' not in st.session_state:
            st.session_state['pagina'] = 'login'

        # Función para cambiar de página
        def cambiar_pagina(pagina):
            st.session_state['pagina'] = pagina

        # Lógica de navegación
        if st.session_state['pagina'] == 'login':
            st.title("Login")
            
            with st.form('frmLogin'): # Creamos un formulario de login
                parUsuario = st.text_input('Usuario') # Creamos un campo de texto para usuario
                parPassword = st.text_input('Password',type='password') # Creamos un campo para la clave de tipo password
                col1, col2, col3 = st.columns(3)  # Divide el espacio en 3 columnas

                with col1:
                    btnLogin = st.form_submit_button('Ingresar', type='primary')

                with col2:
                    btnRecuperar = st.form_submit_button('Recuperar contraseña', type='primary')

                with col3:
                    btnCambiar = st.form_submit_button('Cambiar contraseña', type='primary')
                
                if btnLogin: # Verificamos si se presiono el boton ingresar
                    if validarUsuario(parUsuario,parPassword): # Verificamos si el usuario y la clave existen
                        st.session_state['usuario'] =parUsuario # Asignamos la variable de usuario
                        # Set a cookie
                        # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                        st.rerun() # Reiniciamos la aplicación
                    else:
                        # Si el usuario es invalido, mostramos el mensaje de error
                        st.error("Usuario o clave inválidos", icon="⛔")

                if btnRecuperar:
                    cambiar_pagina("recuperar")

                if btnCambiar:
                    cambiar_pagina("cambiar")

        elif st.session_state['pagina'] == "recuperar":
            st.title("Recuperar Contraseña")
            with st.form("frmRecuperar"):
                email = st.text_input("Correo electrónico")
                btnEnviar = st.form_submit_button("Enviar enlace de recuperación")

                if btnEnviar:
                    st.success("Se ha enviado un enlace a tu correo")

            st.button("Volver", on_click=lambda: cambiar_pagina("login"))

        elif st.session_state['pagina'] == "cambiar":
            st.title("Cambiar Contraseña")
            with st.form("frmCambiar"):
                nueva_password = st.text_input("Nueva Contraseña", type="password")
                confirmar_password = st.text_input("Confirmar Contraseña", type="password")
                btnGuardar = st.form_submit_button("Guardar")

                if btnGuardar:
                    if nueva_password == confirmar_password:
                        st.success("Contraseña actualizada con éxito")
                    else:
                        st.error("Las contraseñas no coinciden")

            st.button("Volver", on_click=lambda: cambiar_pagina("login"))