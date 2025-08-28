"""
Script de setup para o projeto Azure DevOps Integration
"""

import os
import sys
import subprocess


def install_dependencies():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")

    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def setup_python_path():
    """Configura o Python path para incluir o src"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(project_root, 'src')

    if src_path not in sys.path:
        sys.path.insert(0, src_path)
        print(f"✅ Adicionado ao Python path: {src_path}")


def validate_structure():
    """Valida se a estrutura do projeto está correta"""
    print("🔍 Validando estrutura do projeto...")

    required_dirs = [
        'src/azure_devops_integration',
        'tests/fixtures',
        'tests/unit',
        'tests/integration',
        'dags',
        'config'
    ]

    required_files = [
        'src/azure_devops_integration/__init__.py',
        'src/azure_devops_integration/client.py',
        'src/azure_devops_integration/config.py',
        'tests/fixtures/mock_data.py',
        'requirements.txt',
        'README.md'
    ]

    missing_dirs = []
    missing_files = []

    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)

    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_dirs or missing_files:
        print("❌ Estrutura do projeto incompleta:")
        for missing_dir in missing_dirs:
            print(f"  📁 Diretório ausente: {missing_dir}")
        for missing_file in missing_files:
            print(f"  📄 Arquivo ausente: {missing_file}")
        return False

    print("✅ Estrutura do projeto validada!")
    return True


def test_imports():
    """Testa se os imports funcionam corretamente"""
    print("🧪 Testando imports...")

    setup_python_path()

    try:
        # Testa import do módulo principal
        from azure_devops_integration import AzureDevOpsClient, create_azure_devops_client
        print("✅ Import do cliente funcionando")

        # Testa import das configurações
        from azure_devops_integration.config import AZURE_DEVOPS_CONFIG
        print("✅ Import das configurações funcionando")

        # Testa import dos fixtures de teste
        from tests.fixtures import MOCK_TICKETS, MOCK_CREDENTIALS
        print("✅ Import dos fixtures de teste funcionando")

        return True

    except ImportError as e:
        print(f"❌ Erro no import: {e}")
        return False


def show_next_steps():
    """Mostra os próximos passos para o usuário"""
    print("\n" + "="*60)
    print("🎉 Setup concluído! Próximos passos:")
    print("="*60)
    print()
    print("1. 🧪 Execute os testes:")
    print("   python run_tests.py")
    print()
    print("2. ⚙️ Configure as variáveis do Airflow:")
    print("   - azure_devops_organization")
    print("   - azure_devops_project")
    print("   - azure_devops_pat")
    print("   - azure_devops_area_path (opcional)")
    print()
    print("3. 📋 Use o módulo em produção:")
    print("   from azure_devops_integration import create_azure_devops_client")
    print()
    print("4. 📖 Consulte o README.md para mais detalhes")
    print()


def main():
    """Função principal do setup"""
    print("🚀 Setup do Azure DevOps Integration")
    print("="*60)

    # Valida estrutura
    if not validate_structure():
        print("\n❌ Setup falhou - estrutura do projeto incompleta")
        return False

    # Instala dependências
    if not install_dependencies():
        print("\n❌ Setup falhou - erro ao instalar dependências")
        return False

    # Testa imports
    if not test_imports():
        print("\n❌ Setup falhou - erro nos imports")
        return False

    # Mostra próximos passos
    show_next_steps()

    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
