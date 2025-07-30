TEXTS = {
    1: """data_processor.py
import json
# Импорт модуля для работы с файловой системой
import os
# Константа с именем файла для хранения данных
DATA_FILE = "data.json"

# Класс, представляющий студента
class Student:
    # Конструктор класса
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades
        # Вычисление средней оценки (округленной до 2 знаков)
        self.avg = round(sum(grades) / len(grades), 2) if grades else 0.0

    # Метод для преобразования объекта в словарь
    def to_dict(self):
        return {
            "name": self.name,
            "grades": self.grades,
            "avg": self.avg # Средняя оценка уже вычислена в конструкторе
        }

# Функция загрузки данных из файла
def load_data():
    # Проверка существования файла
    #exists - Функция из модуля os.path. Проверяет существование файла или директории по указанному пути
    if not os.path.exists(DATA_FILE):
        return []  # Возвращаем пустой список, если файла нет
    # Открытие файла для чтения
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f) # Загрузка JSON из файла
        # Преобразование словарей в объекты Student
        return [Student(d["name"], d["grades"]) for d in data]
""",
    2: """# Функция сохранения данных в файл
def save_data(students):
    # Открытие файла для записи
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        # Преобразование объектов Student в словари и запись в JSON
        #json.dump() Функция для сериализации Python-объектов в JSON-формат
        #Записывает результат напрямую в файловый объект (в отличие от json.dumps(), который возвращает строку)
        #[s.to_dict() for s in students] - преобразующий список студентов в список словарей
        # indent=4 - Добавляет отступы в 4 пробела для вложенных структур (Без этого параметра JSON записывался бы в одну строку)
        json.dump([s.to_dict() for s in students], f, indent=4)

# Загрузка данных при старте программы
students = load_data()
# Функция обработки команд
def process_command(command, payload):
    global students  # Используем глобальную переменную students. Видна во всех функциях модуля. По умолчанию доступна только для чтения внутри функций
    # Используем match-case для обработки разных команд
    match command:
        case "PUT": # Добавление нового студента. .get() метод Специальный метод словаря для безопасного доступа
            name = payload.get("name")
            grades = payload.get("grades")
            # Проверка корректности данных
            #Это условие выполняет валидацию входных данных перед созданием нового студента
            #isinstance() - безопасная проверка типа, учитывающая наследование
            #Проверяет, что grades НЕ является объектом типа list
            if not name or not isinstance(grades, list):
                return {"error": "Некорректные данные"}
            # Создание нового студента
            new_student = Student(name, grades)
            students.append(new_student)  # Добавление в список
            save_data(students) # Сохранение данных
            return {"status": "ok"}""",
    3: """

        case "GET-SORT": # Получение отсортированного списка
            # Сортировка по имени (без учета регистра)
            #Я тут уже устала чет сильно
            #key=lambda s: s.name.lower() - Лямбда-функция, которая для каждого студента: Берет его имя (s.name). Приводит к нижнему регистру (lower())
           #Лямбда-функция (lambda) — это анонимная (безымянная) функция в Python, которая:
            #Не имеет имени (в отличие от def). Может принимать аргументы. Выполняет одно выражение и возвращает его результат. Используется там, где нужна простая функция на короткое время
           #Синтаксис лямбда-функции lambda аргументы: выражение
        # lambda — ключевое слово
        # аргументы — входные параметры (можно несколько через запятую)
            # выражение — что функция возвращает (нельзя писать return явно)
            result = sorted(students, key=lambda s: s.name.lower())
            #s.to_dict() for s in students] - Это генератор списка, который преобразует каждый объект Student
            # в списке students в словарь с помощью метода to_dict().
            return {"students": [s.to_dict() for s in result]}

        case "GET-REVERSE": # Получение списка в обратном порядке
            result = list(reversed(students))
            return {"students": [s.to_dict() for s in result]}

        case "GET-SHUFFLE": # Получение перемешанного списка
            import random # Импорт внутри функции, чтобы не загружать без необходимости
            result = students[:] # Создаем копию списка
            random.shuffle(result)  # Перемешиваем
            return {"students": [s.to_dict() for s in result]}

        case _: # Обработка неизвестной команды
            return {"error": f"Неизвестная команда: {command}"}
""",
    4: """server.py
import socket
#эт крч для работы с сетевыми соединениями
import threading
#ну тут понятно модуль для работы с потоками
import json
# Импорт модуля json для работы с JSON-данными
from data_processor import process_command
# Импорт функции process_command из модуля data_processor для обработки команд
HOST, PORT = '127.0.0.1', 8888
#Тут я определяю константы host(IP-адрес сервера и port(порт сервера)
""",
    5: """# Функция для обработки подключения клиента
# conn - объект соединения, addr - адрес клиента (IP и порт)
def handle_client(conn, addr):
    # Вывод сообщения о подключении клиента
    print(f"Подключен: {addr}.")
    # Использование контекстного менеджера(with) для соединения (автоматическое закрытие)
    with conn:
        # Создание буфера для накопления данных
        #buffer = b'' создает буфер для накопления сетевых данных.
        # В TCP-соединениях данные могут приходить частями (пакетами),
        # и нам нужно собрать их в цельное сообщение перед обработкой.
        buffer = b''
        # Бесконечный цикл для обработки данных от клиента
        while True:
            try:
                # Получение данных от клиента (максимум 4096 байт за раз)
                data = conn.recv(4096)
                # Если данных нет (клиент отключился), выходим из цикла
                if not data:
                    break
                    # Добавляем полученные данные в буфер
                buffer += data
                try:
                    # Пытаемся декодировать JSON из буфера
                    #decode() Декодировать - Метод decode() преобразует байтовую
                    # строку (bytes) в обычную строку (str),
                    # используя определённую кодировку (по умолчанию utf-8).
                    request = json.loads(buffer.decode())
                    # Очищаем буфер после успешного декодирования
                    buffer = b''
                    # Извлекаем команду из запроса
                    #get-request - это словарь Python, полученный из JSON
                    # .get("command") - метод словаря, который:
                    # Ищет ключ "command" в словаре request
                    # Возвращает соответствующее значение, если ключ существует
                    # Возвращает None, если ключа нет (без ошибки)
                    command = request.get("command")
                    # Извлекаем данные (payload) из запроса
                    payload = request.get("payload")
                    # Обрабатываем команду с помощью импортированной функции
                    response = process_command(command, payload)
                    # Отправляем ответ клиенту в JSON-формате
                    #conn.sendall() - Надёжная отправка всех данных
                    # response - это Python-объект (обычно словарь), который нужно отправить клиенту
                    # dumps() (от "dump string") преобразует объект в JSON-форматированную строку
                    conn.sendall(json.dumps(response).encode())
                    # Если произошла ошибка декодирования JSON, продолжаем цикл
                except json.JSONDecodeError:
                    continue
                    # Обработка ошибки разрыва соединения клиентом
            except ConnectionResetError:
                print(f"Отключен: {addr}.")
                break
                # Обработка любых других исключений
            except Exception as e:
                # Отправляем клиенту сообщение об ошибке
                conn.sendall(json.dumps({"error": str(e)}).encode())

    print(f"Отключен: {addr}.")

# Основная функция сервера
def main():
    # Создание TCP-сокета
""",
    6: """

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязка сокета к указанному хосту и порту
    server.bind((HOST, PORT))
    # Начало прослушивания входящих соединений
    server.listen()
    # Сообщение о запуске сервера
    print(f"Сервер запущен {HOST}:{PORT}")
    # Бесконечный цикл для принятия новых соединений
    while True:
        # Принятие нового соединения (блокирующий вызов)
        conn, addr = server.accept()
        # Создание нового потока для обработки клиента
        threading.Thread(target=handle_client, args=(conn, addr)).start()
# Стандартная проверка для запуска main() при непосредственном выполнении файла
if __name__ == "__main__":
    main()
""",
    7: """client.py
import sys
import socket
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

HOST, PORT = '127.0.0.1', 8888


class SocketWorker(QThread):
    response_received = pyqtSignal(dict) # Сигнал для передачи ответа

    def __init__(self, sock, request):
        super().__init__()
        self.sock = sock
        self.request = request

    def run(self):
        try:
            self.sock.sendall(json.dumps(self.request).encode())
            response = self.sock.recv(4096)
            self.response_received.emit(json.loads(response.decode()))
        except Exception as e:
            self.response_received.emit({"error": str(e)})

class StudentClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент - Управление студентами")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.layout = QVBoxLayout(self)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")
        self.grades_input = QLineEdit()
        self.grades_input.setPlaceholderText("Оценки через запятую")
        self.add_btn = QPushButton("Добавить")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["Все", "Средний ≥ 4", "Есть 5"])
        self.stats_label = QLabel()
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Имя", "Оценки", "Средний"])
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.grades_input)
        self.layout.addWidget(self.add_btn)
        self.layout.addWidget(self.filter_box)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.stats_label)
        self.add_btn.clicked.connect(self.add_student)
        self.filter_box.currentIndexChanged.connect(self.load_students)
        self.load_students()
""",
    8: """ def send_request(self, command, payload=None):
        request = {"command": command, "payload": payload}
        self.worker = SocketWorker(self.sock, request)
        self.worker.response_received.connect(self.handle_response)
        self.worker.start()

    def add_student(self):
        name = self.name_input.text().strip()
        grades_text = self.grades_input.text().strip()
        if not name or not grades_text:
            return
        try:
            grades = list(map(int, grades_text.split(',')))
        except ValueError:
            return
        self.send_request("PUT", {"name": name, "grades": grades})
        self.name_input.clear()
        self.grades_input.clear()

    def load_students(self):
        self.send_request("GET-SORT")

    def handle_response(self, response):
        if "students" in response:
            students = response["students"]
            filter_type = self.filter_box.currentText()
            if filter_type == "Средний ≥ 4":
                students = [s for s in students if s["avg"] >= 4]
            elif filter_type == "Есть 5":
                students = [s for s in students if 5 in s["grades"]]

            self.table.setRowCount(0)
            for s in students:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(s["name"]))
                self.table.setItem(row, 1, QTableWidgetItem(','.join(map(str, s["grades"]))))
                self.table.setItem(row, 2, QTableWidgetItem(f"{s['avg']:.2f}"))""",
    9: """if students:
                avgs = [s["avg"] for s in students]
                self.stats_label.setText(
                    f"Студентов: {len(students)} | Мин: {min(avgs):.2f} | Макс: {max(avgs):.2f} | Средний: {sum(avgs)/len(avgs):.2f}"
                )
            else:
                self.stats_label.setText("Нет данных")
        elif "error" in response:
            self.stats_label.setText("Ошибка: " + response["error"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StudentClient()
    win.show()
    sys.exit(app.exec())
""",
    10: """import json
import os

DATA_FILE = "data.json"

class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades
        self.avg = round(sum(grades) / len(grades), 2) if grades else 0.0

    def to_dict(self):
        return {
            "name": self.name,
            "grades": self.grades,
            "avg": self.avg
        }

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Student(d["name"], d["grades"]) for d in data]

def save_data(students):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in students], f, indent=4)

students = load_data()
""",
    11: """def process_command(command, payload):
    global students
    match command:
        case "PUT":
            name = payload.get("name")
            grades = payload.get("grades")
            if not name or not isinstance(grades, list):
                return {"error": "Некорректные данные"}
            new_student = Student(name, grades)
            students.append(new_student)
            save_data(students)
            return {"status": "ok"}
        case "GET-SORT":
            result = sorted(students, key=lambda s: s.name.lower())
            return {"students": [s.to_dict() for s in result]}
        case "GET-REVERSE":
            result = list(reversed(students))
            return {"students": [s.to_dict() for s in result]}
        case "GET-SHUFFLE":
            import random
            result = students[:]
            random.shuffle(result)
            return {"students": [s.to_dict() for s in result]}
        case _:
            return {"error": f"Неизвестная команда: {command}"}
""",
    12: """import socket
import threading
import json
from data_processor import process_command

HOST, PORT = '127.0.0.1', 8888

def handle_client(conn, addr):
    print(f"Подключен: {addr}.")
    with conn:
        buffer = b''
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                buffer += data
                try:
                    request = json.loads(buffer.decode())
                    buffer = b''
                    command = request.get("command")
                    payload = request.get("payload")
                    response = process_command(command, payload)
                    conn.sendall(json.dumps(response).encode())
                except json.JSONDecodeError:
                    continue
            except ConnectionResetError:
                print(f"Отключен: {addr}.")
                break
            except Exception as e:
                conn.sendall(json.dumps({"error": str(e)}).encode())
    print(f"Отключен: {addr}.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()import socket
import threading
import json
from data_processor import process_command

HOST, PORT = '127.0.0.1', 8888

def handle_client(conn, addr):
    print(f"Подключен: {addr}.")
    with conn:
        buffer = b''
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                buffer += data
                try:
                    request = json.loads(buffer.decode())
                    buffer = b''
                    command = request.get("command")
                    payload = request.get("payload")
                    response = process_command(command, payload)
                    conn.sendall(json.dumps(response).encode())
                except json.JSONDecodeError:
                    continue
            except ConnectionResetError:
                print(f"Отключен: {addr}.")
                break
            except Exception as e:
                conn.sendall(json.dumps({"error": str(e)}).encode())
    print(f"Отключен: {addr}.")

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Сервер запущен {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    main()
""",
    13: """import sys
import socket
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLabel
)
from PyQt6.QtCore import QThread, pyqtSignal

HOST, PORT = '127.0.0.1', 8888

class SocketWorker(QThread):
    response_received = pyqtSignal(dict)

    def __init__(self, sock, request):
        super().__init__()
        self.sock = sock
        self.request = request

    def run(self):
        try:
            self.sock.sendall(json.dumps(self.request).encode())
            response = self.sock.recv(4096)
            self.response_received.emit(json.loads(response.decode()))
        except Exception as e:
            self.response_received.emit({"error": str(e)})
""",
    14: """class StudentClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиент - Управление студентами")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.layout = QVBoxLayout(self)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")
        self.grades_input = QLineEdit()
        self.grades_input.setPlaceholderText("Оценки через запятую")
        self.add_btn = QPushButton("Добавить")
        self.filter_box = QComboBox()
        self.filter_box.addItems(["Все", "Средний ≥ 4", "Есть 5"])
        self.stats_label = QLabel()
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Имя", "Оценки", "Средний"])
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.grades_input)
        self.layout.addWidget(self.add_btn)
        self.layout.addWidget(self.filter_box)
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.stats_label)
        self.add_btn.clicked.connect(self.add_student)
        self.filter_box.currentIndexChanged.connect(self.load_students)
        self.load_students()

    def send_request(self, command, payload=None):
        request = {"command": command, "payload": payload}
        self.worker = SocketWorker(self.sock, request)
        self.worker.response_received.connect(self.handle_response)
        self.worker.start()
""",
    15: """def add_student(self):
        name = self.name_input.text().strip()
        grades_text = self.grades_input.text().strip()
        if not name or not grades_text:
            return
        try:
            grades = list(map(int, grades_text.split(',')))
        except ValueError:
            return
        self.send_request("PUT", {"name": name, "grades": grades})
        self.name_input.clear()
        self.grades_input.clear()

    def load_students(self):
        self.send_request("GET-SORT")
""",
    16: """   def handle_response(self, response):
        if "students" in response:
            students = response["students"]
            filter_type = self.filter_box.currentText()
            if filter_type == "Средний ≥ 4":
                students = [s for s in students if s["avg"] >= 4]
            elif filter_type == "Есть 5":
                students = [s for s in students if 5 in s["grades"]]

            self.table.setRowCount(0)
            for s in students:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(s["name"]))
                self.table.setItem(row, 1, QTableWidgetItem(','.join(map(str, s["grades"]))))
                self.table.setItem(row, 2, QTableWidgetItem(f"{s['avg']:.2f}"))

            if students:
                avgs = [s["avg"] for s in students]
                self.stats_label.setText(
                    f"Студентов: {len(students)} | Мин: {min(avgs):.2f} | Макс: {max(avgs):.2f} | Средний: {sum(avgs)/len(avgs):.2f}"
                )
            else:
                self.stats_label.setText("Нет данных")
        elif "error" in response:
            self.stats_label.setText("Ошибка: " + response["error"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = StudentClient()
    win.show()
    sys.exit(app.exec())
""",
    20: """import json
import os
from dataclasses import dataclass, asdict
import random

DATA_FILE = "data.json"

@dataclass
class DataItem:
    id: int
    name: str
    values: list
    avg: float = 0.0
    
    def __post_init__(self):
        self.avg = round(sum(self.values) / len(self.values), 2) if self.values else 0.0

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return [DataItem(**item) for item in json.load(f)]

def save_data(items):
    with open(DATA_FILE, 'w') as f:
        json.dump([asdict(item) for item in items], f, indent=4)

def process_command(command, payload):
    items = load_data()
    
    match command:
        case "PUT":
            new_item = DataItem(**payload)
            items.append(new_item)
            save_data(items)
            return {"status": "ok"}
            
        case "GET-ALL":
            return {"items": [asdict(item) for item in items]}
            
        case "GET-SORT":
            sorted_items = sorted(items, key=lambda x: x.avg)
            return {"items": [asdict(item) for item in sorted_items]}
            
        case "GET-REVERSE":
            reversed_items = list(reversed(items))
            return {"items": [asdict(item) for item in reversed_items]}
            
        case "GET-SHUFFLE":
            shuffled_items = items.copy()
            random.shuffle(shuffled_items)
            return {"items": [asdict(item) for item in shuffled_items]}
            
        case _:
            return {"error": "Unknown command"}""",
    21: """import sys
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import socket

HOST, PORT = 'localhost', 8888

class ClientApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sock = socket.socket()
        self.sock.connect((HOST, PORT))
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Data Client")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Input fields
        self.id_input = QLineEdit(placeholderText="ID")
        self.name_input = QLineEdit(placeholderText="Name")
        self.values_input = QLineEdit(placeholderText="Values (comma separated)")
        
        # Buttons
        self.add_btn = QPushButton("Add")
        self.add_btn.clicked.connect(self.add_item)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Values", "Avg"])
        
        # Filters
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Avg ≥ 4", "Has value 5"])
        self.filter_combo.currentIndexChanged.connect(self.load_data)
        
        # Stats
        self.stats_label = QLabel("Stats: ")
        
        # Add widgets
        layout.addWidget(self.id_input)
        layout.addWidget(self.name_input)
        layout.addWidget(self.values_input)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.filter_combo)
        layout.addWidget(self.table)
        layout.addWidget(self.stats_label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.load_data()
        
    def add_item(self):
        try:
            data = {
                "id": int(self.id_input.text()),
                "name": self.name_input.text(),
                "values": [int(x) for x in self.values_input.text().split(',')]
            }
            self.send_request("PUT", data)
            self.id_input.clear()
            self.name_input.clear()
            self.values_input.clear()
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid input")
            
    def load_data(self):
        self.send_request("GET-ALL")
        
    def send_request(self, command, payload=None):
        try:
            self.sock.sendall(json.dumps({
                "command": command,
                "payload": payload
            }).encode())
            
            response = json.loads(self.sock.recv(4096).decode())
            self.update_ui(response)
            
        except Exception as e:
            self.stats_label.setText(f"Error: {str(e)}")
            
    def update_ui(self, response):
        if "items" in response:
            items = response["items"]
            filter_text = self.filter_combo.currentText()
            
            if filter_text == "Avg ≥ 4":
                items = [i for i in items if i['avg'] >= 4]
            elif filter_text == "Has value 5":
                items = [i for i in items if 5 in i['values']]
                
            self.table.setRowCount(len(items))
            for row, item in enumerate(items):
                self.table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
                self.table.setItem(row, 1, QTableWidgetItem(item['name']))
                self.table.setItem(row, 2, QTableWidgetItem(', '.join(map(str, item['values']))))
                self.table.setItem(row, 3, QTableWidgetItem(f"{item['avg']:.2f}")))
                
            if items:
                avgs = [i['avg'] for i in items]
                self.stats_label.setText(
                    f"Total: {len(items)} | Min: {min(avgs):.2f} | Max: {max(avgs):.2f} | Avg: {sum(avgs)/len(avgs):.2f}"
                )
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientApp()
    window.show()
    sys.exit(app.exec())""",
    22: """# data_processor.py
@dataclass
class Book:
    isbn: str
    title: str
    author: str
    year: int
    rating: float

# client.py
self.table.setHorizontalHeaderLabels(["ISBN", "Название", "Автор", "Год", "Рейтинг"])
self.filter_combo.addItems(["Все", "Рейтинг > 4", "После 2000 года"])""",
    23: """# data_processor.py
@dataclass
class Employee:
    id: str
    name: str
    position: str
    salary: float
    experience: int

# client.py
self.table.setHorizontalHeaderLabels(["ID", "Имя", "Должность", "Зарплата", "Стаж"])
self.filter_combo.addItems(["Все", "Зарплата > 50000", "Стаж > 5 лет"])""",
    24: """# data_processor.py
@dataclass
class Car:
    vin: str
    brand: str
    year: int
    mileage: int
    price: float

# client.py
self.table.setHorizontalHeaderLabels(["VIN", "Марка", "Год", "Пробег", "Цена"])
self.filter_combo.addItems(["Все", "Пробег < 100000", "Цена < 1000000"])""",
    25: """# data_processor.py
@dataclass
class Student:
    id: str
    name: str
    group: str
    grades: list
    avg_grade: float = 0.0

# client.py
self.table.setHorizontalHeaderLabels(["ID", "Имя", "Группа", "Оценки", "Средний"])
self.filter_combo.addItems(["Все", "Средний ≥ 4.5", "Группа ИВТ-21"])""",
    26: """# data_processor.py
@dataclass
class Product:
    article: str
    name: str
    price: float
    quantity: int
    category: str

# client.py
self.table.setHorizontalHeaderLabels(["Артикул", "Название", "Цена", "Кол-во", "Категория"])
self.filter_combo.addItems(["Все", "Цена < 500", "Кол-во > 10"])""",
    27: """# data_processor.py
@dataclass
class Patient:
    card_id: str
    name: str
    diagnosis: str
    visit_date: str
    cost: float

# client.py
self.table.setHorizontalHeaderLabels(["Карта", "ФИО", "Диагноз", "Дата", "Стоимость"])
self.filter_combo.addItems(["Все", "Стоимость > 10000", "2024 год"])""",
    28: """# data_processor.py
@dataclass
class Order:
    id: str
    dish: str
    price: float
    cook_time: int
    status: str

# client.py
self.table.setHorizontalHeaderLabels(["ID", "Блюдо", "Цена", "Время", "Статус"])
self.filter_combo.addItems(["Все", "Цена > 1000", "Статус Готово"])""",
    29: """# data_processor.py
@dataclass
class Movie:
    id: str
    title: str
    genre: str
    rating: float
    duration: int

# client.py
self.table.setHorizontalHeaderLabels(["ID", "Название", "Жанр", "Рейтинг", "Длительность"])
self.filter_combo.addItems(["Все", "Рейтинг > 8", "Жанр Фантастика"])""",
    30: """# data_processor.py
@dataclass
class Transaction:
    id: str
    amount: float
    type: str
    date: str
    category: str

# client.py
self.table.setHorizontalHeaderLabels(["ID", "Сумма", "Тип", "Дата", "Категория"])
self.filter_combo.addItems(["Все", "Сумма > 50000", "Тип Расход"])"""

}