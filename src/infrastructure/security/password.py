import bcrypt

def gerar_hash_senha(senha_plana: str) -> str:
    """
    Gera um hash seguro utilizando o algoritmo bcrypt e 12 rounds de salt.
    
    Args:
        senha_plana (str): A senha em texto limpo.
        
    Returns:
        str: O hash da senha codificado em string UTF-8.
    """
    salt = bcrypt.gensalt(rounds=12)
    senha_bytes = senha_plana.encode("utf-8")
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode("utf-8")

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """
    Verifica se a senha em texto limpo corresponde ao hash fornecido.
    
    Args:
        senha_plana (str): A senha em texto limpo enviada para validação.
        senha_hash (str): O hash seguro da senha armazenado no banco.
        
    Returns:
        bool: True se a senha for válida, False caso contrário.
    """
    senha_bytes = senha_plana.encode("utf-8")
    hash_bytes = senha_hash.encode("utf-8")
    return bcrypt.checkpw(senha_bytes, hash_bytes)


from src.use_cases.autenticacao.autenticar_usuario import ServicoCriptografia

class BcryptServicoCriptografia(ServicoCriptografia):
    """
    Implementação concreta do serviço de criptografia utilizando o bcrypt.
    Implementa o contrato ServicoCriptografia definido nos Casos de Uso.
    """
    def verificar_senha(self, senha_plana: str, senha_hash: str) -> bool:
        return verificar_senha(senha_plana, senha_hash)

    def gerar_hash(self, senha_plana: str) -> str:
        return gerar_hash_senha(senha_plana)

