#----------------------------------------------LIBRERIAS----------------------------------------------------------------------
import streamlit as st
import plotly.graph_objs as go
from PIL import Image
import matplotlib.pyplot as plt
import tkinter
import numpy as np
import pandas as pd
import seaborn as sns #primero importar las librerias que vamos a en nuestra app 
import os
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import FastMarkerCluster
import geopandas as gpd
from branca.colormap import LinearColormap

st.set_option('deprecation.showPyplotGlobalUse', False)
#----------------------------------------------CONFIGURACIÓN DE PÁGINA ----------------------------------------------------------------------

st.set_page_config(page_title="Bienvenidos a Madrid", layout="centered") # después establecer el título de página, su layout e icono 

#---------------------------------------------- COSAS QUE PODEMOS USAR EN TODA NUESTRA APP----------------------------------------------------------------------
airbnb  = pd.read_csv("airbnb_anuncios.csv")
airbnb = airbnb.drop(['name','id','host_name', 'last_review'], axis=1)
airbnb['reviews_per_month'].fillna(0, inplace=True)
airbnb = airbnb.dropna(axis=0)
#---------------------------------------FUNCIONES Y DATOS CON LOS QUE TRABAJAREMOS----------------------------------------------------------

#BAARIOS DE MADRID
def obten_unicos(barrios):
    unicos = []
    for barrio in barrios:
        if barrio not in unicos:
            unicos.append(barrio)
    return len(unicos)


#PRECIO
airbnb['price'] = pd.to_numeric(airbnb['price'], errors='coerce')
precio_media=airbnb.groupby('neighbourhood_group')['price'].mean()
precio_total = airbnb['price'].mean()
precio_rango = airbnb.groupby('neighbourhood_group')['price'].agg(['min', 'max'])
min_value=airbnb["price"].min()
max_value=airbnb["price"].max()

#ALOJAMIENTOS
home = airbnb[airbnb['room_type'] == "Entire home/apt"]
host_homeTOP = home.groupby(['host_id']).size().reset_index(name='Entire home/apt').sort_values(by=['Entire home/apt'], ascending=False).head(10)
host_homeBOT = home.groupby(['host_id']).size().reset_index(name='Entire home/apt').sort_values(by=['Entire home/apt'], ascending=True).head(10)

hosts = pd.concat([host_homeTOP, host_homeBOT])
resultHome = airbnb[airbnb['host_id'].isin(hosts['host_id'])]
resultHome["text"] = resultHome["host_id"]

#---------------------------------------------------------------------------

private = airbnb[airbnb['room_type'] == "Private room"]
host_privateTOP = private.groupby(['host_id']).size().reset_index(name='Private room').sort_values(by=['Private room'], ascending=False).head(10)
host_privateBOT = private.groupby(['host_id']).size().reset_index(name='Private room').sort_values(by=['Private room'], ascending=True).head(10)

hosts1 = pd.concat([host_privateTOP, host_privateBOT])
resultPrivate= airbnb[airbnb['host_id'].isin(hosts1['host_id'])]
resultPrivate["text"] = resultPrivate["host_id"]

#---------------------------------------------------------------------------

shared = airbnb[airbnb['room_type'] == "Shared room"]
host_sharedTOP = shared.groupby(['host_id']).size().reset_index(name='Shared room').sort_values(by=['Shared room'], ascending=False).head(10)
host_sharedBOT = shared.groupby(['host_id']).size().reset_index(name='Shared room').sort_values(by=['Shared room'], ascending=True).head(10)

hosts2 = pd.concat([host_sharedTOP, host_sharedBOT])
resultShared= airbnb[airbnb['host_id'].isin(hosts2['host_id'])]
resultShared["text"] = resultShared["host_id"]

#---------------------------------------------------------------------------

hotel = airbnb[airbnb['room_type'] == "Hotel room"]
host_HotelTOP = hotel.groupby(['host_id']).size().reset_index(name='Hotel room').sort_values(by=['Hotel room'], ascending=False).head(10)
host_HotelBOT = hotel.groupby(['host_id']).size().reset_index(name='Hotel room').sort_values(by=['Hotel room'], ascending=True).head(10)

