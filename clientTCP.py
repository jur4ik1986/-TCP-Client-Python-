#-----------------------------------------------------------------#
#---------------Modul to create a TCP/IP ClientSocket-------------#
#-----------------------------------------------------------------#
#--------------Chapter 1: Import neccessary moduls----------------# 
#-----------------------------------------------------------------#
import socket
import threading
import protoChat as chat
#-----------------------------------------------------------------#
#----------Chapter 2: Declarating variables-----------------------#
#-----------------------------------------------------------------#
sessionToken=''
_HOST = '127.0.0.1'
_PORT = 65432
_MESSAGE_TYPE_LOGIN='LOGIN'
_MESSAGE_TYPE_CHAT='MSG'
_SEPARATOR_MESSAGES = '\n'
#-----------------------------------------------------------------#
#----------Chapter 3: Define the startClient function-------------# 
#-----------------------------------------------------------------#
def startClient():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSkt:
        clientSkt.connect((_HOST, _PORT))
        print(f'Enter user name:')
        userName=input()
        print(f'Bitte Passwort fuer {userName} eingeben')
        userPassword = input()
        loginMessage = chat.buildMessage(userName,_MESSAGE_TYPE_LOGIN, userPassword)
        if loginMessage is None:
            print('Error: Message type not supported')
        clientSkt.sendall(loginMessage.encode())
        thread=threading.Thread(target=handleMessages, args=(clientSkt,),daemon=True)
        thread.start()
        print(f'Connection established to server {_HOST}:{_PORT}')
        while True:
            userMessage = input()
            userMessageFramed = chat.buildMessage(userName,_MESSAGE_TYPE_CHAT,userMessage)
            if userMessageFramed is None:
                print('Error: Message type not supported')
            clientSkt.sendall(userMessageFramed.encode())
#-----------------------------------------------------------------#
#----------Chapter 4: Define the handleMessages function----------# 
#-----------------------------------------------------------------#
def handleMessages(clientSkt):
    #print(f'DEBUG: Message handler started for {clientSkt}.')
    receiveBuffer = ''
    while True:
        try:
            decodedData = clientSkt.recv(1024)
            if not decodedData:
                break
            receiveBuffer+=decodedData.decode() # Decode byte stream to UTF-8
            while "\n" in receiveBuffer: 
                positionSeparator = receiveBuffer.find(_SEPARATOR_MESSAGES)
                framedMessage = receiveBuffer[:positionSeparator]                
                receiveBuffer = receiveBuffer[positionSeparator+1:]
                parserReturn = chat.parseMessage(framedMessage)
                if parserReturn is None:
                    continue
                userName, messageType, payLoad = parserReturn
                if messageType == 'TOKEN' and userName == 'SERVER':
                    sessionToken = payLoad
                elif messageType == _MESSAGE_TYPE_CHAT:
                    print(f'New broadcast: {payLoad}')
        except:
            #print(f'DEBUG: Message handler break for {clientSkt}')
            break
#-----------------------------------------------------------------#
#----------Chapter 5: Conditions to start the skript--------------# 
#-----------------------------------------------------------------#       
if __name__ == "__main__":
    startClient()
#-----------------------------------------------------------------#
#-------------------------------END-------------------------------#
#-----------------------------------------------------------------#