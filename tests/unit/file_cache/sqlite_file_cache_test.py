import time
from pathlib import Path
from tempfile import NamedTemporaryFile

import polars as pl

from buckaroo.file_cache.sqlite_file_cache import SQLiteFileCache
from buckaroo.file_cache.base import Executor, ProgressNotification
from tests.unit.file_cache.bisector_test import SimpleColumnExecutor


def create_tempfile_with_text(text: str) -> Path:
    with NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write(text)
        f.flush()
        return Path(f.name)


def test_sqlite_filecache_metadata_and_upsert():
    fc = SQLiteFileCache(":memory:")
    path_1 = create_tempfile_with_text("hello")
    assert not fc.check_file(path_1)
    md = {'alpha': 1}
    fc.add_metadata(path_1, md)
    assert fc.check_file(path_1)
    assert fc.get_file_metadata(path_1) == md
    fc.upsert_file_metadata(path_1, {'beta': 2})
    assert fc.get_file_metadata(path_1) == {'alpha':1, 'beta':2}

    # change file contents -> mtime increases -> cache invalid
    path_1.write_text("world")
    time.sleep(3) #Delay for CI
    assert not fc.check_file(path_1)


def test_sqlite_filecache_executor_integration():
    # Run executor and verify series results persisted in sqlite
    df = pl.DataFrame({'a1': [10,20,30], 'b2': [1,2,3]})
    ldf = df.lazy()
    fc = SQLiteFileCache(":memory:")
    collected: list[ProgressNotification] = []
    def listener(p:ProgressNotification) -> None:
        collected.append(p)

    ex = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    ex.run()
    # compute expected series hashes/results to cross-check what was stored
    exec_ = SimpleColumnExecutor()
    args = exec_.get_execution_args({'a1': {}, 'b2': {}})  # type: ignore
    results = exec_.execute(ldf, args)
    for col, col_res in results.items():
        stored = fc.get_series_results(col_res.series_hash)
        assert stored is not None
        assert stored.get('len') == 3

