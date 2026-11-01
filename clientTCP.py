#-----------------------------------------------------------------#
#---------------Modul to create a TCP/IP ClientSocket-------------#
#-----------------------------------------------------------------#
#--------------Chapter 1: Import neccessary moduls----------------# 
#-----------------------------------------------------------------#
import socket
import threading
import protoChat
#-----------------------------------------------------------------#
#----------Chapter 2: Declarating variables-----------------------#
#-----------------------------------------------------------------#
sessionToken=''
HOST = '127.0.0.1'
PORT = 65432
MESSAGE_TYPE_LOGIN='LOGIN'
MESSAGE_TYPE_CHAT='MSG'
SEPARATOR_MESSAGES = '\n'
#-----------------------------------------------------------------#
#----------Chapter 3: Define the startClient function-------------# 
#-----------------------------------------------------------------#
def startClient():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSkt:
        clientSkt.connect((HOST, PORT))
        print(f'Enter user name:')
        userName=input()
        print(f'Bitte Passwort fuer {userName} eingeben')
        userPassword = input()
        loginMessage = protoChat.buildMessage(userName,MESSAGE_TYPE_LOGIN, userPassword)
        clientSkt.sendall(loginMessage.encode())
        thread=threading.Thread(target=handleMessages, args=(clientSkt,),daemon=True)
        thread.start()
        #print(f'Connection established to server {HOST}:{PORT}')
        while True:
            userMessage = input()
            userMessageFramed = protoChat.buildMessage(userName,MESSAGE_TYPE_CHAT,userMessage)
            clientSkt.sendall(userMessageFramed.encode())
#-----------------------------------------------------------------#
#----------Chapter 4: Define the handleMessages function----------# 
#-----------------------------------------------------------------#
def handleMessages(clientSkt):
    print(f'DEBUG: Message handler started for {clientSkt}.')
    receiveBuffer = ''
    while True:
        try:
            decodedData = clientSkt.recv(1024)
            if not decodedData:
                break
            receiveBuffer+=decodedData.decode() # Decode byte stream to UTF-8
            while "\n" in receiveBuffer: 
                positionSeparator = receiveBuffer.find(SEPARATOR_MESSAGES)
                framedMessage = receiveBuffer[:positionSeparator]                
                receiveBuffer = receiveBuffer[positionSeparator+1:]
                parserReturn = protoChat.parseMessage(framedMessage)
                if parserReturn is None:
                    continue
                userName, messageType, payLoad = parserReturn
                if messageType == 'TOKEN' and userName == 'SERVER':
                    sessionToken = payLoad
                elif messageType == MESSAGE_TYPE_CHAT:
                    print(f'New broadcast: {payLoad}')
        except:
            print(f'DEBUG: Message handler break for {clientSkt}')
            break
#-----------------------------------------------------------------#
#----------Chapter 5: Conditions to start the skript--------------# 
#-----------------------------------------------------------------#       
if __name__ == "__main__":
    startClient()
#-----------------------------------------------------------------#
#-------------------------------END-------------------------------#
#-----------------------------------------------------------------#