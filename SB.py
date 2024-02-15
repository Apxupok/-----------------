import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader, PdfWriter
import os
import win32com.client

def create_pdf():
    # Выбираем папку, содержащую .tiff файлы, из которой будем создавать PDF
    folder_path = filedialog.askdirectory(parent=root)
    if folder_path:
        # добавляем фильтрацию файлов .tif

        
        # Создаем папку "tif" для перемещения исходных .tiff файлов
        tif_folder = os.path.join(folder_path, "tif")
        if not os.path.exists(tif_folder):
            os.makedirs(tif_folder)
        
        # Получаем список .tiff файлов в выбранной папке
        tiff_files = [filename for filename in os.listdir(folder_path) if filename.lower().endswith('.tif')]

        for tiff_file in tiff_files:

            tiff_path = os.path.join(folder_path, tiff_file)

            
            
            # Перемещаем .tiff файлы в папку "tif"
            new_tiff_path = os.path.join(tif_folder, tiff_file)
            os.rename(tiff_path, new_tiff_path)
            
            # Создаем объект COM для взаимодействия с Adobe Acrobat
            adobe_app = win32com.client.Dispatch('AcroExch.App')
            adobe_app.Show()  # Открываем приложение Adobe Acrobat
            
            av_doc = win32com.client.Dispatch('AcroExch.AVDoc')
            
            # Открываем .tiff файл в Adobe Acrobat
            av_doc.Open(new_tiff_path, new_tiff_path)
            
            pd_doc = av_doc.GetPDDoc()
            
            # Выбираем путь для сохранения PDF файла
            # Переименовываем файл, если в конце было "CБ", чтобы стало "СБ"
            if tiff_file.endswith('CБ.tif'):
                new_tiff_file = os.path.join(folder_path, tiff_file.replace('CБ', 'СБ'))
                save_path = os.path.join(folder_path, new_tiff_file[:-4] + '.pdf')
                print(new_tiff_file)
            else: 
                save_path = os.path.join(folder_path, tiff_file[:-4] + '.pdf')

            # Сохраняем файл PDF с использованием выбранного пути
            pd_doc.Save(1, save_path)
            pd_doc.Close()
            
            av_doc.Close(True)
            
            adobe_app.Exit()
        
        # Показывать список преобразованных файлов
        show_converted_files(folder_path, folder_path)

def process_pdf():
    # Выбираем папку с PDF файлами для обработки
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Создаем папку "old_pdf" для перемещения оригинальных PDF файлов
        old_pdf_folder = os.path.join(folder_path, "old_pdf")
        if not os.path.exists(old_pdf_folder):
            os.makedirs(old_pdf_folder)
        
        # Перемещаем все PDF файлы в папку "old_pdf"
        move_pdf_files(folder_path, old_pdf_folder)
        
        # Обрабатываем каждый PDF файл в выбранной папке
        for filename in os.listdir(old_pdf_folder):
            if filename.endswith('.pdf'):
                pdf_file = os.path.join(old_pdf_folder, filename)

                # Открываем PDF файл
                with open(pdf_file, 'rb') as file:
                    pdf_reader = PdfReader(file)

                    # Удаляем свойства документа "Описание" и "Заказные" в PDF
                    if "/Title" in pdf_reader.trailer["/Info"]:
                        del pdf_reader.trailer["/Info"]["/Title"]
                    if "/Subject" in pdf_reader.trailer["/Info"]:
                        del pdf_reader.trailer["/Info"]["/Subject"]

                    # Создаем новый PDF writer
                    pdf_writer = PdfWriter()

                    # Добавляем все страницы в новый PDF writer
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)

                    # Сохраняем изменения в оригинальном PDF файле
                    new_pdf_file = os.path.join(folder_path, filename)
                    with open(new_pdf_file, 'wb') as new_file:
                        pdf_writer.write(new_file)

                    # Переименовываем файл, если в конце было "CБ", чтобы стало "СБ"
                    if filename.endswith('CБ.pdf'):
                        new_filename = os.path.join(folder_path, filename.replace('CБ', 'СБ'))
                        os.rename(pdf_file, new_filename)

        # Показывать список старых файлов PDF
        show_converted_files(folder_path, folder_path)

def move_pdf_files(folder_path, pdf_folder):
    # Создаем папку "pdf" в выбранной папке
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    # Получаем список .pdf файлов в выбранной папке
    pdf_files = [filename for filename in os.listdir(folder_path) if filename.lower().endswith('.pdf')]

    # Перемещаем .pdf файлы в папку "pdf"
    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder_path, pdf_file)
        new_pdf_path = os.path.join(pdf_folder, pdf_file)
        os.rename(pdf_path, new_pdf_path)

def show_converted_files(folder_path, pdf_folder):
    # Создаем новое окно tkinter для списка преобразованных файлов
    converted_files_window = tk.Toplevel()
    converted_files_window.title("Преобразованные файлы")
    converted_files_window.geometry("400x300") # Устанавливаем размер окна

    # Получаем список старых файлов PDF в папке "pdf"
    pdf_files = [filename for filename in os.listdir(pdf_folder) if filename.lower().endswith('.pdf')]

    # Получаем количество преобразованных файлов
    num_of_converted_files = len(pdf_files)

    # Создаем список для отображения преобразованных файлов
    listbox = tk.Listbox(converted_files_window)

    # Добавляем заголовок и количество преобразованных файлов
    listbox.insert(tk.END, "Преобразованные файлы:")
    listbox.insert(tk.END, f"Количество файлов: {num_of_converted_files}")
    listbox.insert(tk.END, "")

    # Выводим список преобразованных файлов
    for pdf_file in pdf_files:
        listbox.insert(tk.END, os.path.join(pdf_folder, pdf_file))

    # Размещаем список на окне
    listbox.pack(fill="both", expand=True)

    # Цикл обработки событий для окна списка преобразованных файлов
    converted_files_window.mainloop()


# Создаем графический интерфейс
root = tk.Tk()

# Создаем кнопки
button_create_pdf = tk.Button(root, text="Создать PDF из Tiff", command=create_pdf)
button_create_pdf.pack()

button_process_pdf = tk.Button(root, text="Обработать PDF файлы", command=process_pdf)
button_process_pdf.pack()

# Запускаем графический интерфейс
root.mainloop()