hosts3 = pd.concat([host_HotelTOP, host_HotelBOT])
resultHotel= airbnb[airbnb['host_id'].isin(hosts3['host_id'])]
resultHotel["text"] = resultHotel["host_id"]

#---------------------------------------------------------------------------

top_hosts = pd.DataFrame(columns=["host_id"])
top_hosts = top_hosts.append(host_homeTOP[["host_id"]])
top_hosts = top_hosts.append(host_privateTOP[["host_id"]])
top_hosts = top_hosts.append(host_sharedTOP[["host_id"]])
top_hosts = top_hosts.drop_duplicates()

top_hosts_count = airbnb.groupby(["host_id"]).size().reset_index(name='Count of listings')
top_hosts_count = top_hosts_count.sort_values(by=['Count of listings'], ascending=False)
top_hosts_count = top_hosts_count[top_hosts_count['host_id'].isin(top_hosts['host_id'])]

#--------------------------------------------------------------------------------
# Calcular el total de alojamientos
total_listings = airbnb.shape[0]

# Agrupar los alojamientos por host_id y contar el número de alojamientos por host_id
host_count = airbnb.groupby(["host_id"]).size().reset_index(name='Count of listings')

# Ordenar de forma descendente el número de alojamientos
host_count = host_count.sort_values(by=['Count of listings'], ascending=False)

# Seleccionar el top 1% de los host_ids con más alojamientos
top_hosts = host_count.head(int(host_count.shape[0]*0.01))

# Sumar el número de alojamientos de los host_ids seleccionados
top_hosts_listings = top_hosts['Count of listings'].sum()

# Calcular el porcentaje de alojamientos que tiene el top 1% de los host_ids con más alojamientos
percentage = (top_hosts_listings / total_listings) * 100

#print("El top 1% de los host_ids con más alojamientos tiene un total de {} alojamientos, lo que representa un {:.2f}% del total de alojamientos.".format(top_hosts_listings, percentage))

#--------------------------------------------------------------------------------


#---------------------------------------------- EMPIEZA LA APP ----------------------------------------------------------------------


st.image ('https://estaticos.esmadrid.com/cdn/farfuture/BWcvMivTxTmm5LYOUGDmKVLY-o-P8m3C07xjIpbc3b8/mtime:1646730209/sites/default/files/styles/content_type_full/public/widgets/items/images/la_gran_via.jpg?itok=LbHN7qFI') # llamado a imágenes

st.title('Airbnb en datos.') #st.title nos va a permitir mandar un titulo

st.write('Vamos a analizar y representar datos sobre los alojamientos en la plataforma de Airbnb en la ciudad de Madrid')


#---------------------------------------------- TABLAS QUE COMPONENEN LA APP ----------------------------------------------------------------------

tabs = st.tabs(["Datos generales del airbnb", "Datos generales", "Datos de distritos y barrios", "Datos"]) # establecer tabs

tab_plots= tabs[0] #nombres de cada tab, recordar que nuestra primera tab, es la posición cero para python
with tab_plots: # utilizar "with" como "context manager" lo que va a permitir insertar lo que queramos 
    st.write(airbnb) # lo que queremos insertar
   
    
tab_plots= tabs[1] #segunda tab siempre sería tabs[1] 
with tab_plots:

    st.write('Contamos con un total de {} anuncios, repartidos en {} distritos y {} barrios. '.format(airbnb['neighbourhood_group'].value_counts().sum(),obten_unicos(airbnb['neighbourhood_group']),obten_unicos(airbnb['neighbourhood'])))  
    px.set_mapbox_access_token(open(".mapbox_token").read())
    fig1=px.scatter_mapbox(data_frame=airbnb, lat=airbnb['latitude'], lon=airbnb['longitude'],color=airbnb['neighbourhood_group'],template="plotly_white", hover_name="neighbourhood",  center=dict(lat=40.416729, lon=-3.703339), size_max=15, zoom=10)
    st.plotly_chart(fig1)

    sns.countplot(y=airbnb['neighbourhood_group'])
    st.pyplot()

    fig2=px.pie(data_frame=airbnb, values=airbnb['host_id'],names=airbnb['neighbourhood_group'],template="plotly_white",  title="Distribucion de alojamientos por barrios")
    st.plotly_chart(fig2, theme="streamlit", use_container_width=True)


