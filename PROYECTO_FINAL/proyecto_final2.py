import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt


st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title="Las llamas", layout="centered")

df = pd.read_csv("datos.csv")

st.image ('https://efeverde.com/wp-content/uploads/2022/01/9ed7202cfdb80c7bf99a843bc9d5fecd561d99b8-scaled-3.jpg')

st.title('Ardiendo en Datos: Un Análisis Profundo de los Incendios Forestales.')
st.write('Vamos a analizar y representar datos sobre los incendios forestales registrados entre el 2000 - 2015 recogidos por el Ministerio para la Transición Ecológica y el Reto Demográfico.')

#---------------------------------------FUNCIONES Y DATOS CON LOS QUE TRABAJAREMOS----------------------------------------------------------

#SUPERFICIE QUEMADA
superficie_quemada_por_comunidad = df.groupby(['idcomunidad'])['superficie'].sum().reset_index(name='superficie_quemada')
superficie_quemada_por_anio_y_comunidad = df.groupby(['año', 'idcomunidad'])['superficie'].sum().reset_index(name='superficie_quemada')

df_incendios_ordenados = df.sort_values(by=['superficie'], ascending=False)

# obtener los 10 primeros incendios de la lista resultante
los_10_mas_grandes = df_incendios_ordenados.head(10)

#---------------------------------------FUNCIONES Y DATOS CON LOS QUE TRABAJAREMOS----------------------------------------------------------


#---------------------------------------FUNCIONES Y DATOS CON LOS QUE TRABAJAREMOS----------------------------------------------------------


def arima_prediction(data, date_col, value_col, order=(1,1,1), start=None, end=None, future_periods=12):
    
    # Convertir la columna de fechas a datetime
    data[date_col] = pd.to_datetime(data[date_col])
    
    # Establecer la columna de fechas como índice
    data = data.set_index(date_col)
    
    # Seleccionar los datos de entrenamiento y de prueba
    train_data = data.loc[start:end, value_col]
    test_data = data.loc[end:, value_col]
    
    # Entrenar el modelo ARIMA
    model = ARIMA(train_data, order=order)
    model_fit = model.fit()
    
    # Realizar la predicción
    predictions = model_fit.predict(start=start, end=end, typ='levels')
    future_predictions = model_fit.forecast(steps=future_periods)[0]
    
    # Crear un gráfico de la serie temporal original y la predicción
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(data.index, data[value_col], label='Observados')
    ax.plot(predictions.index, predictions, label='Predicción')
    ax.plot(future_predictions.index, future_predictions, label='Predicción futura')
    ax.legend()
    ax.set_title('ARIMA Predicción')
    ax.set_xlabel(date_col)
    ax.set_ylabel(value_col)
    
    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)
    
    # Devolver las predicciones futuras
    return future_predictions




tabs = st.tabs(["Dataset del Ministerio", "Datos generales", "Datos de Comunidades Autónomas"])

with tabs[0]:
    st.write(df)

