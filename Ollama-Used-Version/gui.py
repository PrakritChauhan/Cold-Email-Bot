import threading
import queue
import time
from cold_email_bot import ColdEmailBot
from tkinter import *
from tkinter import scrolledtext, messagebox

# ----------------- Queue for safe cross-thread updates -------------------
status_queue = queue.Queue()

def update_status(message):
    status_queue.put(message)

def process_queue():
    while not status_queue.empty():
        msg = status_queue.get()
        status_box.insert(END, msg + "\n")
        status_box.see(END)
    window.after(10, process_queue)  # Tight 10ms interval for snappy updates

# --------------------------- Submit Logic --------------------------

def threaded_submit():
    email_count = int(email_count_spinbox.get())
    email_length = int(email_length_spinbox.get())
    if email_count < 1:
        messagebox.showerror("Error", "Please enter a valid number of emails")
        return
    elif email_length < 25:
        messagebox.showerror("Error", "Please enter a valid length of emails")
        return

    email_bot = ColdEmailBot(email_count, email_length)
    thread = threading.Thread(target=email_bot.send_email, args=(update_status,), daemon=True)
    thread.start()

def start():
    process_queue()
    window.mainloop()
#--------------------------UI--------------------------------
window = Tk()
window.geometry("750x450")
window.resizable(False, False)
window.title("Cold Emails Bot")

title_label = Label(text="Cold Emails Bot", font=("Montserrat", 30, "bold"))
email_count_label = Label(text="Number of emails to send:", font=("Montserrat", 15, "bold"))
email_length_label = Label(text="Email length (words):", font=("Montserrat", 15, "bold"))
title_label.grid(row=0, column=1, padx=10, pady=10)
email_count_label.grid(row=1, column=0, padx=10, pady=10)
email_length_label.grid(row=2, column=0, padx=10, pady=10)

submit_button = Button(text="Initiate Process",  font=("Montserrat", 20, "bold"), command=threaded_submit)
submit_button.grid(row=3, column=1, padx=20, pady=20)

email_count_spinbox = Spinbox(window, from_=0, to=100, increment=10, width=10)
email_length_spinbox = Spinbox(window, from_=0, to=150, increment=5, width=10)
email_count_spinbox.grid(row=1, column=1, padx=20, pady=20)
email_length_spinbox.grid(row=2, column=1, padx=20, pady=20)

status_box = scrolledtext.ScrolledText(window, width=104, height=10)
status_box.place(x=0, y=300)


