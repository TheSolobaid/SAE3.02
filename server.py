import pymysql.cursors
import socket
import threading
import time
from datetime import datetime, timedelta

# Database infos
#MODIFY4PROD il faut modifier le user et le password de la database
connection_sql = pymysql.connect(host='localhost',
                                 user='root',
                                 password='toto',
                                 database='sae301_discord',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

# Socket infos
#MODIFY4PROD vérifier que le port est bien le bon
host = "0.0.0.0"
port = 1000
server_socket = socket.socket()
server_socket.bind((host, port))

# Declarations of variables
server_stop = False
hello_admin = " __    __   _______  __       __        ______   \n|  |  |  | |   ____||  |     |  |      /  __  \  \n|  |__|  | |  |__   |  |     |  |     |  |  |  | \n|   __   | |   __|  |  |     |  |     |  |  |  | \n|  |  |  | |  |____ |  `----.|  `----.|  `--'  | \n|__|  |__| |_______||_______||_______| \______/  "
clients = []
connected_pseudo = {}
pseudo = {}
ligne = '__________________________________________________'
lock = threading.Lock()
channels_are = ["General", "Blabla", "Comptabilite", "Marquetting","Informatique"]
resquesting_channel =False
at_least_one_client = False

# def wait_conf_sub(client, connection_sql):
#     global resquesting_channel
#     if resquesting_channel :
#         message = client.recv(1024).decode()
#         print(message)
#         if message == ":ignore":
#             print(f"{pseudo[client]} sais 'ok'")
#             resquesting_channel = False
#         else:
#             message = message.split(":subbing:")
#             print(f"{message[0]} is subbing to {message[1]}") 
#             resquesting_channel = False

def check_ban(client, connection_sql, pseudo):
    print(f"cheking ban for {pseudo}")
    with connection_sql.cursor() as cursor:
        sql_select = "SELECT `id`, `user`, `start_ban`, `duration` FROM ban WHERE `user` = %s;"
        cursor.execute(sql_select, pseudo)
        result = cursor.fetchall()
        if result:
            print(result)
            for row in result:
                ban_id = row['id']
                user = row['user']
                start_ban = row['start_ban']
                duration_minutes = row['duration']
                expiration_time = start_ban + timedelta(minutes=duration_minutes)
                if datetime.now() < expiration_time:
                    client.send(f"ban{round(((expiration_time - datetime.now()).seconds / 60),2)}".encode())
                    return(True)
                else:
                    print(f"{user} is not banned")
                    try:
                        with connection_sql.cursor() as remove_cursor:
                            sql_remove = f"DELETE FROM ban WHERE id = {ban_id};"
                            remove_cursor.execute(sql_remove)
                            connection_sql.commit()
                    except pymysql.Error as e:
                        print(f"MySQL Error: {e}")
                    return False


def verify_access(client,connection_sql,chanel):
    if chanel in channels_are:
        try:
            with connection_sql.cursor() as cursor:
                sql = "SELECT  `user`,`channel`,`etat` FROM `access` WHERE `user`=%s and `channel`=%s;"
                cursor.execute(sql,(pseudo[client], chanel))
                result = cursor.fetchall() # TODO finir et tester la verificationd d'access au chanells.
        except pymysql.Error as e:
            print(f"MySQL Error: {e}")
        else:
            if result:
                if result[0].get('etat') == 1 and result[0].get('channel') == chanel and result[0].get('user') == pseudo[client]:
                    client.send(':start_check'.encode())
                    time.sleep(0.001)
                    client.send(":subed".encode())
                else:
                    client.send(':start_check'.encode())
                    time.sleep(0.001)
                    client.send(":notsubed".encode())
                    time.sleep(0.001)
                    # wait_conf_sub(client,connection_sql)
                    client.send(":end_check".encode())

            else:
                client.send(':start_check'.encode())
                time.sleep(0.001)
                client.send(":notsubed".encode())
                time.sleep(0.001)
                client.send(":end_check".encode())

                
    else:
        client.send(':start_check'.encode())
        time.sleep(0.001)
        client.send(":subed".encode())
        time.sleep(0.001)
        client.send(":end_check".encode())
        time.sleep(0.001)
        


def get_chanel(client, connection_sql, pseudo = None):
    print("requestion channel")
    try:
        with connection_sql.cursor() as cursor:
            sql = "SELECT  `user` FROM `users`"
            cursor.execute(sql)

            result = cursor.fetchall()
    except pymysql.Error as e:
        print(f"MySQL Error: {e}")
    else:
        chanel_list = ""
        for i in channels_are:
            chanel_list = chanel_list + f",{i}"    
        for chanel in result:
                if chanel.get('user') != pseudo:
                    chanel_list = chanel_list+f",{chanel.get('user')}"
        print(chanel_list)
        print("sending channels")
        client.send(chanel_list.encode())


def get_history(client, connection_sql, channel, pseudo ):
    try:
        if channel not in channels_are:
            with connection_sql.cursor() as cursor:
                sql = "SELECT  `sender`,`message` FROM `messages` WHERE (`recever`=%s and `sender`=%s) or (`recever`=%s and `sender`=%s);"
                cursor.execute(sql, (channel, pseudo, pseudo, channel))
                result = cursor.fetchall()
        else:
            with connection_sql.cursor() as cursor:
                sql = "SELECT  `sender`,`message` FROM `messages` WHERE `recever`=%s"
                cursor.execute(sql, channel)
                result = cursor.fetchall()
    except pymysql.Error as e:
        print(f"MySQL Error: {e}")
    else:
        client.send(":start_history".encode())
        time.sleep(0.1)
        if result:
            for i in result:
                message = i.get('sender')+":said:"+i.get('message')
                client.send(message.encode())
                time.sleep(0.01)
            client.send(":end_history".encode())
        else:
            client.send(":end_history".encode())

def command_entry():
    global server_stop
    while not server_stop:
        connection_sql = pymysql.connect(host='localhost', user='root', password='toto', database='sae301_discord', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor) #MODIFY4PROD il faut modifier le user et le password de la database
        command = input()
        if  any(substring in command for substring in ['?', 'help','commande']):
            print("Les commandes disponnibles sont :\n  - /arret qui arretrera le serveur\n  - /liste user qui listera les pseudo utilisateur\n  - /ban nom_d'utilisateur temps(en minute) qui ban l'utiliasteur sur la periode de temps définie\n  - /liste demande qui listera les demandes pour les channels ")
        if command == "/arret":
            for client in clients:
                client.send(":server_stop".encode())
            server_stop = True
            arret_server()
        if command == "/liste demande":
            try:    
                with connection_sql:
                    with connection_sql.cursor() as cursor:
                        sql = "SELECT  `user`,`channel`FROM `access` WHERE `etat`=0;"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                
            except pymysql.Error as e:
                print(f"MySQL Error: {e}")
            else:
                if not result:
                    print("No pending requests.")
                else:
                    for row in result:
                        print(f"{row['user']} demande pour le channel {row['channel']}")
        if command == "/liste user":
            try:    
                with connection_sql:
                    with connection_sql.cursor() as cursor:
                        sql = "SELECT  `user`FROM `users`;"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                
            except pymysql.Error as e:
                print(f"MySQL Error: {e}")
            else:
                print("\nliste des users : \n")
                for row in result:
                    print(f"- {row['user']}")
                print()
        if command[:4] == "/ban":
            command = command.split(" ")
            try:    
                with connection_sql:
                    with connection_sql.cursor() as cursor:
                        sql = "SELECT  `user`FROM `users`;"
                        cursor.execute(sql)
                        result = cursor.fetchall()
                
            except pymysql.Error as e:
                print(f"MySQL Error: {e}")
            else:
                try: 
                    with connection_sql:
                        with connection_sql.cursor() as cursor:
                            sql_insert = "INSERT INTO ban (user, start_ban, duration) VALUES (%s, NOW(), %s);"
                            cursor.execute(sql_insert,[command[1],command[2]])
                        connection_sql.commit()
                        connection_sql.close()

                except pymysql.Error as e:
                    print(f"MySQL Error: {e}")
                else:
                    print(f"{command[1]} is ban for {command[2]}")

def get(client, connection_sql):
    global server_stop
    global pseudo
    global clients
    global connected_pseudo
    global resquesting_channel
    while not server_stop:
        if client in clients:
            if not resquesting_channel:
                try:
                    message = client.recv(1024).decode()
                    print(message)
                except ConnectionResetError:
                    print("Client forcibly disconnected")
                    print(clients)
                    clients.remove(client)
                except ConnectionAbortedError:
                    print("Client forcibly disconnected")
                    clients.remove(client)
                except OSError:
                    print("Client has probably disconnected")
                else:
                    if message[:1] == ":":
                        message = message[1:]
                        if message[:11] == "chanel_list":
                            get_chanel(client, connection_sql, pseudo[client])  
                        elif message[:11] == "get_history":
                            get_history(client, connection_sql, message[11:] ,pseudo[client])
                        elif message[:12] == 'check_access':
                            verify_access(client, connection_sql,  message[12:])
                        elif message == 'bye':
                            print(f"{pseudo[client]} has disconnected")
                            with lock:
                                clients.remove(client)
                                del pseudo[client]
                            client.send(":okbye".encode())
                            client.close()
                    else:
                        message = message.split(":to:")
                        with connection_sql.cursor() as cursor:
                            sql = "insert into messages (sender,message,recever) values (%s,%s,%s);"
                            cursor.execute(sql, (pseudo[client], message[0], message[1]))
                            connection_sql.commit()
                        message_send = f"{pseudo[client]}:to:{message[1]}:to:{message[0]}"
                        for client_receve in clients:
                                if client_receve != client:
                                    client_receve.send(message_send.encode())
                        

def id_process(client, connection_sql):
    global server_stop
    global pseudo
    global clients
    global connected_pseudo
    logged_in = False
    while not logged_in:
        if not server_stop:
            try:
                message = client.recv(1024).decode()
                print(f"message reçu {message}")
            except ConnectionResetError:
                print("Client forcibly disconnected")
                break
            except ConnectionAbortedError:
                print("Client forcibly disconnected")
                break
            except OSError:
                print("Client has probably disconnected")
            else:
                # LOGGING IN
                if message[:1] == ":":
                    message = message[1:]
                    if message[:5] == "login":
                        message = message[5:].split(':')
                        try:
                            with connection_sql.cursor() as cursor:
                                sql = "SELECT  `password` FROM `users` WHERE `user`=%s"
                                cursor.execute(sql, (message[0],))
                                result = cursor.fetchone()
                        except pymysql.Error as e:
                            print(f"MySQL Error: {e}")
                        else:
                            if message[0] not in connected_pseudo:
                                if result and result['password'] == message[1]:
                                    if not check_ban(client, connection_sql,message[0]):
                                        client.send('logged-in'.encode())
                                        pseudo[client] = message[0]
                                        print(f'bienvenue {message[0]}')
                                        with lock:
                                            connected_pseudo[pseudo[client]] = client
                                        logged_in = True
                                else:
                                    print('Wrong credentials')
                                    client.send("error".encode())

                            else:
                                print(f"{message[0]} is already connected. Please logout from your other devices.")
                                client.send('already connected'.encode())


                    # SIGNING IN
                    elif message[:6] == "signin":
                        message = message[6:].split(':')
                        try:
                            with connection_sql.cursor() as cursor:
                                sql = "SELECT  `password` FROM `users` WHERE `user`=%s"
                                cursor.execute(sql, (message[0],))
                                result = cursor.fetchone()
                        except pymysql.Error as e:
                            print(f"MySQL Error: {e}")
                        else:
                            if result:
                                client.send("already".encode())
                            else:
                                try:
                                    with connection_sql.cursor() as cursor:
                                        sql = "insert into users (user,password) values (%s,%s);"
                                        cursor.execute(sql, (message[0], message[1]))
                                        sql = "insert into access (user,channel, etat) values (%s,%s,%s)"
                                        cursor.execute(sql, (message[0], 'General', 1))
                                        connection_sql.commit()
                                except pymysql.Error as e:
                                    print(f"MySQL Error: {e}")
                                else:
                                    client.send('signed-in'.encode())
                                    print(f'bienvenue {message[0]}')
                                    pseudo[client] = message[0]
                                    logged_in = True
                                    #TODO faire en sorte que dans qq'un s'inscrit il apparêt même sur les gens connecter  ce moment

def connect(client):
    global server_stop
    global clients
    global connection_sql
    global connected_pseudo
    try:
        with pymysql.connect(host='localhost', user='root', password='toto', database='sae301_discord', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor) as connection_sql: #MODIFY4PROD il faut modifier le user et le password de la database
            identifiction_thread = threading.Thread(target=id_process, args=[client, connection_sql])
            identifiction_thread.start()
            identifiction_thread.join()

            with lock:
                clients.append(client)
            
            reception = threading.Thread(target=get, args=[client, connection_sql])
            reception.start()
            
            while not server_stop:
                if server_stop:
                    for client in clients:
                        client.send(":server_stop".encode())
            reception.join()
    except pymysql.Error as e:
        print(f"MySQL Error: {e}")
    finally:
        with lock:
            for client in clients:
                client.close()
            arret_server()


def arret_server():
    server = socket.socket()
    server.connect(("localhost", port))   
    server.close()


if __name__ == '__main__':
    admin_connected = False
    while not admin_connected:
        print("\nbienvenue sur le serveur\n")
        admin = input('login: ')
        pwd = input('password: ')
        if admin == "admin" and pwd == "admin":
            admin_connected = True
            print(f"\n\n{hello_admin}\n\n")
            print('press "?" or "help" to list all the command available')

    with connection_sql:
        with connection_sql.cursor() as cursor:
            sql = "CREATE TABLE IF NOT EXISTS users(id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, user varchar(40), password varchar(40))"
            cursor.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS messages(id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, sender varchar(40), recever varchar(40), message varchar(100) NOT NULL)"
            cursor.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS access (id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,user VARCHAR(40), channel VARCHAR(40), etat TINYINT(1))"
            cursor.execute(sql)
            sql = "CREATE TABLE IF NOT EXISTS ban (id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,user VARCHAR(40) NOT NULL, start_ban DATETIME NOT NULL, duration INT NOT NULL)"
            cursor.execute(sql)
            
        connection_sql.commit()
    server_socket.listen(5)
    command_entry_tread = threading.Thread(target=command_entry)
    
    command_entry_tread.start()
    while not server_stop:
        client_socket, address = server_socket.accept()
        if not server_stop:
            connection = threading.Thread(target=connect, args=[client_socket])
            connection.start()
            at_least_one_client = True

    if at_least_one_client:
        connection.join()
    server_socket.close()
