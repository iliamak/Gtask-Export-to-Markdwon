import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Указываем права доступа
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']

def main():
    # Аутентификация
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Подключаемся к Google Tasks
    service = build('tasks', 'v1', credentials=creds)

    # Получаем все списки задач
    tasklists = service.tasklists().list().execute()
    tasklist_id = None
    for tasklist in tasklists.get('items', []):
        if tasklist['title'] == 'Идеи':
            tasklist_id = tasklist['id']
            break

    if tasklist_id is None:
        print("Список задач 'Идеи' не найден.")
        return

  # Получаем все задачи с учетом пагинации
    tasks_items = []
    next_page_token = None
    while True:
        tasks = service.tasks().list(tasklist=tasklist_id, pageToken=next_page_token).execute()
        tasks_items.extend(tasks.get('items', []))
        next_page_token = tasks.get('nextPageToken')
        if not next_page_token:
            break

    if not tasks_items:
        print("В списке 'Идеи' нет задач.")
        return

    # Форматируем задачи в Markdown
    markdown_content = ""
    for task in tasks_items:
        title = task.get('title', 'Без названия')
        notes = task.get('notes', '')
        markdown_content += f"## {title}\n{notes}\n\n"

    # Сохраняем в файл
    with open('ideas.md', 'w', encoding='utf-8') as md_file:
        md_file.write(markdown_content)

    print("Задачи успешно сохранены в ideas.md")

if __name__ == '__main__':
    main()