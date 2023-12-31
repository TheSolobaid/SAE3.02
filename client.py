import sys
from PyQt6.QtWidgets import *
import socket
import threading
import time

#MODIFY4PROD il faut modifier l'ip du serveur et le port
host = "127.0.0.1"
port = 1000
login = False
signedin = False
connected = False
server_socket = socket.socket()
connected = False
logedin = False
username = ""
stop_app = False

class mainWindow(QMainWindow):
    global connected

    def __init__(self):
        super().__init__()
        self.central_widget = QStackedWidget()
        self.setWindowTitle("App De Discution")
        self.setCentralWidget(self.central_widget)
        self.login = login_window(self)
        self.signin = signin_window(self)
        self.acceuil = acceuil_window(self)
        self.discution = discutionwindow(self)

        self.stacked_widget = self.central_widget
        self.stacked_widget.setLayout(self.stacked_widget.layout())

        self.central_widget.addWidget(self.acceuil)
        self.central_widget.addWidget(self.login)
        self.central_widget.addWidget(self.signin)
        self.central_widget.addWidget(self.discution)
        self.central_widget.setCurrentWidget(self.acceuil)
        self.server_socket = server_socket




    def switch_acceuil(self):
        self.central_widget.setCurrentWidget(self.central_widget.widget(0))

    def switch_login(self):
        self.central_widget.setCurrentWidget(self.central_widget.widget(1))

    def switch_signin(self):
        self.central_widget.setCurrentWidget(self.central_widget.widget(2))

    def switch_discussion(self):
        
        self.central_widget.setCurrentWidget(self.central_widget.widget(3))
        self.discution.get_chanels()

class acceuil_window(QMainWindow):
    def __init__(self, parent=None):
        super(acceuil_window, self).__init__(parent)
        self.setGeometry(200,200,400,300)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        self.Text_acceuil = QLabel("Bienvenue sur l'app de discution", self)
        self.error_message = QLabel("", self)
        self.error_message.setStyleSheet("color: red;")
        self.connected_message = QLabel("", self)
        self.connected_message.setStyleSheet("color: green;")
        self.log_in_button = QPushButton("Se connecter",self)
        self.log_in_button.clicked.connect(self.login)
        self.sign_in_button = QPushButton("S'inscrire",self)
        self.sign_in_button.clicked.connect(self.signin)
        self.close_button = QPushButton("Quitter",self)
        self.close_button.clicked.connect(self.quit)
        self.connect_buton = QPushButton("Connecter le server",self)
        self.connect_buton.clicked.connect(self.connect)
        self.layout.addWidget(self.Text_acceuil,0,0)
        self.layout.addWidget(self.error_message,1,0)
        self.layout.addWidget(self.connected_message,1,0)
        self.layout.addWidget(self.log_in_button, 2,0)
        self.layout.addWidget(self.sign_in_button,2,1)
        self.layout.addWidget(self.close_button,3,0)
        self.layout.addWidget(self.connect_buton,3,1)


    def connect(self):
        self.error_message.clear()
        try:
            server_socket.connect((host, port))
        except ConnectionRefusedError:
            self.show_error_message("server offline")
        else:
            global connected

            connected = True
            self.connected_message.setText("Connected to server !!")

    def show_error_message(self, message):
        self.error_message.setText(message)

    def login(self):
        if connected:
            self.parentWidget().parentWidget().switch_login()
        else:
            self.show_error_message("please connect the server first")

    def signin(self):
        if connected:
            self.parentWidget().parentWidget().switch_signin()
        else:
            self.show_error_message("please connect the server first")


    def quit(self):
        global stop_app
        stop_app= True
        server_socket.send(":bye".encode())
        time.sleep(0.1)
        QApplication.exit(0)

