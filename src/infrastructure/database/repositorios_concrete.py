from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from src.domain.repositories.tenant_repository import TenantRepository
from src.domain.repositories.usuario_repository import UsuarioRepository
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.repositories.cliente_repository import ClienteRepository
from src.domain.repositories.fornecedor_repository import FornecedorRepository
from src.domain.repositories.estoque_saldo_repository import EstoqueSaldoRepository
from src.domain.repositories.estoque_movimentacao_repository import EstoqueMovimentacaoRepository
from src.domain.entities.tenant import Tenant
from src.domain.entities.usuario import Usuario
from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.cliente import Cliente
from src.domain.entities.fornecedor import Fornecedor
from src.domain.entities.estoque_saldo import EstoqueSaldo
from src.domain.entities.estoque_movimentacao import EstoqueMovimentacao
from src.infrastructure.database.models import (
    TenantModel,
    UsuarioModel,
    LojaModel,
    ProdutoModel,
    ClienteModel,
    FornecedorModel,
    EstoqueSaldoModel,
    EstoqueMovimentacaoModel,
)

class RepositorioTenantSQLAlchemy(TenantRepository):
    """
    Implementação concreta do repositório de Tenant usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, tenant: Tenant) -> Tenant:
        model = self.db.query(TenantModel).filter(TenantModel.id == tenant.id).first()
        if not model:
            model = TenantModel(
                id=tenant.id,
                nome_fantasia=tenant.nome_fantasia,
                razao_social=tenant.razao_social,
                cnpj=tenant.cnpj,
                data_cadastro=tenant.data_cadastro
            )
            self.db.add(model)
        else:
            model.nome_fantasia = tenant.nome_fantasia
            model.razao_social = tenant.razao_social
            model.cnpj = tenant.cnpj
            model.data_cadastro = tenant.data_cadastro
            
        # O commit agora é delegado para a transação geral da rota/caso de uso.
        # Apenas damos flush para carregar possíveis IDs e gerados pelo banco.
        self.db.flush()
        
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )

    def obter_por_cnpj(self, cnpj: str) -> Optional[Tenant]:
        model = self.db.query(TenantModel).filter(TenantModel.cnpj == cnpj).first()
        if not model:
            return None
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )

    def obter_por_id(self, id: UUID) -> Optional[Tenant]:
        model = self.db.query(TenantModel).filter(TenantModel.id == id).first()
        if not model:
            return None
        return Tenant(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            data_cadastro=model.data_cadastro
        )


class RepositorioUsuarioSQLAlchemy(UsuarioRepository):
    """
    Implementação concreta do repositório de Usuario usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, usuario: Usuario) -> Usuario:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == usuario.id).first()
        if not model:
            model = UsuarioModel(
                id=usuario.id,
                nome=usuario.nome,
                email=usuario.email,
                senha_hash=usuario.senha_hash,
                role=usuario.role,
                tenant_id=usuario.tenant_id,
                loja_atribuida_id=usuario.loja_atribuida_id
            )
            self.db.add(model)
        else:
            model.nome = usuario.nome
            model.email = usuario.email
            model.senha_hash = usuario.senha_hash
            model.role = usuario.role
            model.loja_atribuida_id = usuario.loja_atribuida_id
            model.tenant_id = usuario.tenant_id
            
        self.db.flush()
        
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )

    def obter_por_email(self, email: str) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        if not model:
            return None
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )

    def obter_por_id(self, id: UUID) -> Optional[Usuario]:
        model = self.db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
        if not model:
            return None
        return Usuario(
            id=model.id,
            nome=model.nome,
            email=model.email,
            senha_hash=model.senha_hash,
            role=model.role,
            tenant_id=model.tenant_id,
            loja_atribuida_id=model.loja_atribuida_id
        )


