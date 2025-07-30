from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QCompleter
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, Signal

class SearchableComboBox(QComboBox):
    selectionChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        # Filter model for matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # Completer that uses filter model
        self.completer = QCompleter(self.pFilterModel, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # Connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)
        self.activated.connect(self.emit_selection_changed)

        # Increase font size
        font = self.font()
        font.setPointSize(11)
        self.setFont(font)
        self.lineEdit().setFont(font)
        self.view().setFont(font)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            # Emit selectionChanged with the selected text
            self.selectionChanged.emit(self.itemText(index))

    def emit_selection_changed(self, index):
        # Emit the selected text when an item is activated
        self.selectionChanged.emit(self.itemText(index))

    def setModel(self, model):
        super().setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super().setModelColumn(column)

    def set_enabled(self, enabled=True):
        self.setEnabled(enabled)
        self.lineEdit().setEnabled(enabled)

    @property
    def options(self):
        return [self.itemText(i) for i in range(self.count())]

    def set_options(self, options):
        self.clear()
        self.addItems(options)

    def text(self):
        return self.currentText()

    def setText(self, value):
        idx = self.findText(value)
        if idx >= 0:
            self.setCurrentIndex(idx)
        else:
            self.setEditText(value)

class SearchableDropdown(QWidget):
    def __init__(self, parent, label_text, options, var=None, width=350, font=("Segoe UI", 11),
                 bg="#1e1e1e", fg="#ffffff", **kwargs):
        super().__init__(parent)
        self.var = var
        self.bg = bg
        self.fg = fg

        self.setStyleSheet(f"background-color: {bg}; color: {fg};")
        self.setMinimumWidth(width)
        self.setMaximumWidth(width)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(8)

        label = QLabel(label_text)
        label.setStyleSheet(f"color: {fg}; font-family: {font[0]}; font-size: {font[1]}pt;")
        label.setFixedWidth(90)
        row_layout.addWidget(label)

        self.combo = SearchableComboBox(self)
        self.combo.set_options(options)
        self.combo.setFixedWidth(width - 100)
        row_layout.addWidget(self.combo)

        main_layout.addLayout(row_layout)

        # Bind to var if provided
        if self.var:
            self.combo.selectionChanged.connect(self.var.set)
        self.combo.selectionChanged.connect(self.on_selection_changed)

    def set_enabled(self, enabled=True):
        self.combo.set_enabled(enabled)

    @property
    def line_edit(self):
        return self.combo.lineEdit()

    @property
    def options(self):
        return self.combo.options

    def on_selection_changed(self, value):
        if self.var:
            self.var.set(value)