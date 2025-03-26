import streamlit as st

def generarMenu():
    with st.sidebar:
        st.page_link('appPrincipal.py', label="Inicio", icon="🏠")
        st.page_link('pages/pagina1.py', label="Pagina 1", icon="📋")
        st.page_link('pages/pagina2.py', label="Pagina 1", icon="📋")