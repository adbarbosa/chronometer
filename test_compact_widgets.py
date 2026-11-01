"""Verifica que a abreviação visual preserva os valores completos dos controlos."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QProxyStyle, QStyle

from chronometer.compact_widgets import ElidingComboBox, ElidingLabel


class RecordingStyle(QProxyStyle):
    """Regista os textos que chegam ao estilo real durante a pintura dos controlos."""

    def __init__(self):
        """Usa um estilo disponível em Linux e Windows e prepara os registos."""
        super().__init__("Fusion")
        self.item_texts = []
        self.combo_texts = []

    def drawItemText(self, painter, rect, flags, palette, enabled, text, text_role):
        """Regista o texto desenhado sem substituir a implementação do estilo."""
        self.item_texts.append(text)
        super().drawItemText(painter, rect, flags, palette, enabled, text, text_role)

    def drawControl(self, element, option, painter, widget=None):
        """Regista a seleção apresentada e mantém a pintura normal da caixa."""
        if element == QStyle.ControlElement.CE_ComboBoxLabel:
            self.combo_texts.append(option.currentText)
        super().drawControl(element, option, painter, widget)


def test_label_shrinks_visually_without_losing_text(qt_app):
    """Uma etiqueta estreita mostra reticências, mas conserva o texto e a ajuda."""
    full_text = "Saída de apresentação num monitor com um nome muito comprido"
    label = ElidingLabel(full_text)
    style = RecordingStyle()
    label.setStyle(style)
    label.resize(100, label.sizeHint().height())
    label.show()
    qt_app.processEvents()

    assert label.width() < label.fontMetrics().horizontalAdvance(full_text)
    assert label.minimumSizeHint().width() < label.width()
    assert style.item_texts[-1].endswith("…")
    assert style.item_texts[-1] != full_text
    assert label.text() == full_text
    assert label.toolTip() == full_text

    label.resize(label.sizeHint())
    label.grab()
    assert style.item_texts[-1] == full_text
    label.setText("Saída oculta")
    assert label.text() == label.toolTip() == "Saída oculta"
    label.clear()
    assert label.text() == label.toolTip() == ""
    label.close()


def test_combo_preserves_monitor_identity_and_updates_tooltip(qt_app):
    """A caixa compacta mantém os itens originais ao pintar ou mudar a seleção."""
    full_text = "Monitor de apresentação com um nome demasiado comprido para o painel"
    combo = ElidingComboBox()
    style = RecordingStyle()
    combo.setStyle(style)
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(2)
    combo.addItem(full_text, "monitor-primary")
    combo.addItem("Segundo monitor", "monitor-secondary")
    combo.setItemData(0, full_text, Qt.ItemDataRole.ToolTipRole)
    combo.resize(100, combo.sizeHint().height())
    combo.show()
    qt_app.processEvents()

    assert combo.minimumSizeHint().width() < combo.fontMetrics().horizontalAdvance(full_text)
    assert style.combo_texts[-1].endswith("…")
    assert style.combo_texts[-1] != full_text
    assert combo.currentText() == combo.itemText(0) == combo.toolTip() == full_text
    assert combo.currentData() == "monitor-primary"
    assert combo.itemData(0, Qt.ItemDataRole.ToolTipRole) == full_text

    combo.setCurrentIndex(1)
    assert combo.currentText() == combo.toolTip() == "Segundo monitor"
    assert combo.currentData() == "monitor-secondary"
    combo.setItemText(1, "Monitor com nome atualizado")
    assert combo.currentText() == combo.toolTip() == "Monitor com nome atualizado"
    combo.clear()
    assert combo.currentText() == combo.toolTip() == ""
    combo.close()
