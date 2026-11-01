#-----------------------------------------------------------------#
#----------This script is used to create a TCP-IPv4-Server--------#
#-----------------------------------------------------------------#
#----------Chapter 1: Import neccessary moduls--------------------# 
#-----------------------------------------------------------------#
import socket
import threading
import protoChat
#-----------------------------------------------------------------#
#----------Chapter 2: Declarating variables-----------------------#
#-----------------------------------------------------------------#
clients = []
sessions = {}
clientsLock=threading.Lock()
sessionsLock=threading.Lock()
HOST='0.0.0.0'
PORT=65432
SEPARATOR_MESSAGES = '\n'
USER_NAME_SERVER='SERVER'
MESSAGE_TYPE_TOKEN='TOKEN'
MESSAGE_TYPE_ERROR='ERROR'
MESSAGE_TYPE_CHAT='MSG'
MESSAGE_TYPE_LOGIN='LOGIN'
USERS = {
    'Jura':'Passwort123',
    'JackSparow':'blackPearl',
    'Admin':'sudoPasswort123'
}
#-----------------------------------------------------------------#
#----------Chapter 3: Define the startServer function-------------#
#-----------------------------------------------------------------#
def startServer():
    print('INFO: Server is starting...')
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as passivSkt: # Create passive socket
        passivSkt.bind((HOST, PORT)) # Binding IP/Port to the created (passive) socket
        passivSkt.listen() # Open passive socket for incoming TCP connections
        print(f'DEBUG: Server ready at {HOST}:{PORT}')
        while True:
            activeSkt, clientAddr = passivSkt.accept() # Accept TCP connections from TCP stack
            print(f'INFO: New client connected: {clientAddr}')
            tempThread=threading.Thread(target=handleClients,args=(activeSkt,clientAddr),daemon=True)
            tempThread.start() # Start separate thread for each established TCP connection
            # Add new client to sessions-dictionary
            with sessionsLock:
                sessions[activeSkt] = {
                'userName':'',
                'loginStatus':False,
                'loginTime':'',
                'lastActivity':'',
                'clientAddr':clientAddr,
                'clientToken':''
                }
            print(f'DEBUG: {clientAddr} added to sessions dictionary')
#-----------------------------------------------------------------#
#----------Chapter 4: Define the handleClients function-----------#
#-----------------------------------------------------------------#
def handleClients(activeSkt, clientAddr):
    with clientsLock:
        clients.append(activeSkt)
        print(f'DEBUG: New thread started for {clientAddr}')
    receiveBuffer = ''
    try:
        while True:
            decodedData = activeSkt.recv(1024) # Receiving byte stream from TCP queue
            if not decodedData:
                break # Ends loop if no data in TCP queue available
            receiveBuffer+=decodedData.decode() # Decode byte stream to UTF-8
            while "\n" in receiveBuffer: 
                idxSeparator = receiveBuffer.find(SEPARATOR_MESSAGES)
                framedMessage = receiveBuffer[:idxSeparator]                
                receiveBuffer = receiveBuffer[idxSeparator+1:]
                parserReturn = protoChat.parseMessage(framedMessage)
                if parserReturn is None:
                    continue # Restarts the loop
                userName, messageType, payLoad = parserReturn
                #handlers = { --> handler über Dict statt ueber if auswählen
                    #"LOGIN": handleLogin, 
                    #"MSG": handleMessage,
                    #"LOGOUT": handleLogout,
                    #"PING": handlePing}
                #handler = handlers[messageType] --> passenden handler aufrufen
                #handler(...)
                if messageType == MESSAGE_TYPE_LOGIN:
                    print(f'DEBUG: Login started for {clientAddr}')
                    handleLogin(activeSkt,userName,payLoad)                    
                elif messageType == 'MSG':
                    print(f'DEBUG: Message handler started for {clientAddr}')
                    handleMessage(activeSkt,userName,payLoad)
    finally:
        print(f'DEBUG: Connection to client {clientAddr} was terminated!')
        with clientsLock:
            clients.remove(activeSkt)        
        with sessionsLock:
            del sessions[activeSkt]
        activeSkt.close()
#-----------------------------------------------------------------#
#-----------------------------------------------------------------#
#-----------------------------------------------------------------#
def handleLogin(activeSkt, userName, userPassword):
    if userName in USERS and USERS[userName]==userPassword:    
        clientToken = userName+userPassword
        print(f'DEBUG: Token for {userName}: {clientToken}')
        tokenMessage = protoChat.buildMessage(USER_NAME_SERVER,MESSAGE_TYPE_TOKEN,clientToken)
        activeSkt.sendall(tokenMessage.encode())
        with sessionsLock:
            sessions[activeSkt]['userName']=userName
            sessions[activeSkt]['loginStatus']=True
            sessions[activeSkt]['clientToken']=clientToken
        print(f'INFO: loginStatus for {userName} changed to TRUE')
    else:
        print(f'ERROR: Client not authenticated.')
        tokenMessage = protoChat.buildMessage(USER_NAME_SERVER,MESSAGE_TYPE_ERROR,'Client not authenticated!')
        activeSkt.sendall(tokenMessage.encode())
#-----------------------------------------------------------------#
#-----------------------------------------------------------------#
#-----------------------------------------------------------------#
def handleMessage(activeSkt,userName,payLoad):
    clientAddr=sessions[activeSkt]['clientAddr']
    userName=sessions[activeSkt]['userName']
    if sessions[activeSkt]['loginStatus']==True:
        framedMessage=protoChat.buildMessage(userName,MESSAGE_TYPE_CHAT,payLoad)
        broadcast(framedMessage,activeSkt,clientAddr)
    elif sessions[activeSkt]['loginStatus']==False:
        print(f'ERROR: User {userName} not logged in')
#-----------------------------------------------------------------#
#----------Chapter X: Define the broadcast function---------------#
#-----------------------------------------------------------------#
def broadcast(framedMessage, activeSkt, clientAddr):
    print(f'DEBUG: Client {clientAddr} started broadcast...')
    with clientsLock:
        tempClients = clients.copy()
    for client in tempClients:
        if client != activeSkt:
            client.sendall(framedMessage.encode())
#-----------------------------------------------------------------#
#----------Chapter 7: Conditions to start the skript--------------# 
#-----------------------------------------------------------------#
if __name__=='__main__':
    startServer()
#-----------------------------------------------------------------#
#-------------------------------END-------------------------------#
#-----------------------------------------------------------------#