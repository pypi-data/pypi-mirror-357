import argparse
from .secrets import set_secret, get_secret, list_secrets, delete_secret

HELP_TEXT = """
Exemplos de uso:

  Salvar um segredo: appserver-secrets set --service github --key GITHUB_TOKEN --password ghp_xxx
  Recuperar um segredo: appserver-secrets get --service github --key GITHUB_TOKEN
  Listar todos os segredos: appserver-secrets list
  Remover um segredo: appserver-secrets delete --service github --key GITHUB_TOKEN

  Verbose (exibe detalhes):
    appserver-secrets get --service github --key GITHUB_TOKEN --verbose
    appserver-secrets list --verbose
"""

def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador de segredos local com keyring + índice.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_TEXT
    )
    subparsers = parser.add_subparsers(dest="command")

    set_parser = subparsers.add_parser("set", help="Gravar token no keyring")
    set_parser.add_argument("--service", required=True, help="Nome do serviço (ex: github, pypi)")
    set_parser.add_argument("--key", required=True, help="Nome da chave (ex: GITHUB_TOKEN)")
    set_parser.add_argument("--password", required=True, help="Senha/token a ser armazenado")

    get_parser = subparsers.add_parser("get", help="Recuperar token do keyring")
    get_parser.add_argument("--service", required=True, help="Nome do serviço (ex: github, pypi)")
    get_parser.add_argument("--key", required=True, help="Nome da chave (ex: GITHUB_TOKEN)")
    get_parser.add_argument("--verbose", action="store_true", help="Exibe saída completa com nome do serviço e chave")

    list_parser = subparsers.add_parser("list", help="Listar todos os tokens conhecidos")
    list_parser.add_argument("--verbose", action="store_true", help="Exibe saída completa com nome do serviço e chave")

    del_parser = subparsers.add_parser("delete", help="Apagar token do keyring")
    del_parser.add_argument("--service", required=True, help="Nome do serviço (ex: github, pypi)")
    del_parser.add_argument("--key", required=True, help="Nome da chave (ex: GITHUB_TOKEN)")

    args = parser.parse_args()

    if args.command == "set":
        set_secret(args.service, args.key, args.password)
        print("SECRET_SAVED")
        # print("Segredo salvo com sucesso.")
    elif args.command == "get":
        password = get_secret(args.service, args.key)
        if password:
            if args.verbose:
                print(f"{args.service} / {args.key} = {password}")
            else:
                print(password)
        else:
            print("SECRET_NOT_FOUND")  # Use a constant for better maintainability
            # print("Segredo não encontrado.")
    elif args.command == "delete":
        delete_secret(args.service, args.key)
        print("SECRET_DELETED")  # Use a constant for better maintainability
        # print("Segredo removido com sucesso.")
    elif args.command == "list":
        index = list_secrets()
        if not index:
            print("SECRET_INDEX_EMPTY")  # Use a constant for better maintainability
            # print("ℹ️ Nenhum segredo registrado.")
        else:
            # print("SECRET_INDEX")
            # print("📋 Segredos registrados:")
            for service in sorted(index):
                for key in sorted(index[service]):
                    print(f"{service} / {key}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
