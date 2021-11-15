import requests
import unicodedata
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tabulate import tabulate
import os

links = []
nombres = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
response = requests.get('https://www.jugarscattergories.com/categorias.php',headers=headers)
soup = BeautifulSoup(response.content, 'lxml')
for cat in soup.select('#content ul a'): #Obtener Links y Nombres de Categorias
    links.append(cat.get('href'))
    nombres.append(cat.text)

topics = input('Ingresa los topics separados por ",":\n')
#Para muestra de resultados rapidos: topics = 'Animales,frutas,nombres,paises,peliculas,colores,flores'
topicarr = topics.split(',')
letra = ''
data = []
tableheaders = []

def clearConsole(): #Limpiar Consola
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

while letra != '0':
    tablerow = ['']*len(topicarr) #Inicializar tablerow longitud igual al numero de topics
    letra = input('Ingresa la letra elegida (0=Salir):\n')

    def normalize(text):    #Normalizar tildes
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return str(text)
    
    def getbyletter(letra,link,idx):   #Buscar en la categoria con la letra elegida
        response = requests.get(link+'/'+letra,headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        tablerow[idx] = soup.select('.terminos li')[random.randint(0,len(soup.select('.terminos li'))-1)].text #Agregar a row en el indice indicado para respetar los headers

    #Iniciar thread por cada topic para buscar con la letra indicada (El primer topic que cumpla la condicion)
    with ThreadPoolExecutor(max_workers=10) as executor:
        for idxt,topic in enumerate(topicarr):
            for idx,nombre in enumerate(nombres):
                if (normalize(nombre.lower()).startswith(normalize(topic.lower()))):
                        tableheaders.append(nombre.split(' ')[0]) #Agregar topic como header en idxt 
                        executor.submit(getbyletter,letra,links[idx],idxt) 
                        break
        executor.shutdown(wait=True) #Esperar threads
        data.append(tablerow) #Agregar row a la tabla

    clearConsole()
    print(tabulate(data,tableheaders)) #Mostrar tabla
    print('\n')

