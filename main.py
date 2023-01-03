#-- Libarys --

import sys, os, shutil
from win10toast import ToastNotifier
import requests
import webbrowser as web
import tinydb
import tkinter as tk
from tkinter import messagebox, Checkbutton
from PIL import ImageTk,Image
from time import time

#-- Important Stuff / Saves --

try:
    os.mkdir("C:/IS it Live")
except:
    pass # Dir is allready made / its starting from the Windows startup
try:
    shutil.copy(os.path.basename(sys.argv[0]), "C:/IS it Live/Is it Live.py")
except:
    pass # file allready copied / its starting from the Windows startup
try:
    shutil.copy("twitch.ico", "C:/IS it Live/twitch.ico")
except:
    pass # Ico is allready copied / its starting from the Windows startup
try:
    shutil.copy("twitch.png", "C:/IS it Live/twitch.png")
except:
    pass # png is allready copied / its starting from the Windows startup

os.chdir("C:/IS it Live")

#-- Variable --

db = tinydb.TinyDB("save.json")

Query = tinydb.Query()

allready_open = []

auto_start = True
open_browser = True

#-- Code --

def pause(secs):
    init_time = time()
    while time() < init_time+secs: pass

class App(tk.Tk):
    def __init__(self):
        super(App, self).__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.trayMenu = None

        global auto_start_box
        
        icon = ImageTk.PhotoImage(Image.open(r"twitch.png"))
        self.iconphoto(False, icon)
        self.title("  Is it Live?")
        self.config(bg="purple")
        self.geometry("400x600")
        
        auto_start_box = tk.BooleanVar()
        check_auto_start = Checkbutton(self,bg="purple",activebackground="purple",width=400,text="Auto Start",variable=auto_start_box,onvalue=True, offvalue=False, command=make_auto_start)
        check_auto_start.place(x=150, y=100, width=100, height=30)


    def on_closing(self):
        if not self.trayMenu: # when system tray is not exists.
            selection = messagebox.askyesnocancel("Tips", "Quit directly?\nYes : Quit.\nNo : Minimize to system tray.")  # "Yes" will return True, "Cancel" will return None, "No" will return False.
            if selection: # when select yes, quit the app directly.
                self.destroy()
            elif selection == False: # Minimize to system tray.
                # make a system tray
                self.withdraw()
                # use bulitin tk.Menu

                # The work about "Winico"
                self.tk.call('package', 'require', 'Winico') # use the tcl "winico", make sure the folder of "winico" is in the same path.
                icon = self.tk.call('winico', 'createfrom', 'twitch.ico') # this is the icon on the system tray.
                self.tk.call('winico', 'taskbar', 'add', icon, # set the icon
                            '-callback', (self.register(self.menu_func), '%m', '%x', '%y'), # refer to winico documentation.
                            '-pos', 0,
                            '-text', u'Is it Live?') # the hover text of the system tray.

                # About menu
                self.trayMenu = tk.Menu(self, tearoff=False)
                self.trayMenu.add_command(label="Show my app", command=self.deiconify)

                # You could also add a cascade menu
                cascadeMenu = tk.Menu(self, tearoff=False)
                cascadeMenu.add_command(label="Casacde one", command=lambda :print("You could define it by yourself"))
                cascadeMenu.add_command(label="Cascade two")
                self.trayMenu.add_cascade(label="Other", menu=cascadeMenu)

                self.trayMenu.add_separator() # you could add a separator

                self.trayMenu.add_command(label="Quit", command=self.destroy)

                # you could also add_command or add_checkbutton for what you want
            else: # This is cancel operation
                pass
        else:
            self.withdraw() # when system tray exists, hide the window directly.

    def menu_func(self, event, x, y):
        if event == 'WM_RBUTTONDOWN': # Mouse event, Right click on the tray.Mostly we will show it.
            self.trayMenu.tk_popup(x, y) # pop it up on this postion
        if event == 'WM_LBUTTONDOWN': # Mouse event, Left click on the tray,Mostly we will show the menu.
            self.deiconify() # show it.
        # All the Mouse event:

        # WM_MOUSEMOVE
        # WM_LBUTTONDOWN
        # WM_LBUTTONUP
        # WM_LBUTTONDBLCLK
        # WM_RBUTTONDOWN
        # WM_RBUTTONUP
        # WM_RBUTTONDBLCLK
        # WM_MBUTTONDOWN
        # WM_MBUTTONUP
        # WM_MBUTTONDBLCLK

def check_live():
    client_id = ''
    client_secret = ''
    # needs saved data
    streamer_name = []

    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        "grant_type": 'client_credentials'
    }
    r = requests.post('https://id.twitch.tv/oauth2/token', body)
    
    #data output

    keys = r.json()
    headers = {
        'Client-ID': client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }
    are_live = []
    for item in streamer_name:
        stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + item, headers=headers)
        stream_data = stream.json()
        if len(stream_data['data']) == 1:
            are_live.append(item)
    return are_live
    
def make_auto_start():
    path = f"{os.path.expanduser(os.getenv('USERPROFILE'))}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
    auto_start = auto_start_box.get()
    if auto_start == True:    
        with open(path + "is it live.bat","w") as f:
            f.write(f'python "C:/IS it Live/Is it Live.py" 123')
    elif auto_start == False:
        os.remove(path + "is it live.bat")

def main():
    if check_live() == []:
        print("No one is live")
        return
    for item in check_live():
        if item not in allready_open:
            # needs saved data as Bool, to check if open with browser
            if open_browser == True:
                web.open("https://twitch.tv/" + item)
            allready_open.append(item)
            n = ToastNotifier()
            n.show_toast(f"{item} ist live!", "Schau jetzt in seinen Stream!",duration=10 ,icon_path='twitch.ico')
        else:
            print("No one is live")

if __name__ == "__main__":
    arg = sys.argv
    if len(arg) == 1:
        app = App()
        app.mainloop()
        while True:
            pause(3)
            main()
    elif len(arg) >= 2:
        if auto_start == False:
            exit()
        while True:
            pause(3)
            main()

"""
--- My Sources ---

https://stackoverflow.com/questions/62372144/how-to-add-system-tray-to-my-tkinter-application-and-avoid-using-lots-of-pywin32
https://stackoverflow.com/questions/12064130/is-there-any-way-to-check-if-a-twitch-stream-is-live-using-python
https://fossil.mpcjanssen.nl/winico/tree?ci=tip&mtime=0&type=tree&udc=1

"""
