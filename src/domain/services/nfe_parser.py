import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass(frozen=True)
class ItemNFe:
    codigo_produto: str
    codigo_barras: Optional[str]
    nome: str
    quantidade: float
    valor_unitario: float


@dataclass(frozen=True)
class EmitenteNFe:
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None


@dataclass(frozen=True)
class NFeDados:
    emitente: EmitenteNFe
    itens: List[ItemNFe]


class NFeParserService:
    """
    Serviço utilitário para parsing de XML de Nota Fiscal Eletrônica (NF-e v4.00).
    """

    @staticmethod
    def parse_xml(xml_content: bytes | str) -> NFeDados:
        # Segurança contra XML Bomb / Billion Laughs e XXE
        # NF-e legítimas nunca contêm declarações DOCTYPE ou ENTITY
        xml_str = xml_content if isinstance(xml_content, str) else xml_content.decode("utf-8", errors="ignore")
        if "<!doctype" in xml_str.lower() or "<!entity" in xml_str.lower():
            raise ValueError("XML inválido por motivos de segurança: declarações DOCTYPE ou ENTITY não são permitidas.")

        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ValueError(f"XML inválido ou corrompido: {str(e)}")

        # Trata namespaces do XML da NF-e
        # O namespace padrão costuma ser http://www.portalfiscal.inf.br/nfe
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        # Encontra a tag infNFe
        inf_nfe = root.find(f".//{ns}infNFe")
        if inf_nfe is None:
            # Tenta encontrar sem namespace
            inf_nfe = root.find(".//infNFe")
            if inf_nfe is None:
                raise ValueError("Estrutura de NF-e inválida: tag <infNFe> não encontrada.")

        # Parsing do Emitente (Fornecedor)
        emit = inf_nfe.find(f"{ns}emit") if inf_nfe.find(f"{ns}emit") is not None else inf_nfe.find("emit")
        if emit is None:
            raise ValueError("Estrutura de NF-e inválida: tag <emit> do emitente não encontrada.")

        cnpj_elem = emit.find(f"{ns}CNPJ") if emit.find(f"{ns}CNPJ") is not None else emit.find("CNPJ")
        cnpj_val = cnpj_elem.text.strip() if cnpj_elem is not None and cnpj_elem.text else ""
        cnpj_limpo = re.sub(r"\D", "", cnpj_val)

        if not cnpj_limpo or len(cnpj_limpo) != 14:
            raise ValueError("CNPJ do emitente da NF-e inválido ou ausente.")

        razao_elem = emit.find(f"{ns}xNome") if emit.find(f"{ns}xNome") is not None else emit.find("xNome")
        razao_social = razao_elem.text.strip() if razao_elem is not None and razao_elem.text else "Fornecedor NF-e"

        fantasia_elem = emit.find(f"{ns}xFant") if emit.find(f"{ns}xFant") is not None else emit.find("xFant")
        nome_fantasia = fantasia_elem.text.strip() if fantasia_elem is not None and fantasia_elem.text else razao_social

        emitente = EmitenteNFe(
            cnpj=cnpj_limpo,
            razao_social=razao_social,
            nome_fantasia=nome_fantasia
        )

        # Parsing dos Itens (<det>)
        det_list = inf_nfe.findall(f"{ns}det") if len(inf_nfe.findall(f"{ns}det")) > 0 else inf_nfe.findall("det")
        if not det_list:
            raise ValueError("Nenhum item/produto foi encontrado na NF-e.")

        itens: List[ItemNFe] = []
        for idx, det in enumerate(det_list, start=1):
            prod = det.find(f"{ns}prod") if det.find(f"{ns}prod") is not None else det.find("prod")
            if prod is None:
                continue

            c_prod_elem = prod.find(f"{ns}cProd") if prod.find(f"{ns}cProd") is not None else prod.find("cProd")
            codigo_prod = c_prod_elem.text.strip() if c_prod_elem is not None and c_prod_elem.text else f"ITEM-{idx}"

            c_ean_elem = prod.find(f"{ns}cEAN") if prod.find(f"{ns}cEAN") is not None else prod.find("cEAN")
            codigo_barras = None
            if c_ean_elem is not None and c_ean_elem.text and c_ean_elem.text.strip().upper() != "SEM GTIN":
                codigo_barras = c_ean_elem.text.strip()

            x_prod_elem = prod.find(f"{ns}xProd") if prod.find(f"{ns}xProd") is not None else prod.find("xProd")
            nome_prod = x_prod_elem.text.strip() if x_prod_elem is not None and x_prod_elem.text else f"Produto {codigo_prod}"

            q_com_elem = prod.find(f"{ns}qCom") if prod.find(f"{ns}qCom") is not None else prod.find("qCom")
            try:
                quantidade = float(q_com_elem.text.strip()) if q_com_elem is not None and q_com_elem.text else 0.0
            except ValueError:
                quantidade = 0.0

            v_un_elem = prod.find(f"{ns}vUnCom") if prod.find(f"{ns}vUnCom") is not None else prod.find("vUnCom")
            try:
                valor_unitario = float(v_un_elem.text.strip()) if v_un_elem is not None and v_un_elem.text else 0.0
            except ValueError:
                valor_unitario = 0.0

            if quantidade <= 0 or valor_unitario < 0:
                continue

            itens.append(ItemNFe(
                codigo_produto=codigo_prod,
                codigo_barras=codigo_barras,
                nome=nome_prod,
                quantidade=quantidade,
                valor_unitario=valor_unitario
            ))

        if not itens:
            raise ValueError("A NF-e não possui itens válidos com quantidade positiva.")

        return NFeDados(emitente=emitente, itens=itens)