class RepositorioLojaSQLAlchemy(LojaRepository):
    """
    Implementação concreta do repositório de Loja usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, loja: Loja) -> Loja:
        self.db.info["tenant_id"] = loja.tenant_id
        model = self.db.query(LojaModel).filter(LojaModel.id == loja.id).first()
        
        if not model:
            model = LojaModel(
                id=loja.id,
                nome=loja.nome,
                cnpj=loja.cnpj,
                endereco=loja.endereco,
                tenant_id=loja.tenant_id,
                ativo=loja.ativo
            )
            self.db.add(model)
        else:
            model.nome = loja.nome
            model.cnpj = loja.cnpj
            model.endereco = loja.endereco
            model.ativo = loja.ativo
            
        self.db.flush()
        
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Loja]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(LojaModel).filter(LojaModel.id == id).first()
        if not model:
            return None
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Loja]:
        self.db.info["tenant_id"] = tenant_id
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        model = self.db.query(LojaModel).filter(LojaModel.cnpj == cnpj_limpo).first()
        if not model:
            return None
        return Loja(
            id=model.id,
            nome=model.nome,
            cnpj=model.cnpj,
            endereco=model.endereco,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def listar_todas(self, tenant_id: UUID) -> List[Loja]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(LojaModel).all()
        return [
            Loja(
                id=m.id,
                nome=m.nome,
                cnpj=m.cnpj,
                endereco=m.endereco,
                tenant_id=m.tenant_id,
                ativo=m.ativo
            )
            for m in models
        ]


class RepositorioProdutoSQLAlchemy(ProdutoRepository):
    """
    Implementação concreta do repositório de Produto usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, produto: Produto) -> Produto:
        self.db.info["tenant_id"] = produto.tenant_id
        model = self.db.query(ProdutoModel).filter(ProdutoModel.id == produto.id).first()
        
        if not model:
            model = ProdutoModel(
                id=produto.id,
                nome=produto.nome,
                sku=produto.sku,
                preco_custo=produto.preco_custo,
                preco_venda=produto.preco_venda,
                markup=produto.markup,
                codigo_barras=produto.codigo_barras,
                fornecedor_id=produto.fornecedor_id,
                tenant_id=produto.tenant_id,
                ativo=produto.ativo
            )
            self.db.add(model)
        else:
            model.nome = produto.nome
            model.sku = produto.sku
            model.preco_custo = produto.preco_custo
            model.preco_venda = produto.preco_venda
            model.markup = produto.markup
            model.codigo_barras = produto.codigo_barras
            model.fornecedor_id = produto.fornecedor_id
            model.ativo = produto.ativo
            
        self.db.flush()
        
        return Produto(
            id=model.id,
            nome=model.nome,
            sku=model.sku,
            preco_custo=model.preco_custo,
            preco_venda=model.preco_venda,
            markup=model.markup,
            tenant_id=model.tenant_id,
            codigo_barras=model.codigo_barras,
            fornecedor_id=model.fornecedor_id,
            ativo=model.ativo
        )

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Produto]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(ProdutoModel).filter(ProdutoModel.id == id).first()
        if not model:
            return None
        return Produto(
            id=model.id,
            nome=model.nome,
            sku=model.sku,
            preco_custo=model.preco_custo,
            preco_venda=model.preco_venda,
            markup=model.markup,
            tenant_id=model.tenant_id,
            codigo_barras=model.codigo_barras,
            fornecedor_id=model.fornecedor_id,
            ativo=model.ativo
        )

    def obter_por_sku(self, sku: str, tenant_id: UUID) -> Optional[Produto]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(ProdutoModel).filter(ProdutoModel.sku == sku).first()
        if not model:
            return None
        return Produto(
            id=model.id,
            nome=model.nome,
            sku=model.sku,
            preco_custo=model.preco_custo,
            preco_venda=model.preco_venda,
            markup=model.markup,
            tenant_id=model.tenant_id,
            codigo_barras=model.codigo_barras,
            fornecedor_id=model.fornecedor_id,
            ativo=model.ativo
        )

    def obter_por_codigo_barras(self, codigo_barras: str, tenant_id: UUID) -> Optional[Produto]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(ProdutoModel).filter(ProdutoModel.codigo_barras == codigo_barras.strip()).first()
        if not model:
            return None
        return Produto(
            id=model.id,
            nome=model.nome,
            sku=model.sku,
            preco_custo=model.preco_custo,
            preco_venda=model.preco_venda,
            markup=model.markup,
            tenant_id=model.tenant_id,
            codigo_barras=model.codigo_barras,
            fornecedor_id=model.fornecedor_id,
            ativo=model.ativo
        )

    def listar_todos(self, tenant_id: UUID) -> List[Produto]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(ProdutoModel).all()
        return [
            Produto(
                id=m.id,
                nome=m.nome,
                sku=m.sku,
                preco_custo=m.preco_custo,
                preco_venda=m.preco_venda,
                markup=m.markup,
                tenant_id=m.tenant_id,
                codigo_barras=m.codigo_barras,
                fornecedor_id=m.fornecedor_id,
                ativo=m.ativo
            )
            for m in models
        ]



