from Tkinter import *


class RollingTimerUI(Frame):
    def __init__(self, master):
        self.master = master

        self.master.geometry("{}x{}+0+0".format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        # define a 4 rows * 3 cols grid, the 1st col twice width as the 2nd and the 3rd col
        self.master.grid_columnconfigure(0, minsize=self.master.winfo_screenwidth()/2)
        self.master.grid_columnconfigure(1, minsize=self.master.winfo_screenwidth()/4, )
        self.master.grid_columnconfigure(2, minsize=self.master.winfo_screenwidth()/4, )
        self.master.grid_rowconfigure(1, minsize=self.master.winfo_screenheight()/4, pad=5)
        self.master.grid_rowconfigure(2, minsize=self.master.winfo_screenheight()/4-10, pad=5)
        self.master.grid_rowconfigure(3, minsize=self.master.winfo_screenheight()/4-10, pad=5)
        self.master.grid_rowconfigure(0, minsize=self.master.winfo_screenheight()/4-10, pad=5)

        self.header = None       # shared through the whole app
        # widgets in function selection page
        self.restore_btn = None
        self.backup_btn = None
        self.selection_widgets = [self.restore_btn, self.backup_btn]
        # widgets in backup page
        self.device_list = None  # shared with restore page
        self.entry = None
        self.message = None      # shared with restore page, progress page
        self.cancel = None       # shared with restore page
        self.backup = None       # shared with restore page
        self.backup_widgets = [self.device_list, self.entry, self.message, self.cancel, self.backup]
        # widgets in restore page
        self.version_list = None
        self.restore_widgets = [self.device_list, self.version_list, self.message, self.cancel, self.backup]
        # widgets in the progress page
        self.progress_bar = None
        self.progress_widgets = [self.message, self.progress_bar]

        self.to_backup_page()
        mainloop()

    @staticmethod
    def __remove_widgets(widget_list):
        """
        Remove the widgets from the current window, for the preparation
        of the next window.
        :param widget_list:
        """
        if not widget_list:
            return
        for w in widget_list:
            if w:
                w.grid_forget()

    def to_restore_page(self, remove_list=None):
        pass

    def to_backup_page(self, remove_list=None):
        self.__remove_widgets(remove_list)
        self.header = Canvas(self.master,  bg='#f0a030')
        self.header.grid(columnspan=3, sticky='NWE')
        self.device_list = Label(self.master, text='LIST', bg='#ff0000')
        self.device_list.grid(row=1, column=0, rowspan=3, sticky="WNSE")
        self.entry = Label(self.master, text="ENTRY", bg='#00ff00')
        self.entry.grid(row=1, column=1, columnspan=2, sticky='WNSE')
        self.message = Label(self.master, text="MESSAGE", bg='#0000ff')
        self.message.grid(row=2, column=1, columnspan=2, sticky='WNSE')
        self.cancel = Button(self.master, text="CANCEL",
                                 command=lambda: self.to_selection_page(self.backup_widgets))
        self.cancel.grid(row=3, column=1, sticky='WNSE')
        self.backup = Button(self.master, text="BACKUP",
                                 command=lambda: self.to_progress_page(self.backup_widgets))
        self.backup.grid(row=3, column=2, sticky='WNSE')

    def to_progress_page(self, remove_list=None):
        pass

    def to_selection_page(self, remove_list=None):
        """
        The first page of the App, function selection page.
        If first enter this page, the remove_list should be None.
        If back from the Restore page or the Backup Page, remove_list
        should be the widgets need to be removed from that page.
        :param remove_list:
        :return:
        """
        self.__remove_widgets(remove_list)
        self.header = Canvas(self.master,  bg='#f0a030')
        self.header.grid(columnspan=3, sticky='NWE')
        self.restore_btn = Button(self.master, text="Restore",
                                  command=lambda: self.to_restore_page(self.selection_widgets))
        self.restore_btn.grid(row=1, column=0, rowspan=3, sticky="WNSE")
        self.backup_btn = Button(self.master, text="Backup",
                                 command=lambda: self.to_backup_page(self.selection_widgets))
        self.backup_btn.grid(row=1, column=1, rowspan=3, columnspan=2, sticky="WNSE")


RollingTimerUI(Tk())