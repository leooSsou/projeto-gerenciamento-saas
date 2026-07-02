import socket
import time
import sys

def aguardar_postgres() -> None:
    """
    Tenta estabelecer conexão TCP com o container do Postgres
    na porta 5432 por até 30 segundos antes de falhar.
    """
    host = "postgres"
    port = 5432
    max_tentativas = 30

    print(f"Aguardando conexão com o Postgres ({host}:{port})...")
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            # Tenta abrir uma conexão de socket TCP na porta do Postgres
            with socket.create_connection((host, port), timeout=1):
                print("Conexão com o Postgres estabelecida com sucesso!")
                # Delay curto extra para garantir que o processo interno do PG esteja pronto para aceitar conexões
                time.sleep(2)
                sys.exit(0)
        except Exception:
            print(f"Tentativa {tentativa}/{max_tentativas}: banco ainda indisponível. Aguardando...")
            time.sleep(1)
            
    print("Erro: O Postgres não ficou pronto a tempo.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    aguardar_postgres()
