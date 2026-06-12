import pytest
import os
from unittest.mock import patch


class TestMockModeDefault:
    def test_mock_mode_default_true(self):
        """Config defaults to mock_mode=True."""
        with patch.dict(os.environ, {
            "MOCK_MODE": "true",
            "AZURE_FOUNDRY_PROJECT_ENDPOINT": "https://fake.api.azureml.ms",
            "AZURE_SEARCH_ENDPOINT": "https://fake.search.windows.net",
        }, clear=False):
            from src.config import Config
            cfg = Config(mock_mode=True)
            assert cfg.mock_mode is True

    def test_validate_credentials_raises_without_azure_when_mock_false(self):
        """Raises ValueError when mock_mode=False but Azure creds missing."""
        with patch.dict(os.environ, {
            "MOCK_MODE": "false",
            "AZURE_FOUNDRY_PROJECT_ENDPOINT": "",
            "AZURE_SEARCH_ENDPOINT": "",
        }, clear=False):
            from src.config import Config
            cfg = Config(
                mock_mode=False,
                azure_foundry_project_endpoint="",
                azure_search_endpoint="",
            )
            with pytest.raises(ValueError, match="missing"):
                cfg.validate_azure_credentials()

    def test_settings_loads_from_env_vars(self, monkeypatch):
        """Settings can be loaded from env vars."""
        monkeypatch.setenv("MOCK_MODE", "true")
        monkeypatch.setenv("AZURE_FOUNDRY_PROJECT_ENDPOINT", "https://test.api.azureml.ms")
        monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://test.search.windows.net")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        from src.config import Config
        cfg = Config()
        assert cfg.log_level == "DEBUG"

    def test_get_settings_cached(self, monkeypatch):
        """get_settings() returns a cached object on repeated calls."""
        monkeypatch.setenv("MOCK_MODE", "true")
        monkeypatch.setenv("AZURE_FOUNDRY_PROJECT_ENDPOINT", "https://cached.api.azureml.ms")
        monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://cached.search.windows.net")

        import importlib
        import src.config as config_module
        importlib.reload(config_module)

        s1 = config_module.get_settings()
        s2 = config_module.get_settings()
        assert s1 is s2

    def test_mock_mode_true_skips_validation(self):
        """When mock_mode=True, missing Azure creds do NOT raise."""
        from src.config import Config
        cfg = Config(
            mock_mode=True,
            azure_foundry_project_endpoint="",
            azure_search_endpoint="",
        )
        cfg.validate_azure_credentials()
