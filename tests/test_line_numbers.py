"""
Tests for the LineNumberedEditor module.
"""

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor

from editor.line_number_editor import LineNumberedEditor, LineNumberArea


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def editor(qapp):
    """Create a fresh LineNumberedEditor for each test."""
    widget = LineNumberedEditor()
    yield widget
    widget.deleteLater()


class TestLineNumberedEditorInit:
    """Tests for LineNumberedEditor initialization."""
    
    def test_has_line_number_area(self, editor):
        """Editor has a line number area widget."""
        assert editor._line_number_area is not None
        assert isinstance(editor._line_number_area, LineNumberArea)
    
    def test_initial_colors_set(self, editor):
        """Editor has initial colors set."""
        assert editor._bg_color is not None
        assert editor._text_color is not None
        assert editor._current_line_color is not None
        assert editor._current_line_bg is not None
    
    def test_viewport_has_left_margin(self, editor):
        """Viewport has left margin for line numbers."""
        margins = editor.viewportMargins()
        assert margins.left() > 0


class TestLineNumberAreaWidth:
    """Tests for line number area width calculation."""
    
    def test_width_for_single_digit(self, editor):
        """Width accommodates single digit line numbers."""
        editor.setPlainText("Line 1")
        width = editor.line_number_area_width()
        assert width > 0
    
    def test_width_increases_for_more_lines(self, editor):
        """Width increases when more digits needed."""
        editor.setPlainText("Line 1")
        width_1 = editor.line_number_area_width()
        
        editor.setPlainText("\n".join([f"Line {i}" for i in range(1, 1001)]))
        width_1000 = editor.line_number_area_width()
        
        assert width_1000 > width_1


class TestLineNumberColors:
    """Tests for line number color configuration."""
    
    def test_set_line_number_colors(self, editor):
        """Can set line number colors."""
        editor.set_line_number_colors("#111111", "#222222", "#333333", "#444444")
        assert editor._bg_color == QColor("#111111")
        assert editor._text_color == QColor("#222222")
        assert editor._current_line_color == QColor("#333333")
        assert editor._current_line_bg == QColor("#444444")
    
    def test_colors_accept_hex_strings(self, editor):
        """Colors accept hex color strings."""
        editor.set_line_number_colors("#ff0000", "#00ff00", "#0000ff", "#ffffff")
        assert editor._bg_color.red() == 255
        assert editor._text_color.green() == 255
        assert editor._current_line_color.blue() == 255


class TestLineNumberArea:
    """Tests for LineNumberArea widget."""
    
    def test_size_hint_uses_editor_width(self, editor):
        """Size hint uses editor's calculated width."""
        area = editor._line_number_area
        hint = area.sizeHint()
        assert hint.width() == editor.line_number_area_width()
        assert hint.height() == 0


class TestCurrentLineHighlight:
    """Tests for current line highlighting."""
    
    def test_extra_selections_set(self, editor):
        """Editor has extra selections for current line."""
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        selections = editor.extraSelections()
        assert len(selections) >= 1
    
    def test_highlight_updates_on_cursor_move(self, editor):
        """Highlight updates when cursor moves."""
        editor.setPlainText("Line 1\nLine 2\nLine 3")
        cursor = editor.textCursor()
        cursor.movePosition(cursor.MoveOperation.Down)
        editor.setTextCursor(cursor)
        selections = editor.extraSelections()
        assert len(selections) >= 1
