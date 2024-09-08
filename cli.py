import cmd
import time
import os
import glob


from transform import transform
from transform import apply
from target import calc
from predict import predict

class DiskPredictCLI(cmd.Cmd):
    intro = "Введите 'help' для отображения команд."
    prompt = "DiskPredict> "
    last_command = None

    # Функция обработки нераспознанных команд
    def default(self, line):
        self.last_command = line
    
    # Пропуск на Enter
    def emptyline(self):
        return False
        
    
    # Функция вызова вспомогательной команды help
    def do_help(self, arg):
        print("""
  Команды:
  transform ./data_example         Сформировать и расчитать БД
  apply ./new.csv                  Добавить данные
  predict MODEL SERIAL_NUMBER      Спрогнозировать кол-во дней до отказа по модели и серийному номеру
  exit                             Выход из программы
    """)

    # Конвертировать датасет к удобному формату (сформировать свою БД)
    def do_transform(self, folder):
        try:
            
            transform(folder)
            calc()
            print("Готово! База данных сформирована и расчитана!")
   
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")


    # Конвертировать датасет к удобному формату (сформировать свою БД)
    def do_calculate(self, folder):
        try:
            
            calc()
            print("Готово! База данных расчитана!")
   
        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    # Добавить CSV в базу данных
    def do_apply(self, path):
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Файл '{path}' не найден.")
            
            print(f"Началось дополнение базы данных из файла '{path}'")
            apply(path)             
            print("Готово! Файл трансформирован и расчитан!")

        except FileNotFoundError as e:
            print(f"Ошибка: {e}")
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    # Функция прогнозирования [модель жёсткого диска] [серийный номер]
    def do_predict(self, args):
        try:
            model, serial = args.split()

            print(f"Началось обучение и построение прогноза")
            days = predict(model, serial)

            print("Модель:", model)
            print("Серийный номер:", serial)
            print("Спрогнозированный вектор на каждый день в истории этого серийного номера:", days)
            print("Прогнозируемое количество дней до поломки:", days[-1])
        except ValueError:
            print('Ошибка: Используйте команду в формате "predict <модель> <серийный номер>".')
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}")

    # Функция выхода из утилиты
    def do_exit(self, arg):
        return True
    
    # Функция сохраняющая последнюю команду перед ее выполнением
    def precmd(self, line): 
        if line:
            self.last_command = line
        return line

    # Функция эмуляции нажатия стрелки вверх для возврата последней команды
    def do_up(self, _):
        if self.last_command:
            self.onecmd(self.last_command)

if __name__ == '__main__':
    DiskPredictCLI().cmdloop()