tab_plots= tabs[2] #tercera tab 
with tab_plots:      
    st.header("Datos generales") 
    st.write('-------------------------------')

    fig4=px.histogram(data_frame=airbnb, x='neighbourhood_group',  title="Alojamientos y su distribucion por distritos")
    st.plotly_chart(fig4, theme=None, use_container_width=True)

    fig4=px.histogram(data_frame=airbnb, x='neighbourhood', color='neighbourhood_group', title="Alojamientos y su distribucion por barrios")
    st.plotly_chart(fig4, theme=None, use_container_width=True)

    fig4=px.histogram(data_frame=airbnb, color=airbnb['room_type'],x='neighbourhood_group',  title="Tipos de alojamientos y su distribucion por distritos")
    st.plotly_chart(fig4, theme=None, use_container_width=True)



    st.write('-------------------------------')

    # agrupar datos por distrito y barrio
    grouped_data = airbnb.groupby(['neighbourhood_group', 'neighbourhood']).count()['number_of_reviews']
    reviews_por_neighbourhood = airbnb.groupby("neighbourhood").sum()["number_of_reviews"]
    reviews_by_group = airbnb.groupby('neighbourhood_group')['number_of_reviews'].sum()

    fig1234 = px.bar(reviews_by_group, x=reviews_by_group.index, y='number_of_reviews', labels={'neighbourhood_group':'Neighbourhood Group', 'number_of_reviews':'Number of Reviews'}, title='Number of Reviews by Neighbourhood Group')
   
    st.plotly_chart(fig1234)

    grouped_data_by_neighbourhood = airbnb.groupby(['neighbourhood']).sum()['number_of_reviews']
    merged_data = pd.merge(grouped_data.reset_index(), grouped_data_by_neighbourhood.reset_index(), on='neighbourhood')

    fig1235=px.bar(merged_data, x='neighbourhood', y=['number_of_reviews_x','number_of_reviews_y'], color='neighbourhood_group', 
                    title='Numero de reviews por barrio y distrito', 
                    labels={'number_of_reviews_x':'Numero de reviews por distrito', 'number_of_reviews_y':'Numero de reviews por barrio'})
    
    st.plotly_chart(fig1235)

    st.write('-------------------------------')
    # Box plot
    box_plot = px.box(airbnb, x='neighbourhood_group', y='price', title='Rango de precios por neighbourhood_group')
    st.plotly_chart(box_plot)

    st.write('-------------------------------')
    fig19 = px.box(airbnb, x='neighbourhood_group', y='price')
    fig19.add_scatter(x=precio_media.index, y=precio_media.values, mode='lines+markers', name='Precio medio por neighbourhood')
    fig19.add_scatter(x=['Total'], y=[precio_total], mode='lines+markers', name='Precio medio total')
    st.plotly_chart(fig19)

