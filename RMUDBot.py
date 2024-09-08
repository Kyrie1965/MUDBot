"""RMUDBot — подкласс MUDBot для работы с мадом «Серый Камень Гаргата».
Вам необходимо его наследовать в своей программе.

RMUDBot(name, password)
    Конструктор с данными подключения к серверу мира «Серый Камень Гаргата».

loginProcessing(line)
    Переопределенный метод класса MUDBot.
    В нем содержится логика входа персонажа в игровой мир «Серый Камень Гаргата».
"""
from MUDBot import MUDBot

class RMUDBot(MUDBot):
    def __init__(self, name, password) -> None:
        if len(name) == 0 or len(password) == 0:
            raise ValueError("RMUDBot(name, password): Имя и пароль не могут быть пустыми.")
        super().__init__("rmud.org", 3041)
        self.name = name
        self.password = password

    def loginProcessing(self, line):
        str = MUDBot.stripANSI(line).strip()

        if str.startswith("Make a choice:"):
            self.send("1")
            return

        if str.startswith("Введите имя Вашего персонажа или \"новый\" для создания нового:"):
            self.send(self.name)
            return

        if str.startswith("Пароль:"):
            self.send(self.password)
            return

        if str.startswith("*** НАЖМИТЕ ВВОД:"):
            self.send("")
            return

        if str.startswith("1) Войти в игру."):
            self.send("1")
            return
        
        if str.startswith("Имя персонажа может содержать только русские буквы."):
            self.disconnect()
            return
        
        if str.startswith("Персонажа с таким именем не существует."):
            self.disconnect()
            return
        
        if str.startswith("Неверный пароль."):
            self.disconnect()
            return