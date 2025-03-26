import streamlit as st
import login

archivo = __file__.split("\\")[-1]
login.generarLogin(archivo)
if 'usuario' in st.session_state:
    st.header('Página :orange[principal]')
    st.subheader('Información página principal')