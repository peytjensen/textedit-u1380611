"""
File Tree Module

Implements a VS Code-style file tree sidebar for browsing and opening files.
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QHeaderView,
    QFileDialog, QToolBar, QStyle, QFileSystemModel, QToolButton,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtGui import QAction, QMouseEvent
from PySide6.QtCore import Signal, Qt, QModelIndex, QDir


class SidebarExpandButton(QToolButton):
    """A small button to expand a collapsed sidebar."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("▶")
        self.setToolTip("Show Explorer")
        self.setFixedWidth(16)
        self.setMinimumHeight(60)
        self.setObjectName("sidebarExpandButton")


class CollapsibleSidebar(QWidget):
    """
    A sidebar container that fully collapses, leaving only an expand button.
    
    Signals:
        collapsed_changed: Emitted when collapsed state changes.
    """
    
    collapsed_changed = Signal(bool)
    
    EXPANDED_MIN_WIDTH = 150
    EXPANDED_MAX_WIDTH = 400
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._collapsed = False
        self._content_widget: Optional[QWidget] = None
        self._expanded_width = 200
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        
        self._expand_button = SidebarExpandButton(self)
        self._expand_button.clicked.connect(self._toggle_collapsed)
        self._expand_button.hide()
        self._layout.addWidget(self._expand_button)
        
        self._main_container = QWidget(self)
        main_layout = QVBoxLayout(self._main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self._header = QFrame(self._main_container)
        self._header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(4, 4, 4, 4)
        header_layout.setSpacing(4)
        
        self._title_label = QLabel("Explorer", self._header)
        self._title_label.setObjectName("sidebarTitle")
        header_layout.addWidget(self._title_label, 1)
        
        self._collapse_button = QToolButton(self._header)
        self._collapse_button.setObjectName("collapseButton")
        self._collapse_button.setText("◀")
        self._collapse_button.setToolTip("Hide Explorer")
        self._collapse_button.clicked.connect(self._toggle_collapsed)
        self._collapse_button.setFixedSize(20, 20)
        header_layout.addWidget(self._collapse_button)
        
        main_layout.addWidget(self._header)
        
        self._content_container = QWidget(self._main_container)
        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        main_layout.addWidget(self._content_container, 1)
        
        self._layout.addWidget(self._main_container, 1)
        
        self._update_size_constraints()
    
    def set_content(self, widget: QWidget):
        """Set the content widget for the sidebar."""
        if self._content_widget:
            self._content_layout.removeWidget(self._content_widget)
        
        self._content_widget = widget
        self._content_layout.addWidget(widget)
    
    @property
    def is_collapsed(self) -> bool:
        """Check if the sidebar is collapsed."""
        return self._collapsed
    
    def set_collapsed(self, collapsed: bool):
        """Set the collapsed state."""
        if self._collapsed == collapsed:
            return
        
        if not collapsed:
            self._expanded_width = max(self.width(), self.EXPANDED_MIN_WIDTH)
        
        self._collapsed = collapsed
        self._update_collapsed_state()
        self.collapsed_changed.emit(collapsed)
    
    def toggle_collapsed(self):
        """Toggle the collapsed state."""
        self.set_collapsed(not self._collapsed)
    
    def _toggle_collapsed(self):
        """Internal handler for collapse button."""
        self.toggle_collapsed()
    
    def _update_collapsed_state(self):
        """Update UI based on collapsed state."""
        if self._collapsed:
            self._main_container.hide()
            self._expand_button.show()
        else:
            self._expand_button.hide()
            self._main_container.show()
        
        self._update_size_constraints()
    
    def _update_size_constraints(self):
        """Update size constraints based on collapsed state."""
        if self._collapsed:
            self.setFixedWidth(16)
        else:
            self.setMinimumWidth(self.EXPANDED_MIN_WIDTH)
            self.setMaximumWidth(self.EXPANDED_MAX_WIDTH)
            self.setFixedWidth(self._expanded_width)


class FileTree(QWidget):
    """
    A file tree sidebar for browsing folders and opening files.
    
    Signals:
        file_open_requested: Emitted when a file should be opened (single click or Enter).
        file_open_new_tab_requested: Emitted when a file should be opened in a new tab (middle click).
    """
    
    file_open_requested = Signal(str)  # file path
    file_open_new_tab_requested = Signal(str)  # file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._root_path: Optional[str] = None
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._toolbar = QToolBar(self)
        self._toolbar.setMovable(False)
        self._toolbar.setIconSize(self._toolbar.iconSize() * 0.8)
        
        style = self.style()
        
        self._open_folder_action = QAction("Open Folder", self)
        self._open_folder_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
        self._open_folder_action.setToolTip("Open Folder")
        self._open_folder_action.triggered.connect(self._on_open_folder)
        self._toolbar.addAction(self._open_folder_action)
        
        self._refresh_action = QAction("Refresh", self)
        self._refresh_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self._refresh_action.setToolTip("Refresh")
        self._refresh_action.triggered.connect(self._on_refresh)
        self._toolbar.addAction(self._refresh_action)
        
        self._close_folder_action = QAction("Close Folder", self)
        self._close_folder_action.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        self._close_folder_action.setToolTip("Close Folder")
        self._close_folder_action.triggered.connect(self._on_close_folder)
        self._close_folder_action.setEnabled(False)
        self._toolbar.addAction(self._close_folder_action)
        
        layout.addWidget(self._toolbar)
        
        self._model = QFileSystemModel(self)
        self._model.setRootPath("")
        self._model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)
        
        self._tree_view = FileTreeView(self)
        self._tree_view.setModel(self._model)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setAnimated(True)
        self._tree_view.setIndentation(16)
        self._tree_view.setSortingEnabled(True)
        self._tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
        for i in range(1, self._model.columnCount()):
            self._tree_view.hideColumn(i)
        
        header = self._tree_view.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self._tree_view)
    
    def _connect_signals(self):
        """Connect signals."""
        self._tree_view.doubleClicked.connect(self._on_item_double_clicked)
        self._tree_view.middle_clicked.connect(self._on_item_middle_clicked)
    
    @property
    def root_path(self) -> Optional[str]:
        """Get the currently open folder path."""
        return self._root_path
    
    def open_folder(self, folder_path: str) -> bool:
        """Open a folder in the file tree."""
        path = Path(folder_path)
        if not path.exists() or not path.is_dir():
            return False
        
        self._root_path = str(path.resolve())
        self._model.setRootPath(self._root_path)
        self._tree_view.setRootIndex(self._model.index(self._root_path))
        self._close_folder_action.setEnabled(True)
        return True
    
    def close_folder(self):
        """Close the currently open folder."""
        self._root_path = None
        home_dir = os.path.expanduser("~")
        self._model.setRootPath(home_dir)
        self._tree_view.setRootIndex(self._model.index(home_dir))
        self._close_folder_action.setEnabled(False)
    
    def refresh(self):
        """Refresh the file tree."""
        if self._root_path:
            current_root = self._root_path
            self._model.setRootPath("")
            self._model.setRootPath(current_root)
            self._tree_view.setRootIndex(self._model.index(current_root))
    
    def _on_open_folder(self):
        """Handle open folder action."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Open Folder",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            self.open_folder(folder_path)
    
    def _on_refresh(self):
        """Handle refresh action."""
        self.refresh()
    
    def _on_close_folder(self):
        """Handle close folder action."""
        self.close_folder()
    
    def _on_item_double_clicked(self, index: QModelIndex):
        """Handle double-click on an item."""
        if not index.isValid():
            return
        
        file_path = self._model.filePath(index)
        if self._model.isDir(index):
            return
        
        self.file_open_requested.emit(file_path)
    
    def _on_item_middle_clicked(self, index: QModelIndex):
        """Handle middle-click on an item."""
        if not index.isValid():
            return
        
        file_path = self._model.filePath(index)
        if self._model.isDir(index):
            return
        
        self.file_open_new_tab_requested.emit(file_path)


class FileTreeView(QTreeView):
    """
    Custom QTreeView that emits a signal on middle mouse button click.
    """
    
    middle_clicked = Signal(QModelIndex)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.MiddleButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                self.middle_clicked.emit(index)
                event.accept()
                return
        
        super().mousePressEvent(event)
