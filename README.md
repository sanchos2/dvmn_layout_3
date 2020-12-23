# Парсер книг с сайта tululu.org

Парсер позволяет загружать с сайта текст книги, обложку и описание книги в формате JSON.

### Как установить

Устанавливаем Python:
```
sudo apt install python3
sudo apt install python3-pip
```
Клонируем проект:
```
git clone https://github.com/sanchos2/dvmn_layout_3
cd dvmn_layout_3
```
Создаем виртуальное окружение, активируем его и  устанавливаем зависимости:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Аргументы

Параметры запуска скрипта:
```
--start_page START_PAGE    Начальная страница
--end_page END_PAGE        Конечная страница
--dest_folder DEST_FOLDER  Путь к каталогу с результатами парсинга
--skip_imgs                Не скачивать картинки
--skip_txt                 Не скачивать книги
--json_path JSON_PATH      Путь к json файлу с результатами парсинга
```
В корне проекта можно создать файл .env в котором имеется возможность переопределить имя json файла и log файла по умолчанию
с помощью переменной JSON_FILE_NAME и LOG_FILE_NAME. Пример:
```
JSON_FILE_NAME=my_file.json
LOG_FILE_NAME=my_log.log

```

Обязательный параметр `--start_page`, остальные опциональные.

Пример:
Будут скачаны все книги начиная с 234 страницы:
```
parse_tululu_category.py --start_page 234
```

Пример:
Будут скачаны все книги начиная с 234 страницы и заканчивая 236ой включительно:
```
parse_tululu_category.py --start_page 234 --end_page 237
```

Пример:
Будут скачаны все книги начиная с 234 страницы и заканчивая 236ой включительно, файл с описанием сохранится в /home/user/documents/library.json:
```
parse_tululu_category.py --start_page 234 --end_page 237 --json_path /home/user/documents/library.json
```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).