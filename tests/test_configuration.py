from vasp_app.config import Settings


def test_default_sqlite_database_uses_configured_data_directory(tmp_path):
    config = Settings(data_dir=tmp_path, database_url="")
    assert config.database_url == "sqlite:///" + str(tmp_path / "atlas.sqlite3")