with tabs[1]:
    st.write(f'Contamos con un total de {len(df)} incendios registrados en España entre el 2000 y el 2015. Fuente: Ministerio para la Transición Ecológica y el Reto Demográfico.')
    
    fig = px.imshow(df.corr(method='pearson'), template="plotly_dark")
    st.plotly_chart(fig)

    st.write('-------------------------------')

    incendios_por_anio = df.groupby('año')['id'].count().reset_index(name='cantidad_incendios')
    fig = px.bar(incendios_por_anio, x='año', y='cantidad_incendios', title='Cantidad de incendios por año')
    st.plotly_chart(fig)

    # Calcular la media de incendios por año
    df['fecha'] = pd.to_datetime(df['fecha'])

    # Obtener la media de incendios por año
    media_incendios = df.groupby(df['fecha'].dt.year)['id'].count().mean()

    # Mostrar resultado en streamlit
    st.write(f"La media de incendios por año es de: {media_incendios:.2f}")

    st.write('-------------------------------')

    superficie_quemada_por_año = df.groupby('año')['superficie'].sum().reset_index()
    fig = px.bar(superficie_quemada_por_año, x='año', y='superficie', template='plotly_dark', labels={'año': 'Año', 'superficie': 'Superficie quemada (ha)'}, title='Superficie quemada por año')
    st.plotly_chart(fig)

    media_superficie = df.groupby(df['fecha'].dt.year)['superficie'].sum().mean()

    # Mostrar resultado en streamlit
    st.write(f"La media de superficie quemada por año es de: {media_superficie:.2f} ha")

    st.write('-------------------------------')
    # Crear diccionario de causas
    causas_dict = {1: 'Fuego por rayo', 2: 'Fuego por accidente o negligencia', 
                3: 'Fuego por accidente o negligencia', 4: 'Fuego intencionado', 
                5: 'Fuego por causa desconocida', 6: 'Incendio reproducido'}

    # Contar cantidad de incendios por causa
    counts = df['causa'].value_counts()

    df['causa'] = df['causa'].replace(3, 2)

    # Contar frecuencia de causas
    causa_counts = df['causa'].value_counts()

    # Crear gráfico de barras
    fig = px.bar(x=causa_counts.index.map(causas_dict), y=causa_counts.values, labels={'x': 'Causa', 'y': 'Cantidad'})
    fig.update_layout(title='Cantidad de Incendios según la causa', xaxis_type='category')
    st.plotly_chart(fig)

    st.write('-------------------------------')

    df_grouped = df.groupby('año').agg({'gastos': 'sum', 'perdidas': 'sum'}).reset_index()
    fig = px.bar(df_grouped, x='año', y=['gastos', 'perdidas'], barmode='group', title='Comparación de gastos y pérdidas totales por año')
    st.plotly_chart(fig)

    media_gastos = df.groupby(df['fecha'].dt.year)['gastos'].sum().mean() / 10**6
    st.write(f"La media de gastos económicos por año es de: {media_gastos:.2f} millones de €")

    media_perdidas = df.groupby(df['fecha'].dt.year)['perdidas'].sum().mean() / 10**6
    st.write(f"La media de pérdidas económicas por año es de: {media_perdidas:.2f} millones de €")

    st.write('-------------------------------')

    df['fecha'] = pd.to_datetime(df['fecha'])

    # Usa la función value_counts() para contar la frecuencia de cada mes y ordénalos por índice
    month_counts = df['fecha'].dt.month.value_counts().sort_index()

    # Muestra los meses más comunes en una gráfica de barras
    fig = px.bar(x=month_counts.index, y=month_counts.values, labels={'x': 'Mes', 'y': 'Frecuencia'})
    st.plotly_chart(fig)

    media_incendios_mes = df.groupby(df['fecha'].dt.month)['id'].count().mean()
    st.write(f"La media de incendios por mes es de: {media_incendios_mes:.2f}")

    st.write('-------------------------------')

    df_sum = df.groupby("año").sum()

    # Crea el gráfico de barras
    fig = px.bar(df_sum, x=df_sum.index, y=["muertos", "heridos"], barmode="group", color_discrete_sequence=["red", "blue"])
    fig.update_layout(title="Comparativa de muertos y heridos por año", xaxis_title="Año", yaxis_title="Número de personas")

    # Muestra el gráfico en Streamlit
    st.plotly_chart(fig)

    st.write('-------------------------------')

    df_grouped2 = df.groupby('año')[['time_ext', 'time_ctrl']].mean().reset_index()

    # crear la figura con pyplot express
    fig = px.line(df_grouped2, x='año', y=['time_ext', 'time_ctrl'], 
                title='Comparación de tiempo medio total por año de extinción contra el de control')

    # Muestra la gráfica en Streamlit
    st.plotly_chart(fig)

    df_scatter = df.groupby('año').agg({'superficie': 'count', 'medios': 'mean'}).reset_index()

    # Crear la figura con px.scatter
    fig = px.scatter(df_scatter, x='superficie', y='medios', color='año', trendline='lowess', template="plotly_dark",
                 labels={'superficie': 'Cantidad de incendios'})

    # Mostrar la figura
    st.plotly_chart(fig)

    st.write('-------------------------------')

    fig = px.scatter(df, x="año", y="superficie", color="causa_supuesta", template="plotly_dark")

    st.plotly_chart(fig)

    fig = px.pie(df, values='superficie', names='causa_supuesta', title='Distribución de la superficie quemada por causa supuesta')
    st.plotly_chart(fig)

    st.write('-------------------------------')

    df['fecha'] = pd.to_datetime(df['fecha'])

    # Renombrar las causas duplicadas
    df['causa'] = df['causa'].replace({3: 2})

    # Crear una tabla de contingencia de la cantidad de incendios por año y por causa
    table = pd.crosstab(df['fecha'].dt.year, df['causa'])

    # Renombrar las causas con el diccionario causas_dict
    table = table.rename(columns=causas_dict)

    # Graficar la serie temporal
    fig = px.line(table, x=table.index, y=table.columns)

    # Personalizar el diseño de la gráfica
    fig.update_layout(
        title="Tendencia de la causa de los incendios forestales a lo largo de los años",
        xaxis_title="Año",
        yaxis_title="Cantidad de incendios",
        legend_title="Causa",
        font=dict(
            family="Arial",
            size=14,
            color="#7f7f7f"
        )
    )

    # Mostrar la gráfica
    st.plotly_chart(fig)


