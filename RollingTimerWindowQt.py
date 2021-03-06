#!/bin/python2
import threading
from PyQt4 import QtCore
from PyQt4.QtGui import *
from string import Template
import sys
import sip
import BackupOperation
import RestoreOperation
import Operation

BACKUP_MESSAGE = 'Select a device listed on the left where to store ' \
                 'the backups. And you can optionally add a tag of this ' \
                 'backup as above.'
RESTORE_MESSAGE = 'Select a device listed above where your backups stored ' \
                  'and a particular backup on the right.'


theme_color = '#0b7cc2'

styles = "QWidget {border: none;" \
         "background: none;}" \
         "QPushButton {color:#111;" \
         "background-color: #ddd;}" \
         "QLabel {font-size: 20px;" \
         "color: #505050;}" \
         "QProgressBar::chunk, QProgressBar {border-radius: 10px;" \
         "text-align: center;}"


class RollingTimerWindow(QDialog):
    """
    A Dialog used to simulate Assistant Window.
    When go to another page, the invoker page should pass its toplevel layout
    to the destination page, which is responsible to remove all sub widgets
    and sub layouts of that toplevel layout first.
    """

    def __init__(self):
        """
        Init the data field self.versions to None
        :return:
        """
        super(RollingTimerWindow, self).__init__()
        self.setWindowTitle('RollingTimer')
        self.versions_list = None
        self.version_list_widget = None
        self.devices_list = None
        self.showFullScreen()
        # self.to_selection_page()

    def to_selection_page(self, previous_layout=None, title='RollingTimer'):
        """
        The function selection page, to choose whether need to restore
        or backup.
        :rtype previous_layout QLayout: toplevel layout of the previous page
                                        need to be removed
        :rtype title str: Title of the page
        """
        self.__remove_widgets(previous_layout)

        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()

        # Header Widget
        image = QWidget(self)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image.setAutoFillBackground(True)
        image_style = styles + 'QWidget {background-color:'+theme_color+';}'
        image.setStyleSheet(image_style)
        # Restore Button
        big_button_style = Template(r'$style QPushButton {font-size:45px;}'
                                    r' QPushButton:hover {color:'
                                    r'$color;}').substitute(style=styles,
                                                            color=theme_color)

        to_restore = QPushButton(QtCore.QString("Restore"), self)
        to_restore.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        to_restore.setStyleSheet(big_button_style)
        # Backup Button
        to_backup = QPushButton(QtCore.QString("Backup"), self)
        to_backup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        to_backup.setStyleSheet(big_button_style)

        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        h2.addWidget(to_restore, 1)
        h2.addWidget(to_backup, 1)

        to_backup.clicked.connect(lambda: self.to_backup_page(v1))
        to_restore.clicked.connect(lambda: self.to_restore_page(v1))

    def to_backup_page(self, previous_layout=None, title='Backup'):
        """
        The backup page. A list of all available devices on the left,
        and a entry for tag this version of backup.
        :rtype previous_layout QLayout: Toplevel layout from previous page.
                        Need to be removed.
        :rtype title str: The page title
        """
        self.__remove_widgets(previous_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.setStyleSheet(styles)
        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()

        # Header Widget
        image = QWidget(self)
        image.setAutoFillBackground(True)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        img_style = styles + 'QWidget {background-color:'+theme_color+';}'
        image.setStyleSheet(img_style)
        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        v1.addWidget(buttons)

        # List of all available backup devices
        device_list = QListWidget(self)
        device_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        device_list.setSelectionMode(QListWidget.SingleSelection)
        device_list.setStyleSheet(styles)
        self.set_device_list(device_list, BackupOperation.BackupOperation())
        h2.addWidget(device_list)
        h2.addLayout(v3)

        # Entry for tagging this backup version
        entry = QLineEdit(self)
        entry.setStyleSheet(styles)
        # Help message
        message = QLabel(BACKUP_MESSAGE, self)
        message.setWordWrap(True)
        message.setStyleSheet(styles)
        v3.addWidget(entry)
        v3.addWidget(message)

        buttons.rejected.connect(lambda: self.to_selection_page(v1))
        buttons.accepted.connect(lambda:
                                 self.__accepted_backup(device_list, entry, v1))

    def set_device_list(self, list_widget, operation):
        self.devices_list = operation.devices()
        for item in self.devices_list:
            item_str = 'Name:{} -- Size:{}'.format(item['NAME'], item['SIZE'])
            QListWidgetItem(list_widget).setText(item_str)

    def __accepted_backup(self, device_list_widget, entry, toplevel_layout):
        # If no selection, auto select the first item
        if not device_list_widget.selectedItems():
            # Now we don't offer auto selection for stability reason
            # device_list_widget.setItemSelected(device_list_widget.item(0), True)
            message_box = QMessageBox()
            message_box.setText('Please select a device to store your backups!')
            message_box.exec_()
            return

        i = int()
        # Find the selection
        for i in range(len(self.devices_list)):
            if device_list_widget.isItemSelected(device_list_widget.item(i)):
                break
        # get the correlated data and the tag
        selected_device = self.devices_list[i]
        tag_string = entry.text()

        src_dict = {'NAME': '/dev/sda1', 'MOUNTPOINT': ''}
        # If available, get the src_dict from cache
        for i in self.devices_list:
            if i['NAME'] == 'sda1':
                src_dict = i
                break

        op = BackupOperation.BackupOperation()
        op.set_destination(selected_device)
        op.set_src(src_dict)
        op.set_tag(tag_string)
        self.to_progress_page(op, toplevel_layout, 'Backup')

    def to_restore_page(self, previous_layout=None, title='Restore'):
        """
        The Restore Page.
        A list of detected backup devices on the left. And a list of
        detected versions on the selected devices on the right.
        :rtype previous_layout QLayout: Toplevel layout from previous page.
                                Need to be removed.
        :rtype title str: Page title
        """
        self.__remove_widgets(previous_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet(styles)

        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()

        # Header Widget for title
        image = QWidget(self)
        image.setAutoFillBackground(True)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_style = styles + 'QWidget {background-color:' + theme_color + ';}'
        image.setStyleSheet(image_style)
        # Lists all available devices
        device_list_widget = QListWidget(self)
        device_list_widget.setSelectionMode(QListWidget.SingleSelection)
        device_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        device_list_widget.setStyleSheet(styles)
        self.set_device_list(device_list_widget, RestoreOperation.RestoreOperation())
        # select the first item as initiate the page
        if len(self.devices_list) > 0:
            device_list_widget.setItemSelected(device_list_widget.item(0), True)
        device_list_widget.currentRowChanged.connect(self.__changed_device_selection)
        # Help message
        help_message = QLabel(RESTORE_MESSAGE, self)
        help_message.setWordWrap(True)
        help_message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        help_message.setStyleSheet(styles)
        # Lists all backup versions of the selected device
        self.version_list_widget = QListWidget(self)
        self.version_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.version_list_widget.setSizePolicy(QSizePolicy.Expanding,
                                               QSizePolicy.Expanding)
        self.version_list_widget.setStyleSheet(styles)
        self.set_version_list(self.version_list_widget)

        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        v1.addWidget(buttons)
        h2.addLayout(v3, 2)
        h2.addStretch(1)
        h2.addWidget(self.version_list_widget, 3)
        v3.addWidget(device_list_widget, 3)
        v3.addWidget(help_message, 1)

        buttons.accepted.connect(lambda: self.__accepted_restore(
            device_list_widget, self.version_list_widget, v1))
        buttons.rejected.connect(lambda: self.to_selection_page(v1))

    def __changed_device_selection(self, current_row):
        device = self.devices_list[current_row]
        self.versions_list = Operation.Operation.versions_from_device(device)
        self.set_version_list(self.version_list_widget)

    def set_version_list(self, list_widget):
        """
        Clear the list_widget, fill it with versions of the selected device.
        :param list_widget:
        :return:
        """
        list_widget.clear()         # TODO: I'm sure I did clear the list first, but why didn't work?
        if self.versions_list and len(self.versions_list):
            for item in self.versions_list:
                QListWidgetItem(list_widget).setText(item.tag)

    def __accepted_restore(self, device_list_widget, version_list_widget, toplevel_layout):
        # Auto select device that has backups
        if not device_list_widget.selectedItems():
            """
            for i in range(len(self.devices_list)):
                device = self.devices_list[i]
                versions = Operation.Operation.versions_from_device(device)
                tags = [version.tag for version in versions]
                if len(tags) > 0:
                    device_list_widget.setItemSelected(device_list_widget.item(i), True)
                    self.versions_list = tags
            """
            # Now we won't offer device auto selection, do it yourself.
            message_box = QMessageBox()
            message_box.setText('Please select a device where stored your backups!')
            message_box.exec_()
            return
        # No more Auto select version
        if not version_list_widget.selectedItems():
            # if len(self.versions_list) > 0:
            #     version_list_widget.setItemSelected(version_list_widget.item(0), True)
            message_box = QMessageBox()
            message_box.setText('Please select a version you want to restore to!')
            message_box.exec_()
            return

        i = int()
        # Get selected device
        for i in range(len(self.devices_list)):
            if device_list_widget.isItemSelected(device_list_widget.item(i)):
                break
        selected_device = self.devices_list[i]
        # Get selected version
        for i in range(len(self.versions_list)):
            if version_list_widget.isItemSelected(version_list_widget.item(i)):
                break
        version_of_selected_tag = self.versions_list[i]

        op = RestoreOperation.RestoreOperation()
        op.set_from_device_dict(selected_device)
        op.set_from_version(version_of_selected_tag)
        self.to_progress_page(op, toplevel_layout, 'Restore')  # Here the devil thing begins

    def to_progress_page(self, operation, remove_layout=None, title='Progress'):
        """
        Progress page.
        A progress bar indicates the progress of the restore/backup operation.
        A label shows the estimate remaining time.
        :rtype remove_layout QLayout: Toplevel layout from previous page.
                                    Need to be removed first.
        :rtype title str: page title
        """
        self.__remove_widgets(remove_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.setStyleSheet(styles)
        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()

        # Header Widget for title
        image = QWidget(self)
        image.setAutoFillBackground(True)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_style = styles + 'QWidget {background-color:' + theme_color + ';}'
        image.setStyleSheet(image_style)

        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 0)
        more_style = Template(r'$style QProgressBar::chunk '
                              r'{background-color: $color;}').substitute(
            style=styles, color=theme_color)
        progress_bar.setStyleSheet(more_style)
        progress_bar.setTextVisible(True)
        time_label = QLabel("Time", self)
        time_label.setStyleSheet(styles)
        # file_label = QLabel("File", self)

        v1.addWidget(image, 1)
        v1.addStretch(1)
        v1.addWidget(progress_bar)
        v1.addLayout(h2)
        v1.addStretch(1)
        v1.addWidget(buttons)
        h2.addWidget(time_label)
        h2.addStretch(1)
        # h2.addWidget(file_label)

        buttons.accepted.connect(lambda: self.to_selection_page(v1))
        # Timer(1.0, self.update_progressbar, (progress_bar, operation)).start()
        operation.finish_signal.connect(lambda: self.progress_finish(progress_bar))
        threading.Thread(target=operation.do).start()

    @staticmethod
    def progress_finish(progressbar_widget):
        progressbar_widget.reset()
        progressbar_widget.setRange(0, 100)
        progressbar_widget.setValue(100)

    # def update_progressbar(self, progressbar_widget, operation):
    #     percent = operation.progress_percentage
    #     progressbar_widget.setValue(percent)
    #     if percent < 100:
    #         Timer(1.0, self.update_progressbar, (progressbar_widget, operation)).start()

    def __remove_widgets(self, layout=None):
        """
        Remove sub layouts and sub widgets of the given :param layout.
        Then remove the layout itself.
        :rtype layout QLayout:
        """
        if not layout:
            return
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                sip.delete(child.widget())
            else:
                # remove widgets in the sub layout
                self.__remove_widgets(child.layout())
        # remove the layout itself
        sip.delete(layout)

    def show(self, to_page_fun=None):
        """
        Override show from Class QWidget.
        To specify which page to go to when the window show.
        By default, to_selection_page.
        :type to_page_fun: a callable method of the RollingTimerWindow instance.
        """
        if not to_page_fun:
            to_page_fun = self.to_selection_page
        to_page_fun()
        super(RollingTimerWindow, self).show()

def show_RollingTimer_window(page_arg='selection'):
    app = QApplication(None)
    win = RollingTimerWindow()

    # build the method name from action we received
    method_name = "to_{}_page".format(page_arg)
    import inspect
    method_fun_tuple = filter(lambda name: name[0] == method_name,
                              inspect.getmembers(win, inspect.ismethod))
    # traverse all method to match the one we want
    win.show(method_fun_tuple[0][1])

    sys.exit(app.exec_())


if __name__ == '__main__':
    arg = "selection"
    # parse action argument from command line.
    if len(sys.argv) == 2 and sys.argv[0] != "python":
        # cmd like `RollingTimer backup`
        arg = sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[0] == "python":
        # cmd like `python RollingTimer backup`
        arg = sys.argv[2]
    show_RollingTimer_window(arg)
