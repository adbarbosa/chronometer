#!/usr/bin/env python3
"""Teste da funcionalidade ConfigManager."""

import json
import sys
from pathlib import Path

# Adicionar caminho ao módulo
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager


def test_save_and_load():
    """Teste: guardar e carregar preferência de monitor."""
    print("🧪 Teste 1: Guardar e carregar preferência de monitor")
    
    # Guardar índice 2
    ConfigManager.save_monitor_index(2)
    loaded = ConfigManager.get_last_monitor_index()
    
    assert loaded == 2, f"Esperado 2, obtido {loaded}"
    print(f"  ✅ Guardou índice 2, carregou: {loaded}")


def test_default_value():
    """Teste: valor por defeito."""
    print("\n🧪 Teste 2: Obter valor por defeito")
    
    # Limpar ficheiro
    if ConfigManager.CONFIG_FILE.exists():
        ConfigManager.CONFIG_FILE.unlink()
    
    loaded = ConfigManager.get_last_monitor_index(default=1)
    assert loaded == 1, f"Esperado 1 (default), obtido {loaded}"
    print(f"  ✅ Valor por defeito funcionando: {loaded}")


def test_type_conversion():
    """Teste: conversão de tipo."""
    print("\n🧪 Teste 3: Conversão de tipo (string para int)")
    
    # Guardar como string (simulando ficheiro corrompido)
    ConfigManager.save("last_monitor_index", "3")
    loaded = ConfigManager.get_last_monitor_index()
    
    assert isinstance(loaded, int), f"Esperado int, obtido {type(loaded)}"
    assert loaded == 3, f"Esperado 3, obtido {loaded}"
    print(f"  ✅ Conversão bem-sucedida: string '3' → int {loaded}")


def test_config_file_location():
    """Teste: localização do ficheiro."""
    print("\n🧪 Teste 4: Localização do ficheiro de configuração")
    
    expected_dir = Path.home() / ".chronometer"
    expected_file = expected_dir / "config.json"
    
    assert ConfigManager.CONFIG_DIR == expected_dir, f"Diretório incorreto: {ConfigManager.CONFIG_DIR}"
    assert ConfigManager.CONFIG_FILE == expected_file, f"Ficheiro incorreto: {ConfigManager.CONFIG_FILE}"
    
    print(f"  ✅ Diretório: {expected_dir}")
    print(f"  ✅ Ficheiro: {expected_file}")
    
    # Verificar se foi criado
    if ConfigManager.CONFIG_FILE.exists():
        with open(ConfigManager.CONFIG_FILE, "r") as f:
            content = json.load(f)
        print(f"  ✅ Conteúdo do ficheiro: {content}")


def test_generic_get_save():
    """Teste: métodos genéricos get/save."""
    print("\n🧪 Teste 5: Métodos genéricos get/save")
    
    # Guardar uma chave customizada
    ConfigManager.save("test_key", "test_value")
    loaded = ConfigManager.get("test_key")
    
    assert loaded == "test_value", f"Esperado 'test_value', obtido {loaded}"
    print(f"  ✅ Guardou e carregou chave customizada: {loaded}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 TESTES DE PERSISTÊNCIA DO CONFIGMANAGER")
    print("=" * 60)
    
    try:
        test_save_and_load()
        test_default_value()
        test_type_conversion()
        test_config_file_location()
        test_generic_get_save()
        
        print("\n" + "=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
