from config import user_config
from transfer_engine import server_test
from directory_manager import directory_scanner
import transfer_engine

from tkinter import Tk, Button, Entry, Label, filedialog
import os
import threading
import queue
import time

# Load in the user config.json into a dict
#NOTE -> dict's are thread safe as long as only one thread writes to the dict.
config = user_config.load_config()

documents_path = os.path.join(os.path.expanduser("~"), "Documents")

# UI TRIGGERED FUNCTIONS
warning = None

def show_file_manager():
    global warning

    folder = filedialog.askdirectory(title="Select target directory", initialdir=documents_path)
    if "Documents" in folder:
        if folder not in config["target_dirs"]:
            config["target_dirs"].append(folder)
            user_config.update_config(config)
            render_target_list()

            if warning:
                warning.destroy()     
        else:
            if warning:
                warning.destroy()

            warning = Label(fg="red", text="Directory is already targeted.")
            warning.grid(row=0, column=0, columnspan=3)   
                
    elif folder != "":
        if warning:
            warning.destroy()

        warning = Label(fg="red", text="Invalid directory, must be in the Documents")
        warning.grid(row=0, column=0, columnspan=3)

def delete_backup(index):
    config["target_dirs"].pop(index)  
    user_config.update_config(config)
    render_target_list()     
   
def render_target_list():
    # removes old list if present
    for widget in window.grid_slaves():
        if int(widget.grid_info()["row"] >= 3):
            widget.destroy()

    for index, dir in enumerate(config["target_dirs"]):
        remove_dir_button = Button(text="-", fg="red", command=lambda i=index: delete_backup(i))
        remove_dir_button.grid(row=index + 3, column=0, sticky="e")
        target_dir = Label(text="-> " + dir)
        target_dir.grid(row=index + 3, column=1, columnspan=2, sticky="w")  


def test_url():
    ip = server_ip.get()
    status = server_test(ip)
    #NOTE -> with the debounce timer set to 400ms and the req timeout set to 300ms a race condition is not posable.
    # Also when the server_ip color is changed the thread has to sink with tkinter and can cause GUI lag if not debounced to avoid updating while the user is typing.
    if status:
        server_ip.config(fg="limegreen")
        config["server_ip"] = ip
        user_config.update_config(config) # auto save the ip if valid
    else:
        server_ip.config(fg="red")
input_debounce = None

# This creates a thread each time the function is called and runs the test url without blocking the UI.
def spin_up_test_thread():
    threading.Thread(target=test_url, daemon=True).start()    

# This is used to avoid race conditions and to prevent posable GUI lag while the user is typing.
def schedule_test_thread():
    global input_debounce
    if input_debounce:
        window.after_cancel(input_debounce)
    input_debounce = window.after(400, spin_up_test_thread)   


#-------------- TKINTER UI LAYOUT's-----------------

def main_window():
    global window, server_ip

    window = Tk()
    window.title("File Backup System")
    window.config(padx=50, pady=50)

    server_ip_label = Label(text="Backup Server LAN IP")
    server_ip_label.grid(row=1, column=0, sticky="e")

    server_ip = Entry()
    if config["server_ip"] != None:
        server_ip.insert(0, config["server_ip"])
        server_ip.config(fg="green")
        schedule_test_thread() 
    else:
        server_ip.config(fg="red")    
    server_ip.grid(row=1, column=1)

    # Entry events
    server_ip.bind("<KeyRelease>", lambda event: schedule_test_thread())

    button = Button(window, text="Add Directory", command=show_file_manager)
    button.grid(row=1, column=2, sticky="w")

    target_dirs_label = Label(text="Target Directories", font=("Arial", 20, "bold"))
    target_dirs_label.grid(row=2, column=0, columnspan=3)

    render_target_list()

    window.mainloop()

# NOTE -> tkinter runs on the main thread. i have set up a thread that listens for a terminal command
# if the command is valid it will be added to a queue to render the gui on the main thread.    
command = queue.Queue()

def gui_render_handler():
    global command

    while True:
        msg = command.get()
        
        if msg == "config":
            main_window()

def listen_for_commands():
    global command

    while True:
        msg = input().lower()
        
        if msg == "config":
            command.put(msg)

update_trigger = queue.Queue()

def directory_management():
    # grabbing the current targets_map list from the json file
    targets_map = directory_scanner.read_directory_map()
    # if the file has just bean created then the file will nead to be uptaded
    if len(targets_map["targets"]) != len(config["target_dirs"]):
        directory_scanner.update_directory_map(config["target_dirs"])
        targets_map = directory_scanner.read_directory_map()

    old_config = list(config["target_dirs"])

    while True:
        if sorted(config["target_dirs"]) != sorted(old_config):
            directory_scanner.update_directory_map(config["target_dirs"])
            targets_to_update = []
            for target in config["target_dirs"]:
                if target not in old_config:
                    targets_to_update.append(target)        

            targets_map = directory_scanner.read_directory_map()

            for target in targets_map["targets"]:
                if target["path"] in targets_to_update:
                    transfer_engine.backup_target(target["path"], config["server_ip"])
            
            old_config = list(config["target_dirs"])
        time.sleep(1)    

threading.Thread(target=listen_for_commands, daemon=True).start()
threading.Thread(target=directory_management, daemon=True).start()

gui_render_handler()
