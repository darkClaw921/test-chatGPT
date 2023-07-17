import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# Установка разрешений для доступа к Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# ID папки, из которой вы хотите скачать файлы
FOLDER_ID = ''

# Определение пути, в который будут загружены файлы

DOWNLOAD_PATH = '/Users/igorgerasimov/Python/Bitrix/test-chatGPT/'
#TOKEN_JSON = 'kgtaprojects-8706cc47a185.json'
TOKEN_JSON = '/Users/igorgerasimov/Python/Bitrix/test-chatGPT/client_secrets.json'

# Путь к папке, в которую будут загружены файлы
#DOWNLOAD_PATH = 'путь_к_папке_для_сохранения'


def download_files(FOLDER_ID:str, maxFile:int = 5)-> list:
    """Скачивает файлы из папки в google drive

    Args:
        FOLDER_ID (str): id папки из которой качать
        maxFile (int, optional): сколько нужно скачать файлов Defaults to 5.

    Returns:
        list: список имен скаченных файлов
    """
    # Аутентификация пользователя
    filesDownload = []
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    # ID папки, из которой вы хотите скачать файлы
    folder_id = FOLDER_ID

    # Запрос списка файлов из заданной папки
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    #maxFile = 5
    # Скачивание файлов
    for index, file in enumerate(file_list):
        # Определение пути и имени файла
        file_path = os.path.join(DOWNLOAD_PATH, file['title'])

        # Скачивание файла
        file.GetContentFile(file_path)
        filesDownload.append(file['title'])
        print(f"Скачивание файла {file['title']} завершено")
        
        if index == maxFile-1:
            return filesDownload

    print("Скачивание файлов завершено!")
    return filesDownload



if __name__ == '__main__':
    download_files()