class signin_window(QMainWindow):
    def __init__(self, parent=None):
        super(signin_window, self).__init__(parent)
        self.setGeometry(200,200,400,300)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout(central_widget)

        self.Text_acceuil = QLabel("Inscrivez vous a l'app", self)
        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Username")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.correction)
        self.password_confirmation_input = QLineEdit(self)
        self.password_confirmation_input.setPlaceholderText("Password confirmation")
        self.password_confirmation_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_confirmation_input.textChanged.connect(self.correction)
        self.password_confirmation_input.returnPressed.connect(self.signin)
        self.error_message = QLabel("", self)
        self.error_message.setStyleSheet("color: red;")
        self.signin_button = QPushButton("sign-in", self)
        self.signin_button.clicked.connect(self.signin)
        self.login_button = QPushButton("Se connecter",self)
        self.login_button.clicked.connect(parent.switch_login)
        self.close_button = QPushButton("Quitter",self)
        self.close_button.clicked.connect(self.quit)


        self.layout.addWidget(self.Text_acceuil,0,0,1,2)
        self.layout.addWidget(self.user_input,1,0,1,2)
        self.layout.addWidget(self.password_input,2,0,1,2)
        self.layout.addWidget(self.password_confirmation_input,3,0,1,2)
        self.layout.addWidget(self.error_message,4,0,1,2)
        self.layout.addWidget(self.signin_button,5,0)
        self.layout.addWidget(self.login_button,5,1)
        self.layout.addWidget(self.close_button,6,0,1,2)


    def signin(self):
        user = self.user_input.text()
        password = self.password_input.text()
        password_confirmation = self.password_confirmation_input.text()
        if password and password_confirmation and user:
            if password != password_confirmation:
                self.show_error_message(message="error password")
            else:
                message = ":signin" + user + ":" + password
                try:
                    server_socket.send(message.encode())
                    print("message envoyé")
                except ConnectionAbortedError or  ConnectionResetError:
                    self.show_error_message("Server has disconnected")
                else:
                    try:
                        print("attente du message")
                        message = self.parent().parent().server_socket.recv(1024).decode()
                        print(f"message reçu {message}")
                    except ConnectionAbortedError:
                        self.show_error_message("No server connected")
                    except ConnectionResetError:
                        self.show_error_message("Server has stopped")
                    else:
                        if message == 'signed-in':
                            global username
                            username = user
                            self.parentWidget().parentWidget().switch_discussion()

                        elif message == 'already':
                            self.show_error_message(f"pseudo {user} already used please change")

        elif not user:
            self.show_error_message(message="please enter a valid username")
        elif not password or password_confirmation:
            self.show_error_message(message="please enter a password")


    def show_error_message(self, message):
        self.error_message.setText(message)

    def correction(self):
        self.error_message.clear()

    def quit(self):
        global stop_app
        stop_app= True
        server_socket.send(":bye".encode())
        QApplication.exit(0)


class login_window(QMainWindow):
    def __init__(self, parent=None):
        super(login_window, self).__init__(parent)
        self.setGeometry(200,200,400,300)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout(central_widget)

        self.Text_acceuil = QLabel("Connectez vous a l'app", self)
        self.user_input = QLineEdit(self)
        self.user_input.setPlaceholderText("Username")
        self.user_input.textChanged.connect(self.correction)
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.correction)
        self.password_input.returnPressed.connect(self.login)
        self.error_message = QLabel("", self)
        self.error_message.setStyleSheet("color: red;")
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        self.signin_button = QPushButton("S'inscrire",self)
        self.signin_button.clicked.connect(parent.switch_signin)
        self.close_button = QPushButton("Quitter",self)
        self.close_button.clicked.connect(self.quit)

        self.layout.addWidget(self.Text_acceuil,0,0,1,2)
        self.layout.addWidget(self.user_input,1,0,1,2)
        self.layout.addWidget(self.password_input,2,0,1,2)
        self.layout.addWidget(self.error_message,3,0,1,2)
        self.layout.addWidget(self.login_button,4,0)
        self.layout.addWidget(self.signin_button,4,1)
        self.layout.addWidget(self.close_button,5,0,1,2)

    def quit(self):
        global stop_app
        stop_app= True
        server_socket.send(":bye".encode())
        QApplication.exit(0)

    def login(self):
        user = self.user_input.text()
        password = self.password_input.text()

        if user and password:
            message = ":login" + user + ":" + password
            try:
                self.parent().parent().server_socket.send(message.encode())
                print("message envoyé")
            except ConnectionAbortedError or  ConnectionResetError:
                self.show_error_message("Server has disconnected")
            else:
                try:
                    print("attente du message")
                    message = self.parent().parent().server_socket.recv(1024).decode()
                    print(f"message reçu {message}")
                except ConnectionAbortedError:
                    self.show_error_message("No server connected")
                except ConnectionResetError:
                    self.show_error_message("Server has stopped")
                else:
                    if message == 'logged-in':
                        global username
                        username = user
                        self.parentWidget().parentWidget().switch_discussion()
                    elif message == "error":
                        self.show_error_message(f"Wrong password for {user}. Please retry.")
                    elif message == 'already connected':
                        self.show_error_message(f"{user} is already connected. Please logout from your other devices.")
                    elif message[:3] == 'ban':
                        time_left = message[3:]
                        self.show_error_message(f"{user} is banned for {time_left} minutes")



    def show_error_message(self, message):
        self.error_message.setText(message)

    def correction(self):
        self.error_message.clear()



