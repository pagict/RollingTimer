from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
import sys
import sip
import BackupOperation
import RestoreOperation
import Operation


# noinspection PyUnresolvedReferences
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
        self.versions_list = None
        self.version_list_widget = None
        self.devices_list = None
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
        image = QWidget(self)
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
        self.devices_list = Operation.Operation.devices()
        for item in self.devices_list:
            item_str = 'Name:{} -- Size:{}'.format(item['NAME'], item['SIZE'])
            QListWidgetItem(list_widget).setText(item_str)

    def __accepted_backup(self, device_list_widget, entry, toplevel_layout):
        # If no selection, auto select the first item
        if not device_list_widget.selectedItems():
            device_list_widget.setItemSelected(device_list_widget.item(0), True)

        i = int()
        # Find the selection
        for i in range(len(self.devices_list)):
            if device_list_widget.isItemSelected(device_list_widget.item(i)):
                break
        # get the correlated data and the tag
        selected_device = self.devices_list[i]
        tag_string = entry.text()

        if __debug__:
            print(selected_device)
            print(tag_string)
        src_dict = {'NAME': 'sda1', 'MOUNTPOINT': ''}

        op = BackupOperation.BackupOperation(src_dict, selected_device, tag_string)
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
        device_list_widget = QListWidget(self)
        device_list_widget.setSelectionMode(QListWidget.SingleSelection)
        device_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_device_list(device_list_widget)
        # select the first item as initiate the page
        if len(self.devices_list) > 0:
            device_list_widget.setItemSelected(device_list_widget.item(0), True)
        device_list_widget.currentRowChanged.connect(self.__changed_device_selection)
        # Help message
        help_message = QLabel("help message", self)
        help_message.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Lists all backup versions of the selected device
        self.version_list_widget = QListWidget(self)
        self.version_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.version_list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.set_version_list(self.version_list_widget)

        v1.addWidget(image, 1)
        v1.addLayout(h2, 3)
        v1.addWidget(buttons)
        h2.addLayout(v3, 2)
        h2.addStretch(1)
        h2.addWidget(self.version_list_widget, 3)
        v3.addWidget(device_list_widget, 3)
        v3.addWidget(help_message, 1)

        buttons.accepted.connect(lambda: self.__accepted_restore(device_list_widget, self.version_list_widget, v1))
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
        list_widget.clear()
        if self.versions_list and len(self.versions_list):
            for item in self.versions_list:
                QListWidgetItem(list_widget).setText(item.tag)

    def __accepted_restore(self, device_list_widget, version_list_widget, toplevel_layout):
        # Auto select device that has backups
        if not device_list_widget.selectedItems():
            for i in range(len(self.devices_list)):
                device = self.devices_list[i]
                versions = Operation.Operation.versions_from_device(device)
                tags = [version.tag for version in versions]
                if len(tags) > 0:
                    device_list_widget.setItemSelected(device_list_widget.item(i), True)
                    self.versions_list = tags
        # Auto select version
        if not version_list_widget.selectedItems():
            if len(self.versions_list) > 0:
                version_list_widget.setItemSelected(version_list_widget.item(0), True)
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

        op = RestoreOperation.RestoreOperation(selected_device, version_of_selected_tag)
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