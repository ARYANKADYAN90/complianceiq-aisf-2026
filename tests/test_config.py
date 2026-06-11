import os
import pytest
from src.config import Config, get_settings

def test_mock_mode_default_true():
    settings = Config()
    assert settings.mock_mode is True

def test_validate_credentials_raises_without_azure_when_mock_false():
    with pytest.raises(ValueError, match="AZURE_FOUNDRY_PROJECT_ENDPOINT"):
        Config(mock_mode=False).validate_azure_credentials()

def test_settings_loads_from_env_vars(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "false")
    monkeypatch.setenv("AZURE_FOUNDRY_PROJECT_ENDPOINT", "http://test")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "http://test")
    monkeypatch.setenv("AZURE_SEARCH_API_KEY", "test-key")
    
    settings = Config()
    assert settings.mock_mode is False
    assert settings.azure_search_api_key == "test-key"

def test_get_settings_cached():
    import src.config
    src.config.get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

def test_settings_repr_hides_api_keys():
    settings = Config(azure_search_api_key="secret-key")
    repr_str = repr(settings)
    assert "secret-key" not in repr_str
