"""Controlos que abreviam apenas a apresentação de textos compridos."""

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QComboBox, QFrame, QLabel, QStyle, QStyleOptionComboBox, QStylePainter, QWidget


class ElidingLabel(QLabel):
    """Mostra texto simples numa linha, mantendo o valor completo na ajuda."""

    def __init__(self, text: str = "", parent: QWidget | None = None):
        """Inicializa o texto e a ajuda sem impor a largura da frase completa."""
        super().__init__(text, parent)
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setToolTip(text)

    def setText(self, text: str):
        """Atualiza o valor original e a ajuda, sem guardar uma versão abreviada."""
        super().setText(text)
        self.setToolTip(text)

    def clear(self):
        """Limpa o texto apresentado e a respetiva ajuda."""
        self.setText("")

    def minimumSizeHint(self) -> QSize:
        """Permite reduzir a largura sem perder a altura necessária ao texto."""
        size = super().minimumSizeHint()
        size.setWidth(0)
        return size

    def paintEvent(self, event):
        """Desenha a moldura e o texto abreviado com a paleta e alinhamento atuais."""
        QFrame.paintEvent(self, event)
        painter = QStylePainter(self)
        margin = self.margin()
        rect = self.contentsRect().adjusted(margin, margin, -margin, -margin)
        alignment = QStyle.visualAlignment(self.layoutDirection(), self.alignment())
        text = self.fontMetrics().elidedText(self.text(), Qt.TextElideMode.ElideRight, max(0, rect.width()))
        painter.drawItemText(
            rect, int(alignment), self.palette(), self.isEnabled(), text, QPalette.ColorRole.WindowText,
        )


class ElidingComboBox(QComboBox):
    """Abrevia o texto selecionado sem alterar os itens ou os seus identificadores."""

    def __init__(self, parent: QWidget | None = None):
        """Mantém a ajuda sincronizada com o texto completo da seleção."""
        super().__init__(parent)
        self.currentTextChanged.connect(self.setToolTip)

    def paintEvent(self, event):
        """Usa o estilo Qt para desenhar a caixa, a seta e a seleção abreviada."""
        if self.isEditable():
            super().paintEvent(event)
            return
        painter = QStylePainter(self)
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        text_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox, option, QStyle.SubControl.SC_ComboBoxEditField, self,
        )
        width = text_rect.width()
        if not option.currentIcon.isNull():
            spacing = self.style().pixelMetric(QStyle.PixelMetric.PM_FocusFrameHMargin, option, self)
            width -= option.iconSize.width() + 2 * spacing
        option.currentText = option.fontMetrics.elidedText(
            option.currentText, Qt.TextElideMode.ElideRight, max(0, width),
        )
        painter.drawControl(QStyle.ControlElement.CE_ComboBoxLabel, option)