tab_plots= tabs[3] #tercera tab 
with tab_plots:
    st.header('BARRIOS') 
    st.write('-------------------------------')
    st.write('Hay un total de {} anfitriones en Madrid y como hemos mencionado anteriormente tambien hay un total de {} alojamientos' .format(len(airbnb['host_id'].value_counts()),airbnb['neighbourhood_group'].value_counts().sum()))
    st.write('Vamos a analizar los tipos de alojamientos que hay:')
    st.write('ALOJAMIENTOS ENTEROS: {}, lo que supone el {:.2f}% de los alojamientos' .format(home.value_counts().sum(),(home.value_counts().sum()/airbnb['neighbourhood_group'].value_counts().sum()*100)))
    st.write('HABITACIONES PRIVADAS: {}, lo que supone el {:.2f}% de los alojamientos' .format(private.value_counts().sum(),(private.value_counts().sum()/airbnb['neighbourhood_group'].value_counts().sum()*100)))
    st.write('HABITACIONES DE HOTEL: {}, lo que supone el {:.2f}% de los alojamientos' .format(hotel.value_counts().sum(),(hotel.value_counts().sum()/airbnb['neighbourhood_group'].value_counts().sum()*100)))
    st.write('HABITACIONES COMPARTIDAS: {}, lo que supone el {:.2f}% de los alojamientos' .format(shared.value_counts().sum(),(shared.value_counts().sum()/airbnb['neighbourhood_group'].value_counts().sum()*100)))
   
    fig5=px.pie(data_frame=airbnb, names=airbnb['room_type'], title="Porcentaje de distribucion de los diferentes alojamientos")
    st.plotly_chart(fig5, theme=None, use_container_width=True)
    st.write('Como podemos observar predomina el alquiler de alojamientos enteros y habitaciones privadas frente a los hoteles y habitaciones compartidas')
   
    st.write('-------------------------------')
    st.header('ALOJAMIENTOS ENTEROS')

    # Seleccionar los top 10 host_ids de alojamientos enteros
    host_home = home.groupby(['host_id']).size()
    top_host_home = host_home.sort_values(ascending=False).head(int(len(host_home)*0.01))
    total_top_host_home = top_host_home.sum()
    total_home = host_home.sum()
    porcentaje = total_top_host_home/total_home*100

    labels = ['1% host', 'Otros']
    values = [porcentaje, 100-porcentaje]

    fig15 = px.pie(values=values, names=labels,title='Porcentaje de casas de los 1% host mas recurrentes')
    st.write(fig15)

    st.write('ALOJAMIENTOS ENTEROS: {} alojamientos estan a manos de 10 personas y/o empresas, lo que supone el {:.2f}% de los alojamientos' .format(host_homeTOP['Entire home/apt'].head(10).sum(),(host_homeTOP['Entire home/apt'].head(10).sum()/home.value_counts().sum()*100)))
    
    fig10=px.scatter_mapbox(resultHome, lat="latitude", lon="longitude",
                  color="host_id", color_continuous_scale=px.colors.sequential.Plasma,
                zoom=10, hover_name='price', opacity=0.5)
    
    fig10.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig10)

    st.write('-------------------------------')
    st.header('HABITACIONES PRIVADAS')

    st.write('HABITACIONES PRIVADAS: {} alojamientos estan a manos de 10 personas y/o empresas, lo que supone el {:.2f}% de los alojamientos enteros' .format(host_privateTOP['Private room'].head(10).sum(),(host_privateTOP['Private room'].head(10).sum()/private.value_counts().sum()*100)))
    
    host_private = private.groupby(['host_id']).size()
    top_host_private = host_private.sort_values(ascending=False).head(int(len(host_private)*0.01))
    total_top_host_private = top_host_private.sum()
    total_private = host_private.sum()
    porcentaje = total_top_host_private/total_private*100

    labels = ['1% host', 'Otros']
    values = [porcentaje, 100-porcentaje]

    fig16 = px.pie(values=values, names=labels,title='Porcentaje de habitaciones privadas de los 1% host mas recurrentes')
    st.write(fig16)


    fig11=px.scatter_mapbox(resultPrivate, lat="latitude", lon="longitude",
                  color="host_id", color_continuous_scale=px.colors.sequential.Plasma,
                zoom=10, hover_name='price', opacity=0.5)
    
    fig11.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig11)

    st.write('-------------------------------')
    st.write('HABITACIONES DE HOTEL: {} alojamientos estan a manos de 10 personas y/o empresas, lo que supone el {:.2f}% de los alojamientos enteros' .format(host_HotelTOP['Hotel room'].head(10).sum(),(host_HotelTOP['Hotel room'].head(10).sum()/hotel.value_counts().sum()*100)))
    
    host_hotel = hotel.groupby(['host_id']).size()
    top_host_hotel = host_hotel.sort_values(ascending=False).head(int(len(host_hotel)*0.01))
    total_top_host_hotel = top_host_hotel.sum()
    total_hotel = host_hotel.sum()
    porcentaje = total_top_host_hotel/total_hotel*100

    labels = ['1% host', 'Otros']
    values = [porcentaje, 100-porcentaje]

    fig17 = px.pie(values=values, names=labels,title='Porcentaje de habitaciones de los 1% host mas recurrentes')
    st.write(fig17)

    fig12=px.scatter_mapbox(resultHotel, lat="latitude", lon="longitude",
                  color="host_id", color_continuous_scale=px.colors.sequential.Plasma,
                zoom=10, hover_name='price', opacity=0.5)
    
    fig12.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig12)

    st.write('-------------------------------')
    st.header('HABITACIONES COMPARTIDAS')
    #st.write(host_sharedTOP.head(10), host_sharedBOT.head(10))

    host_shared = shared.groupby(['host_id']).size()
    top_host_shared = host_shared.sort_values(ascending=False).head(int(len(host_shared)*0.01))
    total_top_host_shared = top_host_shared.sum()
    total_shared = host_shared.sum()
    porcentaje = total_top_host_shared/total_shared*100

    labels = ['1% host', 'Otros']
    values = [porcentaje, 100-porcentaje]

    fig18 = px.pie(values=values, names=labels,title='Porcentaje de habitaciones compartidas de los 1% host mas recurrentes')
    st.write(fig18)


    st.write('HABITACIONES COMPARTIDAS: {} alojamientos estan a manos de 10 personas y/o empresas, lo que supone el {:.2f}% de los alojamientos enteros' .format(host_sharedTOP['Shared room'].head(10).sum(),(host_sharedTOP['Shared room'].head(10).sum()/shared.value_counts().sum()*100)))

    fig13=px.scatter_mapbox(resultShared, lat="latitude", lon="longitude",
                  color="host_id", color_continuous_scale=px.colors.sequential.Plasma,
                zoom=10, hover_name='price', opacity=0.5)
    
    fig13.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig13)

    st.write('-------------------------------')

    #st.dataframe(top_hosts_count)

    host_listings = airbnb.groupby(['host_id']).size()
    top_hosts = host_listings.sort_values(ascending=False).head(int(len(host_listings)*0.01))
    total_top_hosts = top_hosts.sum()
    total_listings = host_listings.sum()
    porcentaje = total_top_hosts/total_listings*100
    labels = ['1% host', 'Otros']
    values = [porcentaje, 100-porcentaje]

    fig = px.pie(values=values, names=labels, title='Porcentaje de alojamientos que tienen el Top 1% de los Hosts')
    

    top_hosts__df = host_listings.sort_values(ascending=False).head(int(len(host_listings)*0.01))

    # Reset the index to convert host_id and listing count back into columns
    top_hosts_df = top_hosts__df.reset_index()

    airbnb2 = pd.read_csv('airbnb_anuncios.csv')
    top_hosts_df_copy = top_hosts_df.copy()
    top_hosts_df_copy = top_hosts_df_copy.rename(columns={0:'Nº de alojamientos'})
