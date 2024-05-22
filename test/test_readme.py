import doctest

from pathlib import Path


def test_readme():
    doctest.testfile(
        str(Path("..") / "README.md"), verbose=False, optionflags=doctest.ELLIPSIS
    )
