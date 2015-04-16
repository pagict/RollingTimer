from Tkinter import *
from ttk import Progressbar

class RollingTimerUI(Frame):
    TAG_DEFAULT = 'Tag this backup'
    BACKUP_HELP = 'MESSAGE'

    def __init__(self, master):
        self.master = master

        self.master.geometry("{}x{}+0+0".format(self.master.winfo_screenwidth(), self.master.winfo_screenheight()))
        self.__config_grid()

        self.header = None       # shared through the whole app
        self.header = Label(self.master, background='#f0a030', font=('', 20), foreground='#0020f0')
        self.header.grid(columnspan=4, sticky='EWNS')

        # widgets in function selection page
        self.restore_btn = None
        self.backup_btn = None
        self.selection_widgets = []
        # widgets in backup page
        self.device_list = None  # shared with restore page
        self.entry = None
        self.message = None      # shared with restore page, progress page
        self.cancel = None       # shared with restore page
        self.do_operation = None       # shared with restore page
        self.backup_widgets = []
        # widgets in restore page
        self.version_list = None
        self.restore_widgets = [self.device_list, self.version_list, self.message, self.cancel, self.do_operation]
        # widgets in the progress page
        self.progress_bar = None
        self.progress_widgets = [self.message, self.progress_bar]

        self.to_selection_page()
        mainloop()

    def __config_grid(self):
        # define a 4 rows * 3 cols grid, the 1st col twice width as the 2nd and the 3rd col
        self.master.grid_columnconfigure(0, weight=4)
        self.master.grid_columnconfigure(1, weight=2)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        self.master.grid_rowconfigure(0, weight=1,)
        self.master.grid_rowconfigure(1, weight=1,)
        self.master.grid_rowconfigure(2, weight=1,)
        self.master.grid_rowconfigure(3, weight=1,)

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
        """
        Restore Page, also need to remove the widgets from the previous page first.
        A device panel on the left. When selected, backups available on the selected
        device will listed in the right list panel.
        :param remove_list:
        :return:
        """
        self.__remove_widgets(remove_list)
        self.__config_grid()
        self.device_list = Listbox(self.master, font=('', 15))
        self.device_list.grid(row=1, column=0, columnspan=1, sticky='WESN', padx=5)
        for item in self.devices():
            self.device_list.insert(END, item)
        self.message = Text(self.master, )
        self.message.grid(row=2, column=0, columnspan=1, sticky='WEN', padx=5)
        self.message.insert(END, 'MESSAGE')
        self.message.config(state='disabled')
        self.version_list = Listbox(self.master)
        self.version_list.grid(row=1, column=1, columnspan=3, sticky='WENS', padx=10)
        for item in self.versions():
            self.version_list.insert(END, item)
        self.cancel = Button(self.master, text="Cancel",
                             command=lambda: self.to_selection_page(self.restore_widgets))
        self.cancel.grid(row=3, column=2, sticky='ES', padx=10)
        self.do_operation = Button(self.master, text='Restore',
                                   command=lambda: self.to_progress_page('Restore', self.restore_widgets))
        self.do_operation.grid(row=3, column=3, sticky='ES', padx=10)
        self.restore_widgets = [self.device_list, self.message, self.version_list, self.cancel, self.do_operation]

    def to_backup_page(self, remove_list=None):
        """
        Backup Page, also need to remove the widgets from the previous page first.
        A list lists available backup storage devices on the left,
        and you can set a tag to describe this backup version.
        :param remove_list:
        :return:
        """
        self.__remove_widgets(remove_list)
        self.__config_grid()
        self.header.config(text='Select a Device to store the backup')
        self.device_list = Listbox(self.master, font=('', 20))
        self.device_list.grid(row=1, column=0, rowspan=3, columnspan=1,
                              sticky="WNSE", padx=5, pady=5)
        for item in self.devices():
            self.device_list.insert(END, item)
        self.entry = Entry(self.master,  bd=2, validate='focus',
                           vcmd=lambda: self.clean_default_entry(self.entry, self.TAG_DEFAULT))
        self.entry.insert(END, self.TAG_DEFAULT)
        self.entry.grid(row=1, column=1, columnspan=3, sticky='WE', padx=20,)
        self.message = Text(self.master, bg='#f0f0ff', bd=0)
        self.message.insert(END, self.BACKUP_HELP)
        self.message.config(state='disabled')
        self.message.grid(row=2, column=1, columnspan=3, sticky='WNSE', padx=20, pady=10)
        self.cancel = Button(self.master, text="CANCEL",
                             command=lambda: self.to_selection_page(self.backup_widgets))
        self.cancel.grid(row=3, column=2, sticky='SE', padx=20)
        self.do_operation = Button(self.master, text="BACKUP",
                                   command=lambda: self.to_progress_page('Backup', self.backup_widgets))
        self.do_operation.grid(row=3, column=3, sticky='SE', padx=20)

        self.backup_widgets = [self.device_list, self.entry, self.message, self.cancel, self.do_operation]

    def to_progress_page(self, title, remove_list=None,):
        """
        Progress page, showing the Restore/Backup operation progress
        Need to remove widgets from the previous page first.
        :param remove_list:
        :return:
        """
        self.__remove_widgets(remove_list)
        self.__config_grid()
        self.header.config(text=title)
        self.progress_bar = Progressbar(self.master)
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky='WES', padx=10)
        self.message = Label(self.master, text="Running")
        self.message.grid(row=2, column=0, sticky='WN', padx=10)
        self.progress_widgets = [self.message, self.progress_bar]

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
        self.__config_grid()
        self.header.config(text="Select a function")
        self.restore_btn = Button(self.master, text="Restore", font=('', 20), padx=0,
                                  command=lambda: self.to_restore_page(self.selection_widgets))
        self.restore_btn.grid(row=1, column=0, rowspan=3, sticky="WNSE")
        self.backup_btn = Button(self.master, text="Backup", font=('', 20), padx=0,
                                 command=lambda: self.to_backup_page(self.selection_widgets))
        self.backup_btn.grid(row=1, column=1, rowspan=3, columnspan=3, sticky="WNSE")
        self.selection_widgets = [self.restore_btn, self.backup_btn]

    def devices(self):
        """
        Get all available devices
        :return: a list of available devices
        """
        return ['item1', 'ITEM2']

    def versions(self):
        """
        Get all available backup versions in the selected device
        :return: a list of available backups
        """
        return ['backup1', 'backup2']

    def clean_default_entry(self, entry, default_msg):
        """
        Check the entry once focused. If the message is default, clear the entry
        :param entry:
        :param default_msg:
        :return:
        """
        print("In validator")
        if not isinstance(entry, Entry):
            return
        msg = entry.get()
        if msg == default_msg:
            entry.delete(0, END)

RollingTimerUI(Tk())