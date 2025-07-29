import os
import pytest
from savekit import SaveKit

TEST_FILE = "test_savekit.json"

@pytest.fixture
def store():
    # Crear instancia usando archivo de prueba
    kit = SaveKit(TEST_FILE)
    # Limpiar datos antes de cada test
    kit.reset()
    yield kit
    # Limpiar archivo después de cada test
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)

def test_put_and_get(store):
    store.put("key1", "value1")
    assert store.get("key1") == "value1"

def test_get_default(store):
    assert store.get("nonexistent", default=42) == 42

def test_remove_key(store):
    store.put("key2", 100)
    store.remove("key2")
    assert store.get("key2") is None

def test_get_all(store):
    store.put("k1", 1)
    store.put("k2", 2)
    all_data = store.get_all()
    assert isinstance(all_data, dict)
    assert all_data == {"k1": 1, "k2": 2}

def test_reset(store):
    store.put("temp", "data")
    store.reset()
    assert store.get_all() == {}

def test_reload(store):
    store.put("reload_test", "initial")
    # Modify file directly to simulate external change
    with open(TEST_FILE, "w") as f:
        f.write('{"reload_test": "changed"}')
    store.reload()
    assert store.get("reload_test") == "changed"