# Use the st.dataframe() method to display the result
    merged_df = pd.merge(top_hosts_df_copy, airbnb2[['host_id','host_name']], on='host_id')
    merged_df = merged_df.drop_duplicates(subset=['host_id'])
    # Rename columns
    merged_df = merged_df[['host_id', 'host_name', 'Nº de alojamientos']]
    
    top_hosts_df = merged_df

    # Use the st.dataframe() method to display the top hosts
    st.subheader("Representacion de los Top 1% de los Host")
    st.write(fig)
    # st.subheader("DataFrame de top hosts")
    # st.dataframe(top_hosts_df,use_container_width=True)
    

    st.subheader("DataFrame de top hosts")
    st.dataframe(top_hosts_df,use_container_width=True)
# Abre las imágenes que quieres usar en el collage
    im1 = Image.open('noticia.PNG')
    im2 = Image.open('34usuarios.PNG')
    im3 = Image.open('hoteleros.PNG')

    images = [im1, im2, im3]
    # Especifica la posición de cada imagen en el collage
    st.image(im1, width=700)
    st.empty()
    st.image(im2, width=700)
    st.empty()
    st.image(im3, width=700)


    st.header('Investigando a Claudia')
    st.image('Claudia.PNG',width=700)
    st.image('friendly.PNG',width=700)
    st.image('novasol.PNG')
    st.image('wyndham.PNG')
    st.image('worldwide.PNG')
    st.image('tom.PNG')
    st.image('detroit.PNG')



