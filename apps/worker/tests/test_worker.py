from pixel_worker.main import main


def test_worker_check_exits_cleanly() -> None:
    assert main([]) == 0


def test_worker_ingest_indexes_fixtures() -> None:
    assert main(["ingest"]) == 0
