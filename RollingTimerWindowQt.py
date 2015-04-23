
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
import sys, sip
import utils
import BackupOperation, RestoreOperation
from multiprocessing import Pool


class RollingTimerWindow(QDialog):
    """
    A Dialog used to simulate Assistant Window.
    When go to another page, the invoker page should pass its toplevel layout
    to the destination page, which is responsible to remove all sub widgets
    and sub layouts of that toplevel layout first.
    """

    def __init__(self):
        super(RollingTimerWindow, self).__init__()
        self.versions = None
        self.showFullScreen()
        self.to_selection_page()

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
        image = QWidget(parent=self)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image.setAutoFillBackground(True)
        p = image.palette()
        p.setColor(image.backgroundRole(), QtGui.QColor('#fff0d0'))
        image.setPalette(p)
        # Restore Button
        to_restore = QPushButton(QtCore.QString("Restore"), self)
        to_restore.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Backup Button
        to_backup = QPushButton(QtCore.QString("Backup"), self)
        to_backup.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        h2.addWidget(to_restore, stretch=1)
        h2.addWidget(to_backup, stretch=1)

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
        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()

        # Header Widget
        image = QWidget(self)
        image.setAutoFillBackground(True)
        p = image.palette()
        p.setColor(image.backgroundRole(), QColor('#fff0d0'))
        image.setPalette(p)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        v1.addWidget(buttons)

        # List of all available backup devices
        device_list = QListWidget(self)
        device_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        device_list.setSelectionMode(QListWidget.SingleSelection)
        self.set_device_list(device_list)
        h2.addWidget(device_list)
        h2.addLayout(v3)

        # Entry for tagging this backup version
        entry = QLineEdit(self)
        # Help message
        message = QLabel("Message", self)
        v3.addWidget(entry)
        v3.addWidget(message)

        buttons.rejected.connect(lambda: self.to_selection_page(v1))
        buttons.accepted.connect(lambda: self.__accepted_backup(device_list, entry, v1))

    def set_device_list(self, list_widget):
        self.devices = utils.available_devices()
        self.devices = [{'NAME': '/root/tst_cpio', 'SIZE': '8G'},
                        {'NAME':'/root/hello', 'SIZE': '7G'}]  #TODO: delete after test
        for item in self.devices:
            item_str = 'Name:{} -- Size:{}'.format(item['NAME'], item['SIZE'])
            QListWidgetItem(parent=list_widget).setText(item_str)

    def __accepted_backup(self, device_list, entry, toplevel_layout):
        if not device_list.selectedItems():
            device_list.setItemSelected(device_list.item(0), True)
        for i in range(len(self.devices)):
            if device_list.isItemSelected(device_list.item(i)):
                break
        selected_device = self.devices[i]
        tag_string = entry.text()
        print(selected_device)
        print(tag_string)
        op = BackupOperation.BackupOperation('~/rpmbuild', '~/tst_cpio', tag_string)
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

        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()
        v3 = QVBoxLayout()

        # Header Widget for title
        image = QWidget(self)
        image.setAutoFillBackground(True)
        p = image.palette()
        p.setColor(image.backgroundRole(), QColor('#fff0d0'))
        image.setPalette(p)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Lists all available devices
        device_list = QListWidget(self)
        device_list.setSelectionMode(QListWidget.SingleSelection)
        device_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_device_list(device_list)
        if len(self.devices) > 0:
            device_list.setItemSelected(device_list.item(0), True)

        device_list.currentRowChanged.connect(self.__changed_device_selection)
        # Help message
        help_message = QLabel("help message", self)
        help_message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Lists all backup versions of the selected device
        self.version_list = QListWidget(self)
        self.version_list.setSelectionMode(QListWidget.SingleSelection)
        self.version_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_version_list(self.version_list)

        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        v1.addWidget(buttons)
        h2.addLayout(v3, 2)
        h2.addStretch(1)
        h2.addWidget(self.version_list, 3)
        v3.addWidget(device_list, 3)
        v3.addWidget(help_message, 1)

        buttons.accepted.connect(lambda: self.__accepted_restore(device_list, self.version_list, v1))
        buttons.rejected.connect(lambda: self.to_selection_page(v1))

    def __changed_device_selection(self, current_row):
        device = self.devices[current_row]
        self.versions = RestoreOperation.RestoreOperation.all_tags(device['NAME'])
        self.set_version_list(self.version_list)

    def set_version_list(self, list_widget):
        list_widget.clear()
        if self.versions and len(self.versions):
            for item in self.versions:
                QListWidgetItem(list_widget).setText(item)

    def __accepted_restore(self, device_list, version_list, toplevel_layout):
        # Auto select device that has backups
        if not device_list.selectedItems():
            for i in range(len(self.devices)):
                device = self.devices[i]
                versions = RestoreOperation.RestoreOperation.all_tags(device['NAME'])
                if len(versions) > 0:
                    device_list.setItemSelected(device_list.item(i), True)
                    self.versions = versions
        # Auto select version
        if not version_list.selectedItems():
            if len(self.versions) > 0:
                version_list.setItemSelected(version_list.item(0), True)

        for i in range(len(self.devices)):
            if device_list.isItemSelected(device_list.item(i)):
                break
        selected_device = self.devices[i]
        for i in range(len(self.versions)):
            if version_list.isItemSelected(version_list.item(i)):
                break
        selected_tag = self.versions[i]

        op = RestoreOperation.RestoreOperation(selected_device['NAME'], selected_tag)
        self.to_progress_page(op, toplevel_layout, 'Restore')



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
        v1 = QVBoxLayout(self)
        h2 = QHBoxLayout()

        # Header Widget for title
        image = QWidget(self)
        image.setAutoFillBackground(True)
        p = image.palette()
        p.setColor(image.backgroundRole(), QColor('#fff0d0'))
        image.setPalette(p)
        image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        progress_bar = QProgressBar(self)
        time_label = QLabel("Time", self)
        file_label = QLabel("File", self)

        v1.addWidget(image, 1)
        v1.addStretch(1)
        v1.addWidget(progress_bar)
        v1.addLayout(h2)
        v1.addStretch(1)
        v1.addWidget(buttons)
        h2.addWidget(time_label)
        h2.addStretch(1)
        #h2.addWidget(file_label)

        buttons.accepted.connect(lambda: self.to_selection_page(v1)) #TODO: Only for debug
        operation.do()

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
                child.widget().deleteLater()
            else:
                # remove widgets in the sub layout
                self.__remove_widgets(child.layout())
        # remove the layout itself
        sip.delete(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = RollingTimerWindow()
    win.show()
    sys.exit(app.exec_())