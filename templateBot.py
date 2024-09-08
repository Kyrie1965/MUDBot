"""Шаблон бота для мада «Серый Камень Гаргата».

В этом коде выполняется подключение к миру «Серый Камень Гаргата» и
переназначен обработчик входящих от сервера строк (обрабочик пустой).
"""
from RMUDBot import RMUDBot

class TemplateBot(RMUDBot):
    def lineProcessing(self, line, ansi):
        pass

if __name__ == "__main__":
    bot = TemplateBot("ИМЯ ПЕРСОНАЖА", "ПАРОЛЬ")
    if bot.connect(verbose = True):
        while bot.connected:
            command = input()
            bot.send(command)