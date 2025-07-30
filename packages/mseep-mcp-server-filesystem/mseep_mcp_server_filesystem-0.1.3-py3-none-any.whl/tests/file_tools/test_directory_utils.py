"""Tests for directory_utils functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Import functions directly from the module
from src.file_tools.directory_utils import (
    _discover_files,
    apply_gitignore_filter,
    filter_with_gitignore,
    list_files,
    read_gitignore_rules,
)
from tests.conftest import TEST_DIR


def test_discover_files(project_dir):
    """Test discovering files in a directory recursively."""
    # Create test directory structure
    test_dir = project_dir / TEST_DIR

    # Create a subdirectory for testing recursion
    subdir = test_dir / "subdir"
    subdir.mkdir(exist_ok=True)

    # Create test files
    test_files = [test_dir / "test1.txt", test_dir / "test2.txt", subdir / "test3.txt"]

    for file_path in test_files:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Content for {file_path.name}")

    # Test file discovery
    discovered_files = _discover_files(test_dir, project_dir)

    # Convert to a set for easy comparison
    rel_paths = set(str(Path(f)) for f in discovered_files)
    expected_paths = {
        str(Path("testdata/test_file_tools/test1.txt")),
        str(Path("testdata/test_file_tools/test2.txt")),
        str(Path("testdata/test_file_tools/subdir/test3.txt")),
    }

    # Check if all expected files were discovered
    assert rel_paths.issuperset(expected_paths)


def test_git_directory_exclusion(project_dir):
    """Test that .git directory is excluded from file discovery."""
    # Create test directory structure
    test_dir = project_dir / TEST_DIR

    # Create a .git directory with some files in it
    git_dir = test_dir / ".git"
    git_dir.mkdir(exist_ok=True)

    # Create some files in the test directory and in the .git directory
    regular_file = test_dir / "regular.txt"
    git_file = git_dir / "git_config.txt"

    regular_file.write_text("Regular file content")
    git_file.write_text("Git file content")

    # Discover files
    discovered_files = _discover_files(test_dir, project_dir)

    # Convert to a set of paths for easier assertion
    discovered_paths = set(discovered_files)

    # Convert paths to a format that's consistent across platforms
    regular_path = str(Path("testdata/test_file_tools/regular.txt"))
    git_path = str(Path("testdata/test_file_tools/.git/git_config.txt"))

    # Assert that the regular file is included
    assert regular_path in discovered_paths

    # Assert that the git file is excluded
    assert git_path not in discovered_paths


def test_read_gitignore_rules_no_file():
    """Test reading gitignore rules when no file exists."""
    # Use a temporary directory to ensure no .gitignore exists
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / ".gitignore"

        # Test with non-existent file
        matcher, content = read_gitignore_rules(temp_path)

        # Both should be None when file doesn't exist
        assert matcher is None
        assert content is None


def test_read_gitignore_rules_with_file():
    """Test reading gitignore rules from an existing file."""
    # Create a temporary .gitignore file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / ".gitignore"

        # Create sample gitignore content
        gitignore_content = "*.log\n/node_modules/\n"
        temp_path.write_text(gitignore_content)

        # Test reading the rules
        matcher, content = read_gitignore_rules(temp_path)

        # Content should match what we wrote
        assert content == gitignore_content

        # Matcher should be a callable function
        assert callable(matcher)

        # Check if it correctly identifies ignored files
        ignored_file = os.path.join(temp_dir, "test.log")
        not_ignored_file = os.path.join(temp_dir, "test.txt")

        # True means the file should be ignored
        assert matcher(ignored_file) is True
        assert matcher(not_ignored_file) is False


def test_apply_gitignore_filter(project_dir):
    """Test applying gitignore filter with a predefined matcher."""

    # Create a simple matcher function that ignores files with .log extension
    def mock_matcher(path):
        return path.endswith(".log")

    # Create list of test file paths
    file_paths = [
        "folder/file.txt",
        "folder/data.log",
        "another/document.md",
        "logs/error.log",
    ]

    # Apply the filter
    filtered = apply_gitignore_filter(file_paths, mock_matcher, project_dir)

    # Check that only non-.log files remain
    assert filtered == ["folder/file.txt", "another/document.md"]

    # Test with None matcher
    assert apply_gitignore_filter(file_paths, None, project_dir) == file_paths


def test_filter_with_gitignore_no_gitignore(project_dir):
    """Test filtering files when no .gitignore file exists."""
    # Create a list of file paths
    file_paths = [
        "testdata/test_file_tools/file1.txt",
        "testdata/test_file_tools/file2.txt",
    ]

    # Test with a directory that doesn't have a .gitignore file
    test_dir = project_dir / TEST_DIR

    # Ensure no .gitignore file exists
    gitignore_path = test_dir / ".gitignore"
    if gitignore_path.exists():
        gitignore_path.unlink()

    # Test the filter with no .gitignore
    filtered_files = filter_with_gitignore(file_paths, test_dir, project_dir)

    # Without a .gitignore file, all files should be returned
    assert set(filtered_files) == set(file_paths)


def test_list_files_basic(project_dir):
    """Test listing files in a directory."""
    # Create test directory structure
    test_dir = project_dir / TEST_DIR

    # Create test files
    test_files = [test_dir / "test1.txt", test_dir / "test2.txt"]

    for file_path in test_files:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Content for {file_path.name}")

    # Test listing files with a mock to handle platform-specific path separators
    with patch("src.file_tools.directory_utils._discover_files") as mock_discover:
        # Configure the mock to return our test files with consistent path separators
        mock_discover.return_value = [
            "testdata/test_file_tools/test1.txt",
            "testdata/test_file_tools/test2.txt",
        ]

        # When gitignore filtering is active, avoid calling the real filter
        with patch(
            "src.file_tools.directory_utils.filter_with_gitignore",
            side_effect=lambda files, *args, **kwargs: files,
        ):
            # Test listing files
            files = list_files(str(TEST_DIR), project_dir=project_dir)

            # Check if all expected files are in the list
            expected_files = {
                "testdata/test_file_tools/test1.txt",
                "testdata/test_file_tools/test2.txt",
            }
            actual_files = set(files)

            # The files should match exactly
            assert actual_files == expected_files


def test_list_files_with_gitignore(project_dir):
    """Test listing files with gitignore filtering."""
    # Create test directory structure
    test_dir = project_dir / TEST_DIR

    # Create test files including ones to be ignored
    (test_dir / "keep.txt").write_text("keep this file")
    (test_dir / "ignore.log").write_text("ignore this file")

    # Create .gitignore file
    gitignore_path = test_dir / ".gitignore"
    gitignore_path.write_text("*.log")

    # Mock the discovery and filtering
    with patch("src.file_tools.directory_utils._discover_files") as mock_discover:
        # Configure the mock to return our test files
        mock_discover.return_value = [
            "testdata/test_file_tools/keep.txt",
            "testdata/test_file_tools/ignore.log",
        ]

        # Mock the filter to remove .log files
        with patch(
            "src.file_tools.directory_utils.filter_with_gitignore"
        ) as mock_filter:
            mock_filter.return_value = ["testdata/test_file_tools/keep.txt"]

            # Test listing files with gitignore filtering
            files = list_files(
                str(TEST_DIR), project_dir=project_dir, use_gitignore=True
            )

            # The .log file should be filtered out
            assert files == ["testdata/test_file_tools/keep.txt"]
            assert not any(f.endswith("ignore.log") for f in files)


def test_list_files_without_gitignore(project_dir):
    """Test listing files without gitignore filtering."""
    # Create test directory structure
    test_dir = project_dir / TEST_DIR

    # Create test files including ones normally ignored
    (test_dir / "keep.txt").write_text("keep this file")
    (test_dir / "dont_ignore.log").write_text("don't ignore this file")

    # Create .gitignore file
    gitignore_path = test_dir / ".gitignore"
    gitignore_path.write_text("*.log")

    # Mock the discovery
    with patch("src.file_tools.directory_utils._discover_files") as mock_discover:
        # Configure the mock to return both files
        mock_discover.return_value = [
            "testdata/test_file_tools/keep.txt",
            "testdata/test_file_tools/dont_ignore.log",
        ]

        # Test listing files without gitignore filtering
        files = list_files(str(TEST_DIR), project_dir=project_dir, use_gitignore=False)

        # Both files should be included
        assert set(files) == {
            "testdata/test_file_tools/keep.txt",
            "testdata/test_file_tools/dont_ignore.log",
        }


def test_list_files_directory_not_found(project_dir):
    """Test listing files in a non-existent directory."""
    non_existent_dir = "testdata/non_existent_dir"

    # Test with a non-existent directory
    with pytest.raises(FileNotFoundError) as excinfo:
        list_files(non_existent_dir, project_dir=project_dir)

    # Verify the error message
    assert f"Directory '{non_existent_dir}' does not exist" in str(excinfo.value)


def test_list_files_not_a_directory(project_dir):
    """Test listing files on a path that is not a directory."""
    # Create a file
    test_file = project_dir / TEST_DIR / "not_a_dir.txt"
    test_file.write_text("This is not a directory")

    # Test with a file path instead of a directory
    with pytest.raises(NotADirectoryError) as excinfo:
        list_files(str(TEST_DIR / "not_a_dir.txt"), project_dir=project_dir)

    # Verify the error message
    assert "is not a directory" in str(excinfo.value)


def test_list_files_with_exception(project_dir):
    """Test handling of unexpected exceptions in list_files."""
    # Mock _discover_files to raise an exception
    with patch(
        "src.file_tools.directory_utils._discover_files",
        side_effect=Exception("Test error"),
    ):
        # Test with a mocked exception
        with pytest.raises(Exception) as excinfo:
            list_files(str(TEST_DIR), project_dir=project_dir)

        # Verify that the exception is propagated
        assert "Test error" in str(excinfo.value)
