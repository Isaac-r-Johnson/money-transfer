import socket
import threading

HOST = '192.168.1.5'
PORT = 9999
DISCONNECT = "!dico"


def get_amounts():
    usernames = open("usernames.txt", "r")
    usernames = str(usernames.readlines())
    usernames = usernames.split("-")
    usernames[0] = usernames[0].replace("[", "")
    usernames[0] = usernames[0].replace("'", "")
    usernames.pop()

    amounts_to_transfer = {
    }

    for username in usernames:
        amounts_to_transfer[username] = 0

    return amounts_to_transfer


def client_fun(client, addr):
    global transfers
    print(f"{addr} just connected!")
    connected = True
    while connected:
        # client.send(DISCONNECT.encode('utf-8'))
        msg = client.recv(1024).decode('utf-8')
        if msg == "LOGIN_CHECK":
            client.send("OK".encode('utf-8'))
            usrn = client.recv(1024).decode('utf-8')
            screw_up = 0
            usernames = open("usernames.txt", "r")
            usernames = str(usernames.readlines())
            usernames = usernames.split("-")
            usernames[0] = usernames[0].replace("[", "")
            usernames[0] = usernames[0].replace("'", "")
            usernames.pop()
            if usrn in usernames:
                client.send("IN_USRNS".encode('utf-8'))
            elif usrn not in usernames and screw_up <= 3:
                screw_up += 1
                client.send("NOT_IN_USRNS".encode('utf-8'))
            else:
                client.send("NOT_FOUND".encode('utf-8'))
        elif msg == "SIGNUP_CHECK":
            client.send("OK".encode('utf-8'))
            usrn = client.recv(1024).decode('utf-8')
            try:
                usernames = open("usernames.txt", "a")
                usernames.write(usrn + "-")
                usernames.close()
                account_file = usrn + "_" + "account.txt"
                account = open(account_file, "w")
                account.write("100")
                account.close()
                client.send("SIGNUP_GOOD".encode('utf-8'))
            except:
                client.send("SIGNUP_BAD".encode('utf-8'))
        elif msg == "VIEW_CHECK":
            client.send("OK".encode('utf-8'))
            usrn = client.recv(1024).decode('utf-8')
            account_file = usrn + "_" + "account.txt"
            account = open(account_file, 'r')
            amount = str(account.readlines())
            amount = amount.replace(']', '')
            amount = amount.replace('[', '')
            amount = amount.replace("'", "")
            client.send(amount.encode('utf-8'))
        elif msg == "TRANSFER_CHECK1":
            client.send("OK".encode('utf-8'))

            m = client.recv(1024).decode('utf-8')
            usrn, person = m.split('-')

            usernames = open("usernames.txt", "r")
            usernames = str(usernames.readlines())
            usernames = usernames.split("-")
            usernames[0] = usernames[0].replace("[", "")
            usernames[0] = usernames[0].replace("'", "")
            usernames.pop()
            if person in usernames and person != usrn:
                client.send("PROCEED".encode('utf-8'))
            elif person == usrn:
                client.send("CAN_NOT_SEND_MONEY_TO_SELF".encode('utf-8'))
            else:
                client.send("USRN_NOT_FOUND".encode('utf-8'))
        elif msg == "TRANSFER_CHECK2":
            client.send("OK".encode('utf-8'))
            m = client.recv(1024).decode('utf-8')
            usrn, amount, person = m.split('-')

            # Subtract amount from account
            account_file = usrn + "_" + "account.txt"
            account_r = open(account_file, "r")
            account_r = str(account_r.readlines())
            account_r = account_r.replace(']', '')
            account_r = account_r.replace('[', '')
            account_r = account_r.replace("'", "")
            try:
                account_r = int(account_r)
            except:
                print("Can't Convert Str to Int!")
            new_amount = account_r - int(amount)
            if new_amount >= 0:
                account_w = open(account_file, "w")
                account_w.write(str(new_amount))
                account_w.close()
                # Transfer Money
                transfers = open("transfers.txt", "a")
                # I (usrn) transferred this amount to this person
                transfers.write(f'{usrn}-{amount}-{person}+')
                transfers.close()
                client.send("TRANSFERRED".encode('utf-8'))
            else:
                client.send("NOT_TRANSFERRED".encode('utf-8'))
        elif msg == "RECEIVE_CHECK":
            usrn = client.recv(1024).decode('utf-8')
            transfers_ = open("transfers.txt", "r")
            transfers = str(transfers_.readlines())
            transfers = transfers.split("+")
            transfers[0] = transfers[0].replace("[", "")
            transfers[0] = transfers[0].replace("'", "")
            transfers.pop()

            names = []
            for tran in transfers:
                tran_ = tran.split("-")
                i = 0
                while i <= len(tran):
                    names.append(tran_[2])
                    i += 1
            if usrn in names:
                client.send("OK".encode('utf-8'))
            else:
                client.send("NO".encode('utf-8'))

            if usrn in names:
                for tran in transfers:
                    tran_ = tran.split("-")
                    if usrn == tran_[2]:
                        name = str(tran_[0])
                        amount = str(tran_[1])
                        data = name + '-' + amount
                        client.send(data.encode('utf-8'))
                        account_file = usrn + "_" + "account.txt"
                        account_r = open(account_file, "r")
                        account_r = str(account_r.readlines())
                        account_r = account_r.replace(']', '')
                        account_r = account_r.replace('[', '')
                        account_r = account_r.replace("'", "")
                        try:
                            account_r = int(account_r)
                        except:
                            print("Can't Convert Str to Int!")
                            break
                        new_amount = int(tran_[1]) + account_r
                        account_w = open(account_file, "w")
                        account_w.write(str(new_amount))
                        account_w.close()
                        tran = tran + "+"
                        transFers_ = open("transfers.txt", "r")
                        transFers = str(transFers_.readlines())
                        transFers_.close()
                        transFers = transFers.replace(']', '')
                        transFers = transFers.replace('[', '')
                        transFers = transFers.replace("'", "")
                        transFers = transFers.replace(tran, '')
                        transFers_ = open("transfers.txt", 'w+')
                        transFers_.write(transFers)
                        transFers_.close()
                        print("Excepted!")
                        break
            else:
                print("Nothing Here!")

        elif msg == DISCONNECT:
            connected = False
    client.close()
    print(f"{address} disconnected!")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()
print("Server is listening.....")

while True:
    c_socket, address = server.accept()
    thread = threading.Thread(target=client_fun, args=(c_socket, address))
    thread.start()
