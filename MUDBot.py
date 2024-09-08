"""MUDBot — основной класс работы с мадами. В основном он предназначен для создания подклассов под конкретные
мады. Класс использует модифированную библиотеку telnetlib.

MUDBot(host, port)
    Конструктор.
    
connect() -> bool
    Подключение к серверу.

disconnect()
    Принудительное отключение от сервера.

send(msg)
    Отправка команды в мад. Можно отправлять строку или массив строк.

stripANSI(text) -> str
    Статический метод класс, удаляет цветовую ANSI-разметку в тексте.

receiveThread()
    Внутренний метод обработки входящих данных от сервера.
    Не предназначен для использования вне класса и переопределения.

loginProcessing(line)
    Метод подлежащий переопределению (callback) в подклассе.
    В нем должна содержаться логика входа персонажа в игровой мир.
    Переопределенный метод выполняется в потоке receiveThread,
    а не в основном потоке вашей программы — учитывайте это.

    line — строка от сервера в оригинальном виде.

lineProcessing(line, ansi)
    Метод подлежащий переопределению (callback) в последнем подклассе.
    В нем должна содержаться вся логика работы бота.
    Переопределенный метод выполняется в потоке receiveThread,
    а не в основном потоке вашей программы — учитывайте это.

    line — строка от сервера без цветовой ANSI-разметки.
    ansi — строка от сервера в оригинальном виде.
"""
import telnetlib_mod
import threading
import re
import select
import time

class MUDBot:
    def __init__(self, host:str, port:int) -> None:
        self.host = host
        self.port = port
        self.socketLock = threading.Lock()
        self.connected = False
        self.telnet = None
        #self.lineProcessing = False
        self.connectionID = 1

    def connect(self, verbose = False) -> bool:
        self.verbose = verbose

        if self.connected or self.telnet:
            return True
        
        try:
            self.telnet = telnetlib_mod.Telnet(self.host, self.port)
        except:
            return False
        
        self.connected = True

        t = threading.Thread(target=self.receiveThread, args=[self.connectionID])
        t.start()

        return True
    
    def disconnect(self, threadSafe = True):
        if threadSafe:
            self.socketLock.acquire()

        try:
            del self.telnet
        except:
            pass
        
        self.telnet = None
        self.connected = False
        self.connectionID += 1
        if threadSafe:
            self.socketLock.release()

    def send(self, msg, append = "\n", threadSafe = True) -> bool:
        if not self.connected or not self.telnet:
            return False
        
        if self.telnet.eof:
            self.disconnect(threadSafe = threadSafe)
            return False
        
        strToSend = ""

        if not isinstance(append, str):
            raise TypeError("send(msg): Отправлять можно только строку или массив строк.")
        
        if isinstance(msg, list):
            for item in list:
                if not isinstance(item, str):
                    raise TypeError("send(msg): Отправлять можно только строки или массив строк.")
            strToSend = append.join(msg) + append
        elif isinstance(msg, str):
            strToSend = msg + append
        else:
            raise TypeError("send(msg): Отправлять можно только строки или массив строк.")
        
        if len(strToSend) == 0:
            return True

        if threadSafe:
            self.socketLock.acquire()

        try:
            self.telnet.write(strToSend.encode())
        except:
            self.disconnect(threadSafe = False)

        if threadSafe:    
            self.socketLock.release()

        return self.connected

    def receiveThread(self, connectionID):
        remainder = b""
        unFinishedLine = ""

        while True:
            if connectionID != self.connectionID:
                return
            if not self.connected or not self.telnet:
                return
            
            try:
                r, w, e = select.select([self.telnet.sock], [], [])
            except:
                if connectionID == self.connectionID and self.connected:
                    self.disconnect()
                return

            if r:
                self.socketLock.acquire()
                try:
                    buff = self.telnet.read_very_eager()
                except:
                    self.disconnect(threadSafe = False)
                self.socketLock.release()

                if connectionID != self.connectionID:
                    return

                if len(buff) == 0:
                    time.sleep(0.01)
                    continue

                if len(remainder) > 0:
                    buff = remainder + buff
                    remainder = b""

                str = None

                try:
                    str = buff.decode("utf8")
                    str = str.replace("\r", "")
                except:   
                    slices = []
                    if len(buff) > 1:
                        slices.append(-1)
                    if len(buff) > 2:
                        slices.append(-2)
                    if len(buff) > 3:
                        slices.append(-3)
                    
                    for x in slices:
                        newbuff = buff[:x]
                        newremainder = buff[x:]
                        try:
                            str = newbuff.decode("utf8")
                            str = str.replace("\r", "")
                            remainder = newremainder
                            break
                        except:
                            pass

                if str == None:
                    if (len(buff) > 3):
                        print("receiveThread: Ошибка в данных от сервера. Разрываем соединение.")
                        self.disconnect()
                        return
                    remainder = buff
                else:
                    if self.verbose:
                        print(str, end="")

                    str = unFinishedLine + str
                    lines = str.split("\n")

                    if (len(lines) == 1):
                        if len(lines[0]) > 1000:
                            unFinishedLine = ""
                            self.loginProcessing(lines[0])
                            self.lineProcessing(MUDBot.stripANSI(lines[0]), lines[0])
                        else:
                            unFinishedLine = lines[0]
                    else:
                        unFinishedLine = lines[-1]
                        lines = lines[:-1]
                        for line in lines:
                            self.loginProcessing(line)
                            self.lineProcessing(MUDBot.stripANSI(line), line)

    """Переопределяется подклассом"""
    def loginProcessing(self, line):
        pass

    """Переопределяется подклассом"""
    def lineProcessing(self, line, ansi):
        pass

    @staticmethod
    def stripANSI(text:str) -> str:
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
