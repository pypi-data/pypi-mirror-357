from PyQt5.QtWidgets import QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QMessageBox, QSpinBox

def make_button(text, style, slot=None):
    btn = QPushButton(text)
    btn.setStyleSheet(style)
    if slot:
        btn.clicked.connect(slot)
    return btn

def CardWidget(left_widgets, right_widgets=None, style=None):
    card = QFrame()
    card.setFrameShape(QFrame.StyledPanel)
    if style:
        card.setStyleSheet(style)
    card_layout = QHBoxLayout()
    left = QVBoxLayout()
    for w in left_widgets:
        left.addWidget(w)
    card_layout.addLayout(left)
    if right_widgets:
        right = QVBoxLayout()
        for w in right_widgets:
            right.addWidget(w)
        card_layout.addLayout(right)
    card.setLayout(card_layout)
    return card

def generic_form_dialog(parent, title, fields):
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    form = QFormLayout(dlg)
    widgets = {}
    for field in fields:
        label, wtype, opts = field
        if wtype == 'line':
            w = QLineEdit(opts.get('default', ''))
        elif wtype == 'combo':
            w = QComboBox()
            w.addItems(opts['items'])
            if 'default' in opts:
                idx = w.findText(opts['default'])
                if idx >= 0: w.setCurrentIndex(idx)
        elif wtype == 'spin':
            w = QSpinBox()
            w.setMinimum(opts.get('min', 0))
            w.setMaximum(opts.get('max', 1000))
            w.setValue(opts.get('default', 0))
        elif wtype == 'doublespin':
            w = QDoubleSpinBox()
            w.setMinimum(opts.get('min', 0))
            w.setMaximum(opts.get('max', 9999999))
            w.setDecimals(opts.get('decimals', 2))
            w.setValue(opts.get('default', 0))
        else:
            continue
        widgets[label] = w
        form.addRow(label, w)
    result = {}
    def save():
        for label, w in widgets.items():
            if isinstance(w, QLineEdit):
                result[label] = w.text()
            elif isinstance(w, QComboBox):
                result[label] = w.currentText()
            elif isinstance(w, (QSpinBox, QDoubleSpinBox)):
                result[label] = w.value()
        dlg.accept()
    save_btn = QPushButton('Сохранить')
    save_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
    save_btn.clicked.connect(save)
    form.addRow(save_btn)
    if dlg.exec_() == QDialog.Accepted:
        return result
    return None
