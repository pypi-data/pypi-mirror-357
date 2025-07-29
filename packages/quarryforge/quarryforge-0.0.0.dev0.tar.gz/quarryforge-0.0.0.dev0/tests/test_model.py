"""Unit tests for the quarryforge.model module.

This test suite provides comprehensive coverage for the FossilRepo,
FossilCommit, and FossilTimeline data models.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from quarryforge.config import model_config
from quarryforge.exception import meta_exception, model_exception
from quarryforge.model import FossilCommit, FossilRepo, FossilTimeline


@pytest.fixture
def mock_repo_paths() -> tuple[Path, Path]:
    """Provides mock Path objects for a repository file and workdir."""
    return (Path('/tmp/test.fossil'), Path('/tmp/workdir'))


@pytest.fixture
def mock_commit_data() -> dict[str, Any]:
    """Provides a dictionary of valid data for a FossilCommit instance."""
    return {
        'uuid': 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
        'date': '2023-01-01 12:00:00',
        'author': 'test_user',
        'comment': 'Initial commit',
        'branch': 'trunk',
        'tags': ['v1.0', 'stable'],
        'phase': ['LEAF'],
        'changes': [('ADDED', 'file1.txt'), ('EDITED', 'file2.txt')],
    }


@pytest.fixture
def mock_commit(mock_commit_data: dict[str, Any]) -> FossilCommit:
    """Provides a fully-formed FossilCommit instance for testing."""
    # The validator returns a tuple of the validated values
    with patch(
        'quarryforge.util.model_util.viable_fossil_commit',
        return_value=tuple(mock_commit_data.values()),
    ):
        return FossilCommit(**mock_commit_data)


class TestFossilRepo:
    """Tests for the immutable FossilRepo class."""

    @patch('quarryforge.util.model_util.viable_fossil_repo')
    def test_init_success(
        self, mock_viable_repo: MagicMock, mock_repo_paths: tuple[Path, Path]
    ) -> None:
        """Test successful initialization of FossilRepo for both new and
        existing repos. Verifies that validation is delegated and attributes
        are set correctly.
        """
        file_path, workdir_path = mock_repo_paths
        mock_viable_repo.return_value = (file_path, workdir_path)

        # MC/DC Case 1: is_new=False
        repo_existing = FossilRepo(
            file=file_path, workdir=workdir_path, is_new=False
        )
        mock_viable_repo.assert_called_once_with(
            file_path, workdir_path, False, model_exception.FossilRepoError
        )
        assert repo_existing.file == file_path
        assert repo_existing.workdir == workdir_path
        assert not repo_existing.is_new

        # MC/DC Case 2: is_new=True
        mock_viable_repo.reset_mock()
        repo_new = FossilRepo(file='new.fossil', workdir='new_dir', is_new=True)
        mock_viable_repo.assert_called_once_with(
            'new.fossil', 'new_dir', True, model_exception.FossilRepoError
        )
        assert repo_new.is_new

    @patch('quarryforge.util.model_util.viable_fossil_repo')
    def test_init_validation_failure(self, mock_viable_repo: MagicMock) -> None:
        """Test that FossilRepo.__init__ propagates exceptions from the
        validator.
        """
        mock_viable_repo.side_effect = model_exception.FossilRepoError(
            code='TEST_CODE',
            message='Validation failed',
            user_message='',
            details={},
        )

        with pytest.raises(
            model_exception.FossilRepoError, match='Validation failed'
        ):
            FossilRepo(file='invalid', workdir='invalid', is_new=False)

    def test_immutability(self, mock_repo_paths: tuple[Path, Path]) -> None:
        """Test that __setattr__ and __delattr__ raise ImmutableError after
        initialization.
        """
        file_path, workdir_path = mock_repo_paths
        with patch(
            'quarryforge.util.model_util.viable_fossil_repo',
            return_value=(file_path, workdir_path),
        ):
            repo = FossilRepo(
                file=file_path, workdir=workdir_path, is_new=False
            )

        # Test __setattr__
        with pytest.raises(meta_exception.ImmutableError):
            repo.file = Path('/another/path')  # type: ignore

        # Test __delattr__
        with pytest.raises(meta_exception.ImmutableError):
            del repo.workdir  # type: ignore

    def test_representations(self, mock_repo_paths: tuple[Path, Path]) -> None:
        """Test the __str__ and __repr__ representations."""
        file_path, workdir_path = mock_repo_paths
        with patch(
            'quarryforge.util.model_util.viable_fossil_repo',
            return_value=(file_path, workdir_path),
        ):
            repo = FossilRepo(file=file_path, workdir=workdir_path, is_new=True)

        expected_str = (
            f'Fossil Repository File: {file_path}\n'
            f'Working Directory: {workdir_path}'
        )
        assert str(repo) == expected_str

        expected_repr = (
            f'FossilRepo(file={file_path!r}, is_new=True, '
            f'workdir={workdir_path!r})'
        )
        assert repr(repo) == expected_repr

    def test_equality_and_hash(
        self, mock_repo_paths: tuple[Path, Path]
    ) -> None:
        """Test the __eq__ and __hash__ methods for correctness covering all
        MC/DC branches.
        """
        file_path, workdir_path = mock_repo_paths
        with patch(
            'quarryforge.util.model_util.viable_fossil_repo',
            return_value=(file_path, workdir_path),
        ):
            # Create instances for comparison
            repo1 = FossilRepo(
                file=file_path, workdir=workdir_path, is_new=False
            )
            repo2 = FossilRepo(
                file=file_path, workdir=workdir_path, is_new=False
            )

            # Manually alter internal state for testing __eq__ thoroughly
            repo_diff_file = FossilRepo(
                file=file_path, workdir=workdir_path, is_new=False
            )
            object.__setattr__(
                repo_diff_file,
                model_config.fossil_repo_config().file,
                Path('/different/file.fossil'),
            )

            repo_diff_workdir = FossilRepo(
                file=file_path, workdir=workdir_path, is_new=False
            )
            object.__setattr__(
                repo_diff_workdir,
                model_config.fossil_repo_config().workdir,
                Path('/different/workdir'),
            )

        # __eq__ MC/DC tests
        assert (repo1 == repo2) is True  # Condition: (True and True)
        # Condition: (False and True) -> False
        assert (repo1 == repo_diff_file) is False
        # Condition: (True and False) -> False
        assert (repo1 == repo_diff_workdir) is False
        assert (repo1 == 'not a repo') is False  # Test `isinstance` check

        # __hash__ tests
        assert hash(repo1) == hash(repo2)
        assert hash(repo1) != hash(repo_diff_file)
        assert hash(repo1) != hash(repo_diff_workdir)


class TestFossilCommit:
    """Tests for the immutable FossilCommit class."""

    @patch('quarryforge.util.model_util.viable_fossil_commit')
    def test_init_success(
        self, mock_viable_commit: MagicMock, mock_commit_data: dict[str, Any]
    ) -> None:
        """Test successful initialization with full data."""
        mock_viable_commit.return_value = tuple(mock_commit_data.values())
        commit = FossilCommit(**mock_commit_data)

        mock_viable_commit.assert_called_once_with(
            **mock_commit_data, exception=model_exception.FossilCommitError
        )
        assert commit.uuid == mock_commit_data['uuid']
        assert commit.tags == mock_commit_data['tags']

    @patch('quarryforge.util.model_util.viable_fossil_commit')
    def test_init_minimal_data_and_none_handling(
        self, mock_viable_commit: MagicMock
    ) -> None:
        """Test initialization with minimal data, ensuring None lists become
        empty lists.
        """
        minimal_data = {'uuid': 'u', 'date': 'd', 'author': 'a', 'comment': 'c'}
        validator_return = (
            'u',
            'd',
            'a',
            'c',
            None,
            None,
            None,
            None,
        )  # branch, tags, phase, changes
        mock_viable_commit.return_value = validator_return

        commit = FossilCommit(**minimal_data)
        assert commit.branch is None
        assert commit.tags == []  # Test None -> []
        assert commit.phase is None
        assert commit.changes == []  # Test None -> []

    @patch('quarryforge.util.model_util.viable_fossil_commit')
    def test_init_validation_failure(
        self, mock_viable_commit: MagicMock
    ) -> None:
        """Test that __init__ propagates exceptions from the validator."""
        mock_viable_commit.side_effect = model_exception.FossilCommitError(
            code='TEST_CODE',
            message='Invalid data',
            user_message='',
            details={},
        )
        with pytest.raises(
            model_exception.FossilCommitError, match='Invalid data'
        ):
            FossilCommit(uuid='', date='', author='', comment='')

    def test_properties_and_get_hash(
        self, mock_commit: FossilCommit, mock_commit_data: dict
    ) -> None:
        """Verify all properties and get_hash() return correct data."""
        print(f'mockuuid: {mock_commit.uuid}')
        print(f'mockdata: {mock_commit_data["uuid"]}')
        print(f'mockgethash: {mock_commit.get_hash()}')
        print(f'mockdata12: {mock_commit_data["uuid"][:12]}')
        assert mock_commit.uuid == mock_commit_data['uuid']
        assert mock_commit.get_hash() == mock_commit_data['uuid'][:12]

    @patch('quarryforge.util.model_util.viable_fossil_commit')
    def test_repr_representation_coverage(
        self, mock_viable_commit: MagicMock
    ) -> None:
        """Test __repr__ for various data combinations to ensure full MC/DC
        coverage.
        """
        # MC/DC Case 1: Full data with all list types
        full_data = {
            'uuid': 'id',
            'date': 'd',
            'author': 'a',
            'comment': 'c',
            'branch': 'b',
            'tags': ['t1'],
            'phase': ['p1'],
            'changes': [('ADDED', 'f1')],
        }
        mock_viable_commit.return_value = tuple(full_data.values())
        commit_full = FossilCommit(**full_data)
        repr_full = repr(commit_full)
        assert "tags=['t1']" in repr_full
        assert "changes=[('ADDED', 'f1')]" in repr_full

        # MC/DC Case 2: Data with non-string/tuple items in a list
        # (to test final else)
        other_data = full_data.copy()
        other_data['changes'] = [1, None]  # type: ignore
        mock_viable_commit.return_value = tuple(other_data.values())
        commit_other = FossilCommit(**other_data)
        assert 'changes=[1, None]' in repr(commit_other)


class TestFossilTimeline:
    """Tests for the FossilTimeline container class."""

    def test_init_mc_dc_cases(self, mock_commit: FossilCommit) -> None:
        """Covers all MC/DC paths for __init__."""
        # MC/DC Case 1: commits=None (evaluates to False in `commits or []`)
        timeline_none = FossilTimeline(commits=None)
        assert len(timeline_none) == 0

        # MC/DC Case 2: commits=[] (evaluates to False in `commits or []`)
        timeline_empty = FossilTimeline(commits=[])
        assert len(timeline_empty) == 0

        # MC/DC Case 3: Raises on invalid type (not a list)
        with pytest.raises(model_exception.FossilTimelineError):
            FossilTimeline(commits=('not', 'a', 'list'))  # type: ignore

        # MC/DC Case 4: Raises on invalid content (contains non-FossilCommit)
        with pytest.raises(model_exception.FossilTimelineError):
            FossilTimeline(commits=[mock_commit, 'not a commit'])  # type: ignore

    def test_init_reverses_order(self, mock_commit: FossilCommit) -> None:
        """Test that the incoming commit list is reversed for chronological
        order.
        """
        commit1 = mock_commit
        commit2_data = {
            'uuid': '2',
            'date': '2',
            'author': 'a2',
            'comment': 'c2',
        }
        with patch(
            'quarryforge.util.model_util.viable_fossil_commit',
            return_value=tuple(commit2_data.values())
            + (None, None, None, None),
        ):
            commit2 = FossilCommit(**commit2_data)

        timeline = FossilTimeline(
            commits=[commit2, commit1]
        )  # Newest to oldest
        assert timeline[0] is commit1  # Should now be oldest
        assert timeline[1] is commit2  # Should now be newest

    def test_dunder_methods(self, mock_commit: FossilCommit) -> None:
        """Test __len__, __getitem__, __iter__, __repr__, and __str__."""
        timeline = FossilTimeline(commits=[mock_commit])
        timeline.add(mock_commit)  # Test add method

        # __len__
        assert len(timeline) == 2

        # __getitem__
        assert timeline[0] is mock_commit
        with pytest.raises(IndexError):
            _ = timeline[2]

        # __iter__
        iterated_commits = [c for c in timeline]
        assert len(iterated_commits) == 2

        # __repr__ and __str__
        assert repr(timeline) == 'FossilTimeline(commits=2 commits)'
        assert str(timeline) == 'Fossil Timeline with 2 commits.'
