"""Пример бота для мада «Серый Камень Гаргата».
Бот сохраняет все сообщения, которые говорят персонажу. В ответ на "Привет" танцует. 
"""
from RMUDBot import RMUDBot
import re
import queue

class SampleBot(RMUDBot):
    def lineProcessing(self, line, ansi):
        regex = re.compile("^(.+) сказала* Вам: \"(.+)\"$")
        result = regex.match(line)
        if result:
            messages.put(line)
            if result.group(2).lower() == "привет":
                self.send("танцевать")
                self.send("сказать " + result.group(1) + " И тебе привет!")

messages = queue.Queue()

if __name__ == "__main__":
    bot = SampleBot("ИМЯ ПЕРСОНАЖА", "ПАРОЛЬ")
    if bot.connect(verbose = True):
        while True:
            command = input()
            bot.send(command)