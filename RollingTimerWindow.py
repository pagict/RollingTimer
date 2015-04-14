from Tkinter import *

class RollingTimerUI(object):
    def __init__(self, master):
        self.master = master
        self.master.geometry("{}x{}+0+0".format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.build_function_select_window()
        mainloop()
    def build_function_select_window(self):
        self.header = Canvas(self.master, width=900, height=80, bg='#f0a030')
        self.header.create_text(50,50, text="RollingTimer", width=800)
        self.header.pack()



RollingTimerUI(Tk())