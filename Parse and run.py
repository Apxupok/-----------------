import os
import PySimpleGUI as sg

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

def parceLicence():
    URL_TEMPLATE = "http://appsrv003:8995/"
    r = requests.get(URL_TEMPLATE)
    print(r.status_code)

    soup = bs(r.text, "html.parser")
    iterator = 0
    vacancies_names = soup.find_all('table', class_='infotable')
    for i in ((str(vacancies_names)).split("<td>")):
    #print(f"{iterator} {i}",sep='\n')
        iterator +=1

    countOfLicence = ((str(vacancies_names)).split("<td>")[52]).split("</td>")[0]
    print(countOfLicence)
    return countOfLicence



def title():
    return[[
        sg.Text(f"Количество лицензий: {parceLicence()}", k = "-Количество лицензий-")
        ]]

def timer():
    return[[
        sg.Text(f"Прошло времени:", k = "-Прошло времени-")
        ]]
    
def buttons(button = "Запуск"):
    return [[sg.Frame(
            title= "Кнопки",
            layout = [[
                sg.Button(button),
                sg.Button("Закрыть")]]
                )]]
def process():
    return[[
        sg.Text("Процесс запущен")
        ]]

#Запускаем программу
window = sg.Window('Window Title', title() + buttons())

while True:
    event, values = window.read(timeout=1000)

    if event == sg.WIN_CLOSED or event == 'Закрыть': # if user closes window or clicks cancel
        break

    if event == '=': # if user closes window or clicks cancel
        break

    if event == "Запуск":
        window.close()
        window = sg.Window("Window with result",timer() + title() + buttons("Стоп") + process(),finalize=True)
        #os.startfile(r'C:/Program Files/IPS/Client/IMClient.exe')
        time = 0
        window["-Прошло времени-"].update(f"Прошло времени: {time} мин")
        while event != "Стоп" or event == sg.WIN_CLOSED or event == 'Закрыть':
            event, values = window.read(timeout=60000) 

            time += 1
            window["-Прошло времени-"].update(f"Прошло времени: {time} мин")
            window["-Количество лицензий-"].update(f"Количество лицензий: {parceLicence()}")
            if (int(parceLicence()) > 0):
                os.startfile(r'C:/Program Files/IPS/Client/IMClient.exe')
                break 

            if event == sg.WIN_CLOSED or event == 'Закрыть': # if user closes window or clicks cancel
                window.close()
                break 

            if event == 'Стоп':
                window.close()
                window = sg.Window("Window with result", title() + buttons("Запуск"))

        

window.close()