import unicodedata
import pywhatkit as whatsapp
import pyautogui
import webbrowser as wb
import time


def remove_accents(accented_string):
    return unicodedata.normalize('NFKD', accented_string).encode('ASCII', 'ignore').upper().decode("utf-8")


def sendMessageWhatsapp():
    try:
        # sending message to reciever
        # using pywhatkit
        # Example:
        # This will open web.whatsapp.com at 14:59:40 and message will be sent at exactly 15:00:00
        # pywhatkit.sendwhatmsg("+919876543210","This is a message",15,00)

        whatsapp.sendwhatmsg("+34697296245",
                             "Hi Steven, welcome to family Buscando Medicos",
                             22, 9)
        print("Successfully Sent!")
    except:
        # handling exception
        # and printing error message
        print("An Unexpected Error!")


def sendMessageWhatsapp2():
    wb.open("web.whatsapp.com")
    time.sleep(10)
    pyautogui.write("Hello")
    pyautogui.press("enter")

if __name__ == "__main__":
    # print(remove_accents("ódontologíá"))
    sendMessageWhatsapp2()
