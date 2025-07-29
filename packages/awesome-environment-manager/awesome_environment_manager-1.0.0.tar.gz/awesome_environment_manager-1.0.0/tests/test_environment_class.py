import pytest
from typing import List
import os
import sys
from unittest.mock import patch
from aem import EnvironmentClass


class EnvironmentVariablesTestClass(EnvironmentClass):
    # Klassenvariablen mit Typ-Hints
    test_string: str = "default_string"
    test_int: int = 0
    test_float: float = 0.0
    test_bool: bool = False
    test_list: List[str] = []
    test_list_int: List[int] = []
    test_dict: dict = {}


def test_environment_variables(monkeypatch):
    # Environment Variablen setzen
    test_env = {
        "test_string": "test_value",
        "test_int": "42",
        "test_float": "3.14",
        "test_bool": "true",
        "test_list": "item1;item2;item3",
        "test_list_int": "1;2;3",
        "test_dict": "key1:value1;key2:value2",
    }

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)

    # Instanz der Testklasse erstellen
    env = EnvironmentVariablesTestClass()

    # Überprüfung der Werte
    assert env.test_string == "test_value"
    assert env.test_int == 42
    assert env.test_float == 3.14
    assert env.test_bool is True
    assert env.test_list == ["item1", "item2", "item3"]
    assert env.test_list_int == [1, 2, 3]
    assert env.test_dict == {"key1": "value1", "key2": "value2"}


def test_invalid_type_conversion():
    # Ungültige Typkonvertierung testen
    with pytest.raises(ValueError):
        EnvironmentClass._convert_type("not_a_number", int)

    with pytest.raises(ValueError):
        EnvironmentClass._convert_type("not_a_float", float)

    with pytest.raises(ValueError):
        EnvironmentClass._convert_type("invalid:dict:format", dict)


def test_bool_conversion():
    # Verschiedene Boolean-Werte testen
    assert EnvironmentClass._convert_type("true", bool) is True
    assert EnvironmentClass._convert_type("1", bool) is True
    assert EnvironmentClass._convert_type("yes", bool) is True
    assert EnvironmentClass._convert_type("y", bool) is True
    assert EnvironmentClass._convert_type("on", bool) is True
    assert EnvironmentClass._convert_type("false", bool) is False
    assert EnvironmentClass._convert_type("0", bool) is False
    assert EnvironmentClass._convert_type("no", bool) is False


def test_empty_values():
    # Leere Werte testen
    assert EnvironmentClass._convert_type("", list) == []
    assert EnvironmentClass._convert_type("", List[str]) == []
    assert EnvironmentClass._convert_type("", List[int]) == []


def test_missing_environment_variables(monkeypatch):
    # Alle Umgebungsvariablen entfernen
    for var in os.environ:
        monkeypatch.delenv(var, raising=False)

    # Instanz erstellen - sollte die Standardwerte verwenden
    env = EnvironmentVariablesTestClass()

    assert env.test_string == "default_string"
    assert env.test_int == 0
    assert env.test_float == 0.0
    assert env.test_bool is False
    assert env.test_list == []
    assert env.test_list_int == []
    assert env.test_dict == {}


def test_dotenv_success():
    mock_dotenv = type("DotEnv", (), {"load_dotenv": lambda: None})

    with patch.dict("sys.modules", {"dotenv": mock_dotenv}):
        # Erstelle eine neue Instanz der Klasse
        EnvironmentClass()
        assert True  # Wenn wir hier ankommen, wurde load_dotenv erfolgreich importiert


def test_dotenv_import_error():
    with patch.dict("sys.modules", {"dotenv": None}):
        # Erstelle eine neue Instanz der Klasse
        EnvironmentClass()
        assert True  # Wenn wir hier ankommen, wurde die ImportError gefangen

