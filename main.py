# Изменение для лабораторной №5
import os
import csv
from datetime import datetime
from operator import itemgetter

class Movement:
    """Базовый класс для представления одного перемещения офисного работника"""
    
    def __init__(self, id_num, datetime_str, is_workplace, room):
        self.__setattr__('id', id_num)
        self.__setattr__('datetime', datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S'))
        self.__setattr__('is_workplace', is_workplace.lower() == 'true' if isinstance(is_workplace, str) else is_workplace)
        self.__setattr__('room', int(room))

    def __setattr__(self, name, value):
        """Перегрузка для записи значений в свойства"""
        if name == 'id' and not isinstance(value, int):
            raise ValueError("ID должен быть целым числом")
        if name == 'datetime' and not isinstance(value, datetime):
            raise ValueError("Дата должна быть объектом datetime")
        if name == 'is_workplace' and not isinstance(value, bool):
            raise ValueError("Рабочее место должно быть булевым значением")
        if name == 'room' and not isinstance(value, int):
            raise ValueError("Номер комнаты должен быть целым числом")
        super().__setattr__(name, value)

    def __repr__(self):
        """Перегрузка repr для строкового представления объекта"""
        return (f"Movement(id={self.id}, datetime={self.datetime.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"is_workplace={self.is_workplace}, room={self.room})")

    @staticmethod
    def validate_csv_row(row):
        """Статический метод для проверки корректности строки CSV"""
        try:
            int(row['№'])
            datetime.strptime(row['Дата и время'], '%Y-%m-%d %H:%M:%S')
            row['Рабочее место'].lower() in ('true', 'false')
            int(row['Комната'])
            return True
        except (KeyError, ValueError, TypeError):
            return False

class MovementCollection(Movement):
    """Класс для работы с коллекцией перемещений (наследование от Movement)"""
    
    def __init__(self, movements=None):
        self._movements = movements if movements is not None else []
        self._index = 0  # Для итератора

    def __iter__(self):
        """Реализация итератора"""
        self._index = 0
        return self

    def __next__(self):
        """Получение следующего элемента при итерации"""
        if self._index >= len(self._movements):
            raise StopIteration
        movement = self._movements[self._index]
        self._index += 1
        return movement

    def __getitem__(self, index):
        """Доступ к элементам коллекции по индексу"""
        if not isinstance(index, int) or index < 0 or index >= len(self._movements):
            raise IndexError("Недопустимый индекс")
        return self._movements[index]

    def __len__(self):
        """Длина коллекции"""
        return len(self._movements)

    @staticmethod
    def count_files_in_directory(path):
        """Статический метод для подсчета файлов в директории"""
        try:
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            return len(files)
        except Exception as e:
            print(f"Ошибка при анализе директории: {e}")
            return 0

    def add_movement(self, movement):
        """Добавление нового перемещения"""
        if not isinstance(movement, Movement):
            raise ValueError("Добавляемый объект должен быть экземпляром Movement")
        self._movements.append(movement)

    def sorted_by_date(self):
        """Генератор для сортировки по дате (новые сначала)"""
        sorted_movements = sorted(self._movements, key=lambda x: x.datetime, reverse=True)
        for movement in sorted_movements:
            yield movement

    def sorted_by_room(self):
        """Генератор для сортировки по номеру комнаты"""
        sorted_movements = sorted(self._movements, key=lambda x: x.room)
        for movement in sorted_movements:
            yield movement

    def filter_workplace(self, is_workplace=True):
        """Генератор для фильтрации по признаку рабочего места"""
        for movement in self._movements:
            if movement.is_workplace == is_workplace:
                yield movement

    @classmethod
    def from_csv(cls, filename):
        """Создание коллекции из CSV-файла"""
        try:
            movements = []
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if cls.validate_csv_row(row):
                        movement = Movement(
                            id_num=int(row['№']),
                            datetime_str=row['Дата и время'],
                            is_workplace=row['Рабочее место'],
                            room=row['Комната']
                        )
                        movements.append(movement)
            return cls(movements)
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return cls()

    def save_to_csv(self, filename_prefix="result"):
        """Сохранение данных в CSV-файлы"""
        try:
            # Сохранение всех данных
            with open(f"{filename_prefix}_all.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['№', 'Дата и время', 'Рабочее место', 'Комната'])
                for movement in self._movements:
                    writer.writerow([
                        movement.id,
                        movement.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        str(movement.is_workplace),
                        movement.room
                    ])

            # Сохранение только рабочих мест
            with open(f"{filename_prefix}_work.csv", 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['№', 'Дата и время', 'Комната'])
                for movement in self.filter_workplace():
                    writer.writerow([
                        movement.id,
                        movement.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        movement.room
                    ])
            print(f"Результаты сохранены в файлы {filename_prefix}_all.csv и {filename_prefix}_work.csv")
            return True
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False

def get_valid_directory():
    """Безопасный запрос пути к директории"""
    while True:
        path = input("Введите путь к директории (или Enter для текущей): ").strip()
        if not path:
            path = os.getcwd()
        if os.path.isdir(path):
            return path
        print(f"Ошибка: '{path}' не является директорией!")

def get_valid_csv_file(default="movements.csv"):
    """Безопасный запрос CSV-файла"""
    while True:
        path = input(f"Введите путь к CSV-файлу [по умолчанию {default}]: ").strip()
        if not path:
            path = default
        if os.path.isfile(path) and path.endswith('.csv'):
            return path
        print(f"Ошибка: файл '{path}' должен существовать и иметь расширение .csv!")

def main():
    print("Change in cloned repo")
    print("=== Лабораторная работа №4. Классы ===")
    
    # Подсчет файлов в директории
    print("\nШаг 1/3: Анализ файлов в директории")
    dir_path = get_valid_directory()
    file_count = MovementCollection.count_files_in_directory(dir_path)
    print(f"Найдено файлов: {file_count}")
    
    # Чтение данных из CSV
    print("\nШаг 2/3: Анализ данных перемещений")
    csv_path = get_valid_csv_file()
    collection = MovementCollection.from_csv(csv_path)
    
    if len(collection) > 0:
        # Анализ данных
        print("\nШаг 3/3: Анализ перемещений")
        
        # Вывод первых 5 перемещений, отсортированных по дате
        print("\nПоследние 5 перемещений (по дате):")
        for i, movement in enumerate(collection.sorted_by_date()):
            if i >= 5:
                break
            print(f"{movement.datetime} | Комната: {movement.room} | Рабочее место: {'Да' if movement.is_workplace else 'Нет'}")
        
        # Вывод первых 5 перемещений, отсортированных по комнате
        print("\nПервые 5 перемещений (по комнатам):")
        for i, movement in enumerate(collection.sorted_by_room()):
            if i >= 5:
                break
            print(f"Комната: {movement.room} | {movement.datetime}")
        
        # Подсчет рабочих и нерабочих перемещений
        workplace_count = sum(1 for _ in collection.filter_workplace(True))
        non_workplace_count = sum(1 for _ in collection.filter_workplace(False))
        print(f"\nВсего рабочих перемещений: {workplace_count}")
        print(f"Всего НЕ рабочих перемещений: {non_workplace_count}")
        
        # Сохранение результатов
        if input("\nСохранить результаты? (y/n): ").lower() == 'y':
            collection.save_to_csv()

if __name__ == "__main__":
    main()