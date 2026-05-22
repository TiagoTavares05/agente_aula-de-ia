import json
import os
import openpyxl
from pydantic import BaseModel, Field
from google.adk.agents.llm_agent import Agent
from .instruction import instruction

# 1. Classe com os campos exatos (sem alterações aqui)
class Candidato(BaseModel):
    nome: str = Field(description="Nome completo do candidato.")
    email: str = Field(description="Endereço de e-mail do candidato. Se não houver, deixe em branco.")
    telefone: str = Field(description="Número de telefone ou celular. Se não houver, deixe em branco.")
    cidade: str = Field(description="Cidade e/ou estado onde o candidato reside. Se não houver, deixe em branco.")
    linkedin: str = Field(description="URL do perfil do LinkedIn. Se não houver, deixe em branco.")
    portfolio: str = Field(description="URL do portfólio, GitHub, etc. Se não houver, deixe em branco.")
    area: str = Field(description="Área de atuação principal ou cargo pretendido.")
    curso_superior: str = Field(description="Nome do curso superior e instituição.")
    ingles: str = Field(description="Nível de proficiência em inglês identificado.")
    justificativa_ia: str = Field(description="Análise justificando se é um bom match para a área.")
    match_ia: str = Field(description="Porcentagem estimada de aderência (ex: 85%) ou nível (Alto, Médio, Baixo).")

# 2. Função atualizada para interagir com o Excel (.xlsx)
def gerar_json_e_salvar_planilha(
    nome: str, email: str, telefone: str, cidade: str, linkedin: str, portfolio: str,
    area: str, curso_superior: str, ingles: str, justificativa_ia: str, match_ia: str
) -> dict:
    """
    Recebe os dados extraídos, monta o JSON e insere em um arquivo nativo do Excel (.xlsx).
    """
    candidato = Candidato(
        nome=nome, email=email, telefone=telefone, cidade=cidade, linkedin=linkedin, 
        portfolio=portfolio, area=area, curso_superior=curso_superior, ingles=ingles, 
        justificativa_ia=justificativa_ia, match_ia=match_ia
    )
    
    resultado_json = candidato.model_dump()
    resultado_json['status'] = 'Analisado'
    
    # Nome exato da sua planilha Excel
    nome_arquivo = 'base_agente.xlsx'
    
    colunas_planilha = [
        'nome', 'email', 'telefone', 'cidade', 'linkedin', 'portfolio', 
        'area', 'curso_superior', 'ingles', 'justificativa_ia', 'match_ia', 'status'
    ]
    
    # Lógica para abrir o Excel existente ou criar um novo se não achar
    if os.path.exists(nome_arquivo):
        workbook = openpyxl.load_workbook(nome_arquivo)
        sheet = workbook.active
    else:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # Se for um arquivo novo, insere o cabeçalho
        sheet.append(colunas_planilha)
    
    # Cria uma lista com os valores do candidato na ordem exata das colunas
    linha_excel = [resultado_json.get(coluna, "") for coluna in colunas_planilha]
    
    # Adiciona a linha na planilha e salva
    sheet.append(linha_excel)
    workbook.save(nome_arquivo)
    
    print(f"\n[ARTEFATO GERADO] Candidato inserido na planilha Excel '{nome_arquivo}':")
    print(json.dumps(resultado_json, indent=2, ensure_ascii=False))
    
    return {
        "status": "sucesso",
        "mensagem": f"Candidato processado e inserido na planilha Excel com sucesso.",
        "dados_candidato": resultado_json
    }

# 3. Configuração do Agente Principal
root_agent = Agent(
    model='gemini-2.5-flash',
    name='analisador_curriculos',
    description="Agente especializado em ler currículos, extrair dados e salvá-los no Excel.",
    instruction=instruction,
    tools=[gerar_json_e_salvar_planilha],
)