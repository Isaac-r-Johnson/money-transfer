import socket
import threading
from tkinter import *
from tkinter import messagebox
import time

universal_font_size = 20
universal_font = "Arial"
universal_entry_width = 50
universal_btn_width = 40
default_pady = (50, 0)
spacing = (15, 0)
border_width = 6
bg = "lightgray"
logged_in = False
root = Tk()
root.geometry('1000x250')
root.title("Money Transfer Machine")
root.iconbitmap("icon.ico")
root.config(bg=bg)

HOST = '192.168.1.24'
PORT = 9999

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    socket.connect((HOST, PORT))

    # GUI
    def login__check(usrn):
        global logged_in
        usrn = usrn.get().lower()
        socket.send("LOGIN_CHECK".encode('utf-8'))
        confirm = socket.recv(1024).decode('utf-8')
        if confirm == "OK":
            socket.send(usrn.encode('utf-8'))
            logged_in_msg = socket.recv(1024).decode('utf-8')
            if logged_in_msg == "IN_USRNS":
                menu(usrn)
            elif logged_in_msg == "NOT_IN_USRNS":
                messagebox.showwarning("Warning", "Your username couldn't be found. Please try again", icon="warning")
                login()
            elif logged_in_msg == "NOT_FOUND":
                messagebox.showwarning("Warning",
                                       "You have failed to input the proper user name three times. Please signup now!",
                                       icon="warning")
                signup()


    def signup__check(usrn):
        usrn = usrn.get().lower()
        popup = messagebox.askquestion("Continue", f"Are you sure you want your username to be {usrn}?")
        if popup == "yes":
            socket.send("SIGNUP_CHECK".encode('utf-8'))
            confirm = socket.recv(1024).decode('utf-8')
            if confirm == "OK":
                socket.send(usrn.encode('utf-8'))
                server_response = socket.recv(1024).decode('utf-8')
                if server_response == "SIGNUP_GOOD":
                    messagebox.showwarning("Info", "Username Created Successfully!", icon="info")
                    login()
                elif server_response == "SIGNUP_BAD":
                    messagebox.showwarning("Warning", "Username Created Unsuccessfully! Please try again",
                                           icon="warning")
                    signup()
        else:
            check_in()


    def menu__check(usrn, inp):
        global logged_in
        inp = inp.get().lower()
        if inp == "tran":
            transfer(usrn)
        elif inp == "reci":
            receive(usrn)
        elif inp == "lo":
            logged_in = False
            check_in()
        elif inp == "account":
            view_account(usrn)
        else:
            messagebox.showwarning("Info", "Please type either 'tran', 'reci', or 'account'", icon="info")
            menu(usrn)


    def view__check(usrn):
        socket.send("VIEW_CHECK".encode('utf-8'))
        confirm = socket.recv(1024).decode('utf-8')
        if confirm == "OK":
            socket.send(usrn.encode('utf-8'))
            amount = socket.recv(1024).decode('utf-8')
            return amount


    def back__btn(usrn):
        menu(usrn)


    def tran__check1(usrn, person):
        person = str(person.get().lower())
        socket.send("TRANSFER_CHECK1".encode('utf-8'))
        confirm = socket.recv(1024).decode('utf-8')
        if confirm == "OK":
            socket.send(f"{usrn}-{person}".encode('utf-8'))

            server_response = socket.recv(1024).decode('utf-8')
            if server_response == "PROCEED":
                transfer2(usrn, person)
            elif server_response == "CAN_NOT_SEND_MONEY_TO_SELF":
                messagebox.showwarning("Error!", "You can not send money to your self!", icon="error")
                transfer(usrn)
            elif server_response == "USRN_NOT_FOUND":
                messagebox.showwarning("Warning", "Username was not found. Please check spelling and try again.",
                                       icon="warning")
                transfer(usrn)


    def tran__check2(usrn, amount, person):
        amount = amount.get()
        check = messagebox.askquestion("Send Money", f"Are you sure you want to send ${amount} to {person}?",
                                       icon='question')
        if check == "yes":
            socket.send("TRANSFER_CHECK2".encode('utf-8'))
            confirm = socket.recv(1024).decode('utf-8')
            if confirm == "OK":
                socket.send(f"{usrn}-{amount}-{person}".encode('utf-8'))
                server_response = socket.recv(1024).decode('utf-8')
                if server_response == "TRANSFERRED":
                    messagebox.showwarning(f"Success", f"Money was successfully sent to {person}", icon="info")
                    menu(usrn)
                elif server_response == "NOT_TRANSFERRED":
                    messagebox.showwarning("Error",
                                           f"You don't have enough money in your account to transfer ${amount}",
                                           icon="error")
                    menu(usrn)

    # Normal Functions
    def menu(usrn):
        clear()
        heading = Label(root, text="Would you like to transfer money or receive money? ('tran', 'reci', 'account'):",
                        font=(universal_font, universal_font_size), bg=bg)
        inp = Entry(root, width=universal_entry_width, borderwidth=border_width,
                    font=(universal_font, universal_font_size))
        next_btn = Button(root, text="Next", command=lambda: menu__check(usrn, inp), padx=universal_btn_width,
                          pady=universal_btn_width / 4)
        heading.pack(pady=default_pady)
        inp.pack(pady=spacing)
        next_btn.pack(pady=spacing)


    def check_in():
        global logged_in
        if not logged_in:
            clear()
            Label(root, text='', bg=bg).pack()
            login_btn = Button(root, text="Login", command=login, padx=universal_btn_width,
                               pady=universal_btn_width / 4)
            signup_btn = Button(root, text="Signup", command=signup, padx=universal_btn_width,
                                pady=universal_btn_width / 4)
            login_btn.pack(pady=(20, 10))
            signup_btn.pack(pady=20)


    def clear():
        for ele in root.winfo_children():
            ele.destroy()


    def login():
        clear()
        heading = Label(root, text="Please Enter Username:", font=(universal_font, universal_font_size), bg=bg)
        usrn = Entry(root, width=universal_entry_width, borderwidth=border_width,
                     font=(universal_font, universal_font_size))
        next_btn = Button(root, text="Next", command=lambda: login__check(usrn), padx=universal_btn_width,
                          pady=universal_btn_width / 4)
        heading.pack(pady=default_pady)
        usrn.pack(pady=spacing)
        next_btn.pack(pady=spacing)


    def signup():
        clear()
        heading = Label(root, text="Please Enter Username you would like to use:",
                        font=(universal_font, universal_font_size), bg=bg)
        usrn = Entry(root, width=universal_entry_width, borderwidth=border_width,
                     font=(universal_font, universal_font_size))
        next_btn = Button(root, text="Next", command=lambda: signup__check(usrn), padx=universal_btn_width,
                          pady=universal_btn_width / 4)
        heading.pack(pady=default_pady)
        usrn.pack(pady=spacing)
        next_btn.pack(pady=spacing)


    def view_account(usrn):
        clear()
        amount = view__check(usrn)
        text = Label(root, text=f"You have ${amount} in your account!", font=(universal_font, universal_font_size),
                     bg=bg)
        btn = Button(root, text="Back", command=lambda: back__btn(usrn), padx=universal_btn_width,
                     pady=universal_btn_width / 4)
        text.pack(pady=default_pady)
        btn.pack(pady=spacing)


    def receive(usrn):
        socket.send("RECEIVE_CHECK".encode('utf-8'))
        socket.send(usrn.encode('utf-8'))

        c = socket.recv(1024).decode('utf-8')
        if c == "OK":
            try:
                data = socket.recv(1024).decode('utf-8')
                name, amount = data.split('-')
                messagebox.showwarning("Continue?", f"{name} has sent you ${amount}", icon="question")
                messagebox.showwarning("Info", f"${amount} has just been transferred to your account!", icon="info")
                menu(usrn)
            except:
                print("Error!")
        else:
            messagebox.showwarning("Info", f"Nothing for you today!", icon="info")
            menu(usrn)


    def transfer(usrn):
        clear()
        heading = Label(root, text="Who would you like to transfer money to? (Enter username of person):",
                        font=(universal_font, universal_font_size), bg=bg)
        person = Entry(root, width=universal_entry_width, borderwidth=border_width,
                       font=(universal_font, universal_font_size))
        next_btn = Button(root, text="Next", command=lambda: tran__check1(usrn, person), padx=universal_btn_width,
                          pady=universal_btn_width / 4)
        heading.pack(pady=default_pady)
        person.pack(pady=spacing)
        next_btn.pack(pady=spacing)


    def transfer2(usrn, person):
        clear()
        heading = Label(root, text="How much would you like in transfer? (please enter and integer):",
                        font=(universal_font, universal_font_size), bg=bg)
        amount = Entry(root, width=universal_entry_width, borderwidth=border_width,
                       font=(universal_font, universal_font_size))
        btn = Button(root, text="Continue", command=lambda: tran__check2(usrn, amount, person),
                     padx=universal_btn_width, pady=universal_btn_width / 4)
        heading.pack(pady=default_pady)
        amount.pack(pady=spacing)
        btn.pack(pady=spacing)


    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
            socket.send("!dico".encode('utf-8'))


    if not logged_in:
        check_in()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

except:
    messagebox.showwarning('Warning', 'Could not connect to the server. Server may currently be under maintenance.',
                           icon='warning')
    root.destroy()