with tabs[2]:
    st.header("Datos generales por CCAA") 
    st.write('-------------------------------')
    
    fig = px.bar(superficie_quemada_por_anio_y_comunidad, x='año', y='superficie_quemada', color='idcomunidad',
             title='Superficie quemada por año y por comunidad autónoma', template='plotly_dark')
    st.plotly_chart(fig)

    fig = px.bar(superficie_quemada_por_anio_y_comunidad, x="año", y="superficie_quemada", color="idcomunidad", barmode="group", title="Superficie quemada por año y por comunidad autónoma")
    st.plotly_chart(fig)

    st.write('-------------------------------')
    st.write('MAPA')

    st.write("Este mapa muestra la ubicación y tamaño de los incendios forestales ocurridos en España entre 2000 y 2015.")

    # Crear el density mapbox
    fig = px.density_mapbox(df, lat='lat', lon='lng', z='superficie', radius=10, zoom=5, animation_frame='año', mapbox_style='carto-positron')
    fig.update_layout(mapbox_style="stamen-toner",
                  mapbox_center_lon=-4,
                  mapbox_center_lat=40,
                  mapbox_zoom=4,
                  width=800) # set the width of the plot to 800 pixels
    st.plotly_chart(fig)


    fig = px.density_mapbox(df, lat='lat', lon='lng', radius=10,
                         center=dict(lat=40, lon=-4),
                         zoom=4, mapbox_style="stamen-terrain", template='plotly_dark',
                         color_continuous_scale='ylorrd', hover_name='municipio', hover_data=['fecha'])
    
    st.plotly_chart(fig)


    st.write('-------------------------------')

    st.write('Informacion sobre los 10 incendios mas grandes que han sucedido en España')
    los_10_mas_grandes

    # Agrupar los datos por idcomunidad y municipio, y calcular la suma de superficie y el número de incendios en cada grupo
    df_municipios = df.groupby(['idcomunidad', 'municipio']).agg({'superficie': 'sum', 'id': 'count'}).reset_index()

    # Ordenar los resultados por el número de incendios en orden descendente y tomar los primeros 10 registros
    top_municipios = df_municipios.sort_values('id', ascending=False).head(10)

    # Mostrar los resultados en Streamlit
    st.write('Los 10 municipios con más incendios son:')
    st.write(top_municipios[['idcomunidad', 'municipio', 'id', 'superficie']])


    st.write('-------------------------------')

    df['perdidas_millones'] = df['perdidas'] / 1000000

    # Calcular las pérdidas totales por comunidad autónoma
    perdidas_por_ca = df.groupby('idcomunidad')['perdidas_millones'].sum().reset_index()

    # Crear la gráfica de barras horizontales con Pyplot Express
    fig = px.bar(perdidas_por_ca, x='perdidas_millones', y='idcomunidad', orientation='h', 
                title='Pérdidas económicas por comunidad autónoma')
    fig.update_traces(marker_color='#FF5733')
    fig.update_layout(xaxis_title='Pérdidas económicas (millones de euros)', yaxis_title='Comunidad Autónoma')
    st.plotly_chart(fig)

    # Agrupa y suma los medios por comunidad autónoma
    medios_por_comunidad = df.groupby('idcomunidad')['medios'].agg('sum').reset_index()

    # Crea la gráfica con plotly express
    fig = px.bar(medios_por_comunidad, x='idcomunidad', y='medios')
    st.plotly_chart(fig)


    