# Muestra el collage en Streamlit
    video_url = "https://www.youtube.com/watch?v=712cDkFsPKM"
    st.video(video_url)


    # Muestra la figura
    st.write('Fuente de datos:')
    st.write('https://www.eldiario.es/madrid/somos/malasana/las-empresas-que-controlan-airbnb-en-madrid-claudia-alberto-leticia-y-fer_1_6433295.html')
    st.write('https://www.elconfidencial.com/espana/madrid/2018-01-09/hoteleros-contra-cifuentes-pisos-turisticos-decreto_1503569/?utm_source=twitter&utm_medium=social&utm_campaign=ECDiarioManual')   
    st.write('https://www.lavanguardia.com/vida/20160906/41139009840/novasol-adquiere-la-compania-de-alquiler-de-apartamentos-friendly-rental.html') 
    st.write('https://www.platinumequity.com/news/wyndham-worldwide-announces-agreement-to-sell-its-european/') 
    st.write('https://www.platinumequity.com/about-us/')  
    st.write('https://www.cnbc.com/2021/10/08/pistons-owner-tom-gores-has-a-new-perspective-as-team-enters-restoration-process.html#:~:text=Gores%20purchased%20the%20team%20in,losing%20record%20under%20his%20ownership.')   
    st.write('https://www.youtube.com/watch?v=712cDkFsPKM')                 
#----------------------------------------------EMPIEZA EL SIDEBAR----------------------------------------------------------------

#ocultar errores
st.set_option('deprecation.showPyplotGlobalUse', False)   
# Create sidebar
st.sidebar.title("Filtros de búsqueda")

def search_neighbourhood(room_type, min_price, max_price, neighbourhood_group, neighbourhood):
    filtered_df = airbnb[(airbnb['room_type'] == room_type) & (airbnb['price'] >= min_price) & (airbnb['price'] <= max_price)]
    
    if neighbourhood_group:
        filtered_df = filtered_df[filtered_df['neighbourhood_group'] == neighbourhood_group]
    if neighbourhood:
        filtered_df = filtered_df[filtered_df['neighbourhood'] == neighbourhood]
    return filtered_df

room_type = st.sidebar.selectbox("Tipo de habitación", airbnb['room_type'].unique())
min_price = st.sidebar.number_input("Precio mínimo", min_value=0, max_value=10000, value=0)
max_price = st.sidebar.number_input("Precio máximo", min_value=0, max_value=10000, value=0)
use_neighbourhood_group = st.sidebar.checkbox("Filtrar por Grupo de barrios")
neighbourhood_group = st.sidebar.selectbox("Grupo de barrios", airbnb['neighbourhood_group'].unique())
use_neighbourhood = st.sidebar.checkbox("Filtrar por Barrios")
neighbourhood = st.sidebar.selectbox("Barrios", airbnb['neighbourhood'].unique())

if st.sidebar.button("Buscar"):
    result = search_neighbourhood(room_type, min_price, max_price, neighbourhood_group if use_neighbourhood_group else None, neighbourhood if use_neighbourhood else None)
    st.write("Resultados de búsqueda:")
    st.write(result)