class RepositorioClienteSQLAlchemy(ClienteRepository):
    """
    Implementação concreta do repositório de Cliente usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, cliente: Cliente) -> Cliente:
        self.db.info["tenant_id"] = cliente.tenant_id
        model = self.db.query(ClienteModel).filter(ClienteModel.id == cliente.id).first()
        
        if not model:
            model = ClienteModel(
                id=cliente.id,
                nome=cliente.nome,
                email=cliente.email,
                documento=cliente.documento,
                tenant_id=cliente.tenant_id,
                ativo=cliente.ativo
            )
            self.db.add(model)
        else:
            model.nome = cliente.nome
            model.email = cliente.email
            model.documento = cliente.documento
            model.ativo = cliente.ativo
            
        self.db.flush()
        
        return Cliente(
            id=model.id,
            nome=model.nome,
            email=model.email,
            documento=model.documento,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Cliente]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(ClienteModel).filter(ClienteModel.id == id).first()
        if not model:
            return None
        return Cliente(
            id=model.id,
            nome=model.nome,
            email=model.email,
            documento=model.documento,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_documento(self, documento: str, tenant_id: UUID) -> Optional[Cliente]:
        self.db.info["tenant_id"] = tenant_id
        doc_limpo = "".join(filter(str.isdigit, documento))
        model = self.db.query(ClienteModel).filter(ClienteModel.documento == doc_limpo).first()
        if not model:
            return None
        return Cliente(
            id=model.id,
            nome=model.nome,
            email=model.email,
            documento=model.documento,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def listar_todos(self, tenant_id: UUID) -> List[Cliente]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(ClienteModel).all()
        return [
            Cliente(
                id=m.id,
                nome=m.nome,
                email=m.email,
                documento=m.documento,
                tenant_id=m.tenant_id,
                ativo=m.ativo
            )
            for m in models
        ]


class RepositorioFornecedorSQLAlchemy(FornecedorRepository):
    """
    Implementação concreta do repositório de Fornecedor usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, fornecedor: Fornecedor) -> Fornecedor:
        self.db.info["tenant_id"] = fornecedor.tenant_id
        model = self.db.query(FornecedorModel).filter(FornecedorModel.id == fornecedor.id).first()
        
        if not model:
            model = FornecedorModel(
                id=fornecedor.id,
                nome_fantasia=fornecedor.nome_fantasia,
                razao_social=fornecedor.razao_social,
                cnpj=fornecedor.cnpj,
                tenant_id=fornecedor.tenant_id,
                ativo=fornecedor.ativo
            )
            self.db.add(model)
        else:
            model.nome_fantasia = fornecedor.nome_fantasia
            model.razao_social = fornecedor.razao_social
            model.cnpj = fornecedor.cnpj
            model.ativo = fornecedor.ativo
            
        self.db.flush()
        
        return Fornecedor(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_id(self, id: UUID, tenant_id: UUID) -> Optional[Fornecedor]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(FornecedorModel).filter(FornecedorModel.id == id).first()
        if not model:
            return None
        return Fornecedor(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def obter_por_cnpj(self, cnpj: str, tenant_id: UUID) -> Optional[Fornecedor]:
        self.db.info["tenant_id"] = tenant_id
        cnpj_limpo = "".join(filter(str.isdigit, cnpj))
        model = self.db.query(FornecedorModel).filter(FornecedorModel.cnpj == cnpj_limpo).first()
        if not model:
            return None
        return Fornecedor(
            id=model.id,
            nome_fantasia=model.nome_fantasia,
            razao_social=model.razao_social,
            cnpj=model.cnpj,
            tenant_id=model.tenant_id,
            ativo=model.ativo
        )

    def listar_todos(self, tenant_id: UUID) -> List[Fornecedor]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(FornecedorModel).all()
        return [
            Fornecedor(
                id=m.id,
                nome_fantasia=m.nome_fantasia,
                razao_social=m.razao_social,
                cnpj=m.cnpj,
                tenant_id=m.tenant_id,
                ativo=m.ativo
            )
            for m in models
        ]


class RepositorioEstoqueSaldoSQLAlchemy(EstoqueSaldoRepository):
    """
    Implementação concreta do repositório de saldos de estoque usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, saldo: EstoqueSaldo) -> EstoqueSaldo:
        model = self.db.query(EstoqueSaldoModel).filter(EstoqueSaldoModel.id == saldo.id).first()
        if not model:
            model = self.db.query(EstoqueSaldoModel).filter(
                EstoqueSaldoModel.loja_id == saldo.loja_id,
                EstoqueSaldoModel.produto_id == saldo.produto_id
            ).first()

        if not model:
            model = EstoqueSaldoModel(
                id=saldo.id,
                loja_id=saldo.loja_id,
                produto_id=saldo.produto_id,
                quantidade=saldo.quantidade,
                tenant_id=saldo.tenant_id
            )
            self.db.add(model)
        else:
            model.quantidade = saldo.quantidade

        self.db.flush()
        return EstoqueSaldo(
            id=model.id,
            loja_id=model.loja_id,
            produto_id=model.produto_id,
            quantidade=model.quantidade,
            tenant_id=model.tenant_id
        )

    def obter_por_loja_e_produto(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> Optional[EstoqueSaldo]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(EstoqueSaldoModel).filter(
            EstoqueSaldoModel.loja_id == loja_id,
            EstoqueSaldoModel.produto_id == produto_id
        ).first()
        if not model:
            return None
        return EstoqueSaldo(
            id=model.id,
            loja_id=model.loja_id,
            produto_id=model.produto_id,
            quantidade=model.quantidade,
            tenant_id=model.tenant_id
        )

    def obter_por_loja_e_produto_com_lock(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> Optional[EstoqueSaldo]:
        self.db.info["tenant_id"] = tenant_id
        model = self.db.query(EstoqueSaldoModel).filter(
            EstoqueSaldoModel.loja_id == loja_id,
            EstoqueSaldoModel.produto_id == produto_id
        ).with_for_update().first()
        if not model:
            return None
        return EstoqueSaldo(
            id=model.id,
            loja_id=model.loja_id,
            produto_id=model.produto_id,
            quantidade=model.quantidade,
            tenant_id=model.tenant_id
        )

    def listar_todos(self, tenant_id: UUID) -> List[EstoqueSaldo]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(EstoqueSaldoModel).all()
        return [
            EstoqueSaldo(
                id=m.id,
                loja_id=m.loja_id,
                produto_id=m.produto_id,
                quantidade=m.quantidade,
                tenant_id=m.tenant_id
            )
            for m in models
        ]


class RepositorioEstoqueMovimentacaoSQLAlchemy(EstoqueMovimentacaoRepository):
    """
    Implementação concreta do repositório de histórico/ledger de movimentações usando SQLAlchemy.
    """
    def __init__(self, db: Session) -> None:
        self.db = db

    def salvar(self, movimentacao: EstoqueMovimentacao) -> EstoqueMovimentacao:
        model = EstoqueMovimentacaoModel(
            id=movimentacao.id,
            loja_id=movimentacao.loja_id,
            produto_id=movimentacao.produto_id,
            tipo=movimentacao.tipo,
            quantidade=movimentacao.quantidade,
            motivo=movimentacao.motivo,
            tenant_id=movimentacao.tenant_id,
            data_movimentacao=movimentacao.data_movimentacao
        )
        self.db.add(model)
        self.db.flush()
        return EstoqueMovimentacao(
            id=model.id,
            loja_id=model.loja_id,
            produto_id=model.produto_id,
            tipo=model.tipo,
            quantidade=model.quantidade,
            motivo=model.motivo,
            tenant_id=model.tenant_id,
            data_movimentacao=model.data_movimentacao
        )

    def listar_por_loja_e_produto(
        self, loja_id: UUID, produto_id: UUID, tenant_id: UUID
    ) -> List[EstoqueMovimentacao]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(EstoqueMovimentacaoModel).filter(
            EstoqueMovimentacaoModel.loja_id == loja_id,
            EstoqueMovimentacaoModel.produto_id == produto_id
        ).order_by(EstoqueMovimentacaoModel.data_movimentacao.asc()).all()
        return [
            EstoqueMovimentacao(
                id=m.id,
                loja_id=m.loja_id,
                produto_id=m.produto_id,
                tipo=m.tipo,
                quantidade=m.quantidade,
                motivo=m.motivo,
                tenant_id=m.tenant_id,
                data_movimentacao=m.data_movimentacao
            )
            for m in models
        ]

    def listar_todas(self, tenant_id: UUID) -> List[EstoqueMovimentacao]:
        self.db.info["tenant_id"] = tenant_id
        models = self.db.query(EstoqueMovimentacaoModel).order_by(EstoqueMovimentacaoModel.data_movimentacao.desc()).all()
        return [
            EstoqueMovimentacao(
                id=m.id,
                loja_id=m.loja_id,
                produto_id=m.produto_id,
                tipo=m.tipo,
                quantidade=m.quantidade,
                motivo=m.motivo,
                tenant_id=m.tenant_id,
                data_movimentacao=m.data_movimentacao
            )
            for m in models
        ]



