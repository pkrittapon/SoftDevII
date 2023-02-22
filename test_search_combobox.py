from PyQt5 import QtWidgets, QtCore
from data.function import Categories

app = QtWidgets.QApplication([])

Set = Categories('SET')
Nasdaq = Categories('NASDAQ')
Crypto = Categories('CRYPTO')
all_symbol = []
for symbol in Set.get_all_stock():
    all_symbol.append(symbol+'\t\t- SET')
for symbol in Nasdaq.get_all_stock():
    all_symbol.append(symbol+'\t\t- NASDAQ')
for symbol in Crypto.get_all_stock():
    all_symbol.append(symbol+'\t\t- CRYPTO')

combo = QtWidgets.QComboBox()
combo.addItems(all_symbol)

# completers only work for editable combo boxes. QComboBox.NoInsert prevents insertion of the search text
combo.setEditable(True)
combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)

# change completion mode of the default completer from InlineCompletion to PopupCompletion
combo.completer().setCompletionMode(QtWidgets.QCompleter.PopupCompletion)

# enable partial consecutive search
combo.completer().setFilterMode(QtCore.Qt.MatchContains)
combo.completer().setCaseSensitivity(QtCore.Qt.CaseInsensitive)

combo.setCurrentIndex(-1)

# connect the slot to the currentIndexChanged signal


# define a slot to handle current index changes
def handle_current_index_changed(index):
        print("Selected item:", combo.currentText())
        combo.setCurrentIndex(-1)
        combo.clearEditText()
        
combo.activated.connect(handle_current_index_changed)

combo.show()
app.exec()
