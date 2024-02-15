import PySimpleGUI as sg

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
listOfAttrText = ['Заголовок объекта']
listOfAttrNumber = ['Идентификатор объекта']

#Уровень продвижения объекта
listOfLvl = {"Все": 0,
            "Создание и модификация":"2",
            "Производство и эксплуатация":"5",
            "Согласование и утверждение":"1000"
            }
#Владелец объекта
listOfUsers = {"Все": 0,
                "Ольга Костюкова":"1223876",
                "Михаил Выдрин":"1373292",
                "Булат Ханафин": "1237194",
                "Вячаслав Булатов":"1236294",
                "Елена Голод":"1225547",
                "Александр Воронов":"1223844",
                "Ксения Дербенёва":"1234951"
               }
#Тип объекта
listOfTypes = {"Все": 0,
                "Модель детали":"1351",
                "Модель сборки":"1317",
                "Сборочные единциы":"1074",
                "Детали":"1052",
                "Чертеж PDF":"1742",
                "Чертёж Inventor":"1367",
                "Сборочный чертеж PDF":"1743",
                "Сборочный чертёж Inventor":"1333"

                }

numberOfLayout = 1
arguments = { 0: '', 1: ''}

def buttons():
    return [[sg.Frame(
            title= "Кнопки",
            layout = [[
                sg.Button('Ok',bind_return_key=True),
                sg.Button('Добавить'),
                sg.Button('Отмена')]]
                )]]

def resultField(resultPutput):
    return[[
        sg.Text("Результат:"),
        sg.InputText(resultPutput,k="-Input Result-")
        ]]

def mainField(mainArguments={'-Combo User-': "Все", '-Combo Type-': "Все", '-Combo Level-': "Все"}):
    return [[sg.Frame(title = "Основные атрибуты",
                      layout =[[
            sg.Text("Пользователь:"),
            sg.Combo(list(listOfUsers.keys()), default_value = mainArguments.get('-Combo User-'), k='-Combo User-'),
            sg.Text("Тип объекта"),
            sg.Combo(list(listOfTypes.keys()), default_value = mainArguments.get('-Combo Type-'), k='-Combo Type-'),],
            [sg.Text("Уровень продвижения объекта"),
            sg.Combo(list(listOfLvl.keys()), default_value = mainArguments.get('-Combo Level-'), k='-Combo Level-')]]
            )  ]]


def attributes(arguments = arguments, numberOfLayout = numberOfLayout):
    attributes = []
    for layout in range(numberOfLayout):
        attributes += [[
            sg.Text(f"Атрибут № {layout+1}"),
            sg.Combo(listOfAttrText + listOfAttrNumber,
                     default_value=arguments.get("-Combo Atribute-" + str(layout*2-2 if layout > 0 else "")),
                     k='-Combo Atribute-'
                     ),
            sg.Text('='), 
            sg.InputText(arguments.get('-Input Atribute-' + str(layout*2-1 if layout > 0 else "")), k='-Input Atribute-')
            ]]
    return attributes

def solve(arguments):
    answer = ['?']
    (answer.append(f'[Владелец объекта] = {listOfUsers.get(arguments.get("-Combo User-"))}')) if arguments.get("-Combo User-") != "Все" else None
    (answer.append(f'[Тип объекта] = {listOfTypes.get(arguments.get("-Combo Type-"))}')) if arguments.get("-Combo Type-") != "Все" else None
    (answer.append(f'[Уровень продвижения объекта] = {listOfLvl.get(arguments.get("-Combo Level-"))}')) if arguments.get("-Combo Level-") != "Все" else None

    for layout in range(numberOfLayout):    
        atribute = arguments.get("-Combo Atribute-" + str(layout*2-2 if layout > 0 else ""))
        atributeValue = arguments.get('-Input Atribute-' + str(layout*2-1 if layout > 0 else ""))
        answer.append(f"[{atribute}] LIKE '%{str(atributeValue)}%'" 
                      if atribute in listOfAttrText else f"[{atribute}]" + ' = ' + str(atributeValue)) if atribute != "" else None
         
    for i in range(1,len(answer)-1):
        answer.insert(i*2," AND ") if len(answer) > 1 else None

    print(answer)
    return ("".join(answer))



#Запускаем программу
window = sg.Window('Window Title', mainField() + attributes() + buttons())

while True:
    event, values = window.read(timeout=1000)

    if event == sg.WIN_CLOSED or event == 'Отмена': # if user closes window or clicks cancel
        break

    if event == '=': # if user closes window or clicks cancel
        break

    if event == "Добавить":
        numberOfLayout += 1
        window.close()
        window = sg.Window('Window Title', mainField(values) + attributes(values, numberOfLayout) + buttons())
        print(values)

    if event == "Ok":
        window.close()
        window = sg.Window("Window with result",mainField(values) + attributes(values, numberOfLayout) + buttons() + resultField(solve(values)) )

window.close()



             

