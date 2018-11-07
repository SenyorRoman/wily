import wily.__main__ as main
from mock import patch
from click.testing import CliRunner
from git import Repo, Actor
import pathlib
import pytest


@pytest.fixture
def builddir(tmpdir):
    """ Create a project and build it """
    repo = Repo.init(path=tmpdir)
    tmppath = pathlib.Path(tmpdir)

    # Write a test file to the repo
    with open(tmppath / "test.py", "w") as test_txt:
        test_txt.write("import abc")

    index = repo.index
    index.add(["test.py"])

    author = Actor("An author", "author@example.com")
    committer = Actor("A committer", "committer@example.com")

    index.commit("basic test", author=author, committer=committer)

    runner = CliRunner()
    result = runner.invoke(main.cli, ["--debug", "--path", tmpdir, "build"])
    assert result.exit_code == 0, result.stdout

    return tmpdir


def test_build_not_git_repo(tmpdir):
    """
    Test that build fails in a non-git directory
    """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", tmpdir, "build"])
        assert result.exit_code == 1, result.stdout


def test_build_invalid_path(tmpdir):
    """
    Test that build fails with a garbage path
    """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", "/fo/v/a", "build"])
        assert result.exit_code == 1, result.stdout


def test_build(tmpdir):
    """
    Test that build fails in a non-git directory
    """
    repo = Repo.init(path=tmpdir)
    tmppath = pathlib.Path(tmpdir)

    # Write a test file to the repo
    with open(tmppath / "test.py", "w") as test_txt:
        test_txt.write("import abc")

    index = repo.index
    index.add(["test.py"])

    author = Actor("An author", "author@example.com")
    committer = Actor("A committer", "committer@example.com")

    index.commit("basic test", author=author, committer=committer)

    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--debug", "--path", tmpdir, "build"])
        assert result.exit_code == 0, result.stdout

    cache_path = tmpdir / ".wily"
    assert cache_path.exists()


def test_report(builddir):
    """
    Test that report works with a build
    """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", builddir, "report", "test.py", "raw.loc"])
        assert result.exit_code == 0, result.stdout


def test_index(builddir):
    """
    Test that index works with a build
    """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", builddir, "index"])
        assert result.exit_code == 0, result.stdout


def test_list_metrics(builddir):
    """
    Test that list-metrics works with a build
    """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", builddir, "list-metrics"])
        assert result.exit_code == 0, result.stdout


def test_clean(builddir):
    """ Test the clean feature """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", builddir, "clean"])
        assert result.exit_code == 0, result.stdout
    cache_path = pathlib.Path(builddir) / ".wily"
    assert not cache_path.exists()


def test_graph(builddir):
    """ Test the graph feature """
    with patch("wily.logger") as logger:
        runner = CliRunner()
        result = runner.invoke(main.cli, ["--path", builddir, "graph", "test.py", "raw.loc"])
        assert result.exit_code == 0, result.stdout

    report_path = pathlib.Path(builddir) / "tempreport.html"
    assert report_path.exists()