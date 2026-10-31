import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

## ----- CONFIGURACION DE LA PAGINA -----
st.set_page_config(page_title="Dashboard Tienda Electronica", layout = "wide")
st.title("📈 Dashboard Tienda Electronica")
st.markdown("Visualizaciones organizadas verticalmente.")

#------ CARGAR DATOS DESDE EL CSV ------
df = pd.read_csv('ventas_limpias.csv')


#CAMBIAR EL FORMATO DE OBJT A DATETIME
df['Fecha'] = pd.to_datetime(df['Fecha'])

# Obtener la semana ( 1,2,3, 4)
df['Semana'] = df['Fecha'].dt.isocalendar().week

#Mostrar el datframe completo en el dashboard

sns.set_theme(style="whitegrid")
with st.expander("Ver base de Datos Completa"):
    st.dataframe(df, use_container_width= True)

## --- Crear las pestañas para cada sección ------

tab1, tab2, tab3 = st.tabs(["Resumen Financiero","Tendencias","Productos"])

with tab1:
    ingresos_cat = df.groupby('Categoria')['Subtotal'].sum().reset_index().sort_values(by = 'Subtotal',ascending = False)
    st.subheader("Ingresos por Categoría")
    fig1, ax1 = plt.subplots(figsize = (8,4))
    sns.barplot(ingresos_cat,x = 'Categoria',y = 'Subtotal',palette = 'viridis',ax = ax1)
    st.pyplot(fig1)

    st.divider()

    st.subheader("Distribución de Ingresos (%)")

    fig2,ax2 = plt.subplots(figsize = (5,5))
    secciones, textos,porcentajes = ax2.pie(ingresos_cat['Subtotal'],
                                            labels = ingresos_cat['Categoria'],
                                            autopct = '%1.1f%%',startangle= 90,
                                            colors = sns.color_palette('pastel'),
                                            textprops= {'fontsize': 7})
    #inclinamos las etiquetas 45 grados
    for texto in textos:
        texto.set_rotation(20)

    for numero in porcentajes:
        numero.set_rotation(45)

    st.pyplot(fig2)

with tab2:
    st.subheader("Ingresos diarios Area Computo")
    df_computo = df[df['Categoria'] == 'Computo']
    ventas_por_dia_computo = df_computo.groupby('Fecha')['Subtotal'].sum().reset_index()
    fig3, ax3 = plt.subplots(figsize = (8,4))
    sns.barplot(data = ventas_por_dia_computo, x = 'Fecha', y = 'Subtotal', color = 'darkorange')
    plt.xticks(rotation= 90)
    st.pyplot(fig3)

    st.divider()

    st.subheader("Ingresos diarios por Categoria")
    st.write("Explora la tendencia de ventas diarias.")
    ventas_por_dia =  df.groupby(['Fecha','Categoria'])['Subtotal'].sum().reset_index()

    datos_grafica = ventas_por_dia.pivot_table(
        index = 'Fecha',
        columns = 'Categoria',
        values = 'Subtotal',
        aggfunc= 'sum'
    ).fillna(0)

    st.bar_chart(datos_grafica)

    st.divider()

    st.subheader("Comparador Dinámico de Ventas")
    
    #1Extraer la i nformacion en un widget interactivo
    categorias = df['Categoria'].unique()
    categorias_seleccionadas = st.multiselect(
        "Selecciona las categorías que deseas comparar:",
        options = categorias,
        default = categorias[:1] # categoria por default
    )

    #2. Filtramos el dataframe segun lo que el usuario eligio
    df_filtrado = df[df['Categoria'].isin(categorias_seleccionadas)]

    #verificar que el usario no haya borrado todas las opciones
    if not df_filtrado.empty:
        datos_grafica2 = df_filtrado.pivot_table(
            index = 'Fecha',
            columns = 'Categoria',
            values = 'Subtotal',
            aggfunc= 'sum'
        ).fillna(0) # si en un dia no se vendio alguna categoria, rellene con cer0

        st.line_chart(datos_grafica2)
    else:
        st.info("👆 por favor, selecciona al menos una categoría en el filtro de arriba.")

with tab3:
    st.subheader("Top Productos más vendidos por semana.")
    #1. obtener semanas
    semanas = sorted(df['Semana'].unique())
    semana_seleccionada = st.selectbox(
        "Selecciona la semana que deseas analizar:",
        options = semanas
    )

    #2. filtrar del dataFrame para usar solo los datos de esa semana
    df_semana = df[df['Semana'] == semana_seleccionada]

    #3. Agrupar por producto y sumar la cantidad vendida
    productos_semana = df_semana.groupby('Producto')['Cantidad'].sum().reset_index()
    #4. ordenar de mayor a menor y guardamos el top 5.
    top_productos_semana = productos_semana.sort_values(by= 'Cantidad',ascending= False).head(5)

    #5 Dibujamos la grafica se Streamlit
    if not top_productos_semana.empty:
        st.bar_chart(
            data = top_productos_semana,
            x = 'Producto',
            y = 'Cantidad',
            color = "#784BFF"
        )
    else:
        st.info("No hay ventas registradas para esa semana.")


