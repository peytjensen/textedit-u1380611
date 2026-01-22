"""
Tests for the file tree module.
"""

import os
import tempfile
from pathlib import Path

import pytest
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import QApplication

from editor.file_tree import FileTree, FileTreeView, CollapsibleSidebar


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for the test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestFileTreeCreation:
    """Tests for FileTree widget creation."""
    
    def test_file_tree_creation(self, qapp):
        """FileTree can be created."""
        tree = FileTree()
        assert tree is not None
        tree.deleteLater()
    
    def test_file_tree_has_toolbar(self, qapp):
        """FileTree has a toolbar with actions."""
        tree = FileTree()
        assert tree._toolbar is not None
        assert tree._open_folder_action is not None
        assert tree._refresh_action is not None
        assert tree._close_folder_action is not None
        tree.deleteLater()
    
    def test_file_tree_has_tree_view(self, qapp):
        """FileTree has a tree view."""
        tree = FileTree()
        assert tree._tree_view is not None
        assert isinstance(tree._tree_view, FileTreeView)
        tree.deleteLater()
    
    def test_initial_root_path_is_none(self, qapp):
        """Initially no folder is open."""
        tree = FileTree()
        assert tree.root_path is None
        tree.deleteLater()
    
    def test_close_folder_initially_disabled(self, qapp):
        """Close folder action is disabled when no folder is open."""
        tree = FileTree()
        assert not tree._close_folder_action.isEnabled()
        tree.deleteLater()


class TestFileTreeOpenFolder:
    """Tests for opening folders in the file tree."""
    
    def test_open_valid_folder(self, qapp):
        """Can open a valid folder."""
        tree = FileTree()
        with tempfile.TemporaryDirectory() as tmpdir:
            result = tree.open_folder(tmpdir)
            assert result is True
            assert tree.root_path == str(Path(tmpdir).resolve())
            assert tree._close_folder_action.isEnabled()
        tree.deleteLater()
    
    def test_open_invalid_folder(self, qapp):
        """Opening non-existent folder returns False."""
        tree = FileTree()
        result = tree.open_folder("/nonexistent/path/that/does/not/exist")
        assert result is False
        assert tree.root_path is None
        tree.deleteLater()
    
    def test_open_file_instead_of_folder(self, qapp):
        """Opening a file instead of folder returns False."""
        tree = FileTree()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test")
            filepath = f.name
        
        try:
            result = tree.open_folder(filepath)
            assert result is False
        finally:
            os.unlink(filepath)
        tree.deleteLater()
    
    def test_close_folder(self, qapp):
        """Can close an open folder."""
        tree = FileTree()
        with tempfile.TemporaryDirectory() as tmpdir:
            tree.open_folder(tmpdir)
            tree.close_folder()
            assert tree.root_path is None
            assert not tree._close_folder_action.isEnabled()
        tree.deleteLater()
    
    def test_close_folder_defaults_to_home_directory(self, qapp):
        """When a folder is closed, it defaults to the user's home directory."""
        tree = FileTree()
        with tempfile.TemporaryDirectory() as tmpdir:
            tree.open_folder(tmpdir)
            tree.close_folder()
            # After closing, the tree should display the home directory
            home_dir = os.path.expanduser("~")
            assert tree._model.rootPath() == home_dir
        tree.deleteLater()


class TestFileTreeRefresh:
    """Tests for refreshing the file tree."""
    
    def test_refresh_with_folder(self, qapp):
        """Refresh works when a folder is open."""
        tree = FileTree()
        with tempfile.TemporaryDirectory() as tmpdir:
            tree.open_folder(tmpdir)
            tree.refresh()
            assert tree.root_path == str(Path(tmpdir).resolve())
        tree.deleteLater()
    
    def test_refresh_without_folder(self, qapp):
        """Refresh is safe when no folder is open."""
        tree = FileTree()
        tree.refresh()
        assert tree.root_path is None
        tree.deleteLater()


class TestFileTreeView:
    """Tests for the custom FileTreeView."""
    
    def test_file_tree_view_creation(self, qapp):
        """FileTreeView can be created."""
        view = FileTreeView()
        assert view is not None
        view.deleteLater()
    
    def test_middle_click_signal_exists(self, qapp):
        """FileTreeView has middle_clicked signal."""
        view = FileTreeView()
        assert hasattr(view, 'middle_clicked')
        view.deleteLater()


class TestFileTreeSignals:
    """Tests for file tree signals."""
    
    def test_file_open_requested_signal(self, qapp):
        """file_open_requested signal exists."""
        tree = FileTree()
        assert hasattr(tree, 'file_open_requested')
        tree.deleteLater()
    
    def test_file_open_new_tab_requested_signal(self, qapp):
        """file_open_new_tab_requested signal exists."""
        tree = FileTree()
        assert hasattr(tree, 'file_open_new_tab_requested')
        tree.deleteLater()


class TestCollapsibleSidebar:
    """Tests for the CollapsibleSidebar widget."""
    
    def test_sidebar_creation(self, qapp):
        """CollapsibleSidebar can be created."""
        sidebar = CollapsibleSidebar()
        assert sidebar is not None
        sidebar.deleteLater()
    
    def test_sidebar_initially_not_collapsed(self, qapp):
        """Sidebar is not collapsed by default."""
        sidebar = CollapsibleSidebar()
        assert sidebar.is_collapsed is False
        sidebar.deleteLater()
    
    def test_set_collapsed(self, qapp):
        """Can set collapsed state."""
        sidebar = CollapsibleSidebar()
        sidebar.set_collapsed(True)
        assert sidebar.is_collapsed is True
        sidebar.deleteLater()
    
    def test_toggle_collapsed(self, qapp):
        """Can toggle collapsed state."""
        sidebar = CollapsibleSidebar()
        assert sidebar.is_collapsed is False
        sidebar.toggle_collapsed()
        assert sidebar.is_collapsed is True
        sidebar.toggle_collapsed()
        assert sidebar.is_collapsed is False
        sidebar.deleteLater()
    
    def test_set_content(self, qapp):
        """Can set content widget."""
        sidebar = CollapsibleSidebar()
        tree = FileTree()
        sidebar.set_content(tree)
        assert sidebar._content_widget is tree
        sidebar.deleteLater()
    
    def test_collapsed_changed_signal(self, qapp):
        """collapsed_changed signal is emitted."""
        sidebar = CollapsibleSidebar()
        signal_received = []
        sidebar.collapsed_changed.connect(lambda v: signal_received.append(v))
        sidebar.set_collapsed(True)
        assert signal_received == [True]
        sidebar.deleteLater()
    
    def test_collapsed_width(self, qapp):
        """Collapsed sidebar has narrow width."""
        sidebar = CollapsibleSidebar()
        sidebar.set_collapsed(True)
        assert sidebar.width() <= 20
        sidebar.deleteLater()