class discutionwindow(QMainWindow):
    def __init__(self, parent=None):
        super(discutionwindow, self).__init__(parent)
        self.chanel_list_got = False
        self.on_channel = ""
        self.start_history= False
        self.start_check = False
        self.tous_chanels = []
        self.setGeometry(200,200,400,300)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout(central_widget)

        self.close_button = QPushButton("Quitter",self)
        self.close_button.clicked.connect(self.quit)
        self.logout_button = QPushButton("logout",self)
        self.logout_button.clicked.connect(parent.switch_acceuil)
        self.channel_list_titre = QLabel("Chanels / MP", self)
        self.channel_list = QListWidget(self)
        self.message_list_titre = QLabel("messages from ...",self)
        self.message_list = QListWidget(self)

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("enter you message")
        self.message_input.returnPressed.connect(self.message_enter)
        




        self.layout.addWidget(self.logout_button,0,0,1,1)
        self.layout.addWidget(self.close_button,0,1,1,1)
        self.layout.addWidget(self.channel_list_titre,1,0,1,1)
        self.layout.addWidget(self.message_list_titre,1,1,1,4)
        self.layout.addWidget(self.channel_list,2,0,4,1)
        self.layout.addWidget(self.message_list,2,1,4,4)
        self.layout.addWidget(self.message_input,6,1,1,4)

    def message_enter(self):
        global username
        if self.message_input.text():
            self.message_list.addItem(f"{username} : {self.message_input.text()}")
            self.send_message(message = self.message_input.text())
            self.message_input.clear()
            scrollbar = self.message_list.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def send_message(self, message):
        message = message+ ":to:" +self.on_channel
        server_socket.send(message.encode())

    def quit(self):
        global stop_app
        stop_app = True
        server_socket.send(":bye".encode())
        self.receive_thread.join()
        QApplication.exit(0)

    def server_stop(self):
        global stop_app
        stop_app = True
        QApplication.exit(0)
        #TODO add le fait de quitter proprememnt (bye) + faire que la thread s'arrête proprement pour que le programme ne soit pas obligé d'etre kill a la main
    
    def get_chanels(self):
        global username

        if connected:
            self.logout_button.setText(f"logout from {username}")
            while not self.chanel_list_got:
                print("requestion chanels")
                message = ":chanel_list"+username
                try:
                    server_socket.send(message.encode()) 
                    print("message envoyé")
                except ConnectionAbortedError or  ConnectionResetError:
                    self.show_error_message(message = "Server has disconnected")
                else:
                    try:
                        print("attente du message")
                        message = server_socket.recv(1024).decode()
                        print(f"message reçu {message}")
                    except ConnectionAbortedError or  ConnectionResetError:
                        print('ya une erreur, il faut que je fassse ça propre') #TODO ça
                    else:
                        self.chanel_list_got = True
                        message = message.split(",")
                        self.tous_chanels = message
                        print(message)
                        for i in message:
                            if i != "":
                                button_item = QPushButton(f"{i}", self)
                                button_item.clicked.connect(lambda _, i=i :self.access_channel(i))

                                
                                list_widget_item = QListWidgetItem()
                                list_widget_item.setSizeHint(button_item.sizeHint())
                                
                                self.channel_list.addItem(list_widget_item)
                                self.channel_list.setItemWidget(list_widget_item, button_item)
            print('requesting starting receving thread')
            self.start_thread()
    
    def historique_message(self, channel):
        message = f":get_history{channel}"
        try:
            server_socket.send(message.encode())
        except ConnectionAbortedError or  ConnectionResetError:
            self.show_error_message("Server has disconnected")
        else:
            history_finish = False
            while not history_finish:
                try:
                    message = server_socket.recv(1024).decode()
                    print(f"historique {message}")
                except ConnectionAbortedError or  ConnectionResetError:
                    print('ya une erreur, il faut que je fassse ça propre') 
                else:
                    
                    if message[:12] == ":end_history":
                        history_finish = True
                        self.start_history = False
                        self.start_check = False

                    elif message ==':start_history' or message == ':start_check':
                        self.start_history= True
                        self.start_check = True

                    elif message[:1] == ":":
                        print(f'message {message} ignored')
                    else:
                        message = message.split(':said:')
                        result = message[0] + ' : '+ message[1]
                        self.message_list.addItem(result)
                        scrollbar = self.message_list.verticalScrollBar()
                        scrollbar.setValue(scrollbar.maximum())
        scrollbar = self.message_list.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    

    
    
    
    def receive_messages(self):
        global stop_app
        while not stop_app:
            global connected
            while connected:
                if not self.start_history and not self.start_check:
                    try:
                        message = server_socket.recv(1024).decode()
                    except ConnectionResetError:
                        connected = False
                    except ConnectionAbortedError:
                        connected = False
                    else:
                        if message[:1] == ":":
                            message = message[1:]
                            if message[:13] == "start_history":
                                self.start_history= True
                                print(f"(tread receve) {message}")
                            if message[:11] == "start_check":
                                self.start_check= True
                                print(f"(tread receve) {message}")
                            if message[:12] == ":end_history":

                                self.start_history = False
                                self.start_check = False
                            if message == "okbye":
                                connected = False
                            if message == "server_stop":
                                print("server stopping")
                                connected = False
                                stop_app = True
                                self.server_stop()
                        else:
                            print(f"(tread receve) {message}")
                            message = message.split(":to:")
                            if (self.on_channel == message[0] and username == message[1]) or (self.on_channel == message[1] and message[1] in self.tous_chanels):
                                result = message[0] + ' : '+ message[2]
                                self.message_list.addItem(result)
                                scrollbar = self.message_list.verticalScrollBar()
                                scrollbar.setValue(scrollbar.maximum())

    
    
    def start_thread(self):
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()


    def access_channel(self, channel):
        if self.check_access(channel):
            print('access granted')
            self.message_list.clear()
            self.message_list_titre.setText(f"messages from {channel}")
            self.historique_message(channel = channel)
            self.on_channel = channel
        else:
            self.show_error_popup(channel)

    def check_access(self, channel):
        check_finished = False
        while not check_finished:
            message = f":check_access{channel}"
            server_socket.send(message.encode())
            
            message = server_socket.recv(1024).decode()
            if message == ":subed":
                check_finished = True
                return True
            elif message == ":notsubed":
                check_finished = True
                return False

    def show_error_popup(self, channel):
        popup = QMessageBox(self)
        popup.setWindowTitle('You are not authorized')
        popup.setText('Ask for access')
        sub_button = QPushButton(f"request access to {channel}", self)
        ok_button = QPushButton("OK",self)
        popup.addButton(sub_button, QMessageBox.ButtonRole.ActionRole)
        popup.addButton(ok_button, QMessageBox.ButtonRole.AcceptRole)
        #HACK here there is a problem, WHY
        sub_button.clicked.connect(lambda _, i=channel: self.sub_to_channel(i))
        ok_button.clicked.connect(self.ok_no_requesting)
        popup.exec()

    

    def ok_no_requesting(self):
        # server_socket.send(':confimation'.encode())
        # time.sleep(0.1)
        # server_socket.send(":ignore".encode())
        print("ok")

    def sub_to_channel(self, channel):
        # server_socket.send(':confimation'.encode())
        # time.sleep(0.1)
        # message = username + ":subbing:" + channel
        # server_socket.send(message.encode())
        print(f"Subbing to channel {channel}")
def main():
    app = QApplication(sys.argv)

    fenetre = mainWindow()
    fenetre.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
