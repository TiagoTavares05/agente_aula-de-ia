import json
import csv
import os
from pydantic import BaseModel, Field
from google.adk.agents.llm_agent import Agent
from .instruction import instruction

# 1. Classe atualizada com os campos exatos da sua planilha (agora extrai email e telefone!)
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

# 2. Função corrigida para usar ponto e vírgula e bater exatamente com suas colunas
def gerar_json_e_salvar_planilha(
    nome: str, email: str, telefone: str, cidade: str, linkedin: str, portfolio: str,
    area: str, curso_superior: str, ingles: str, justificativa_ia: str, match_ia: str
) -> dict:
    """
    Recebe os dados extraídos, monta o JSON e insere na base existente usando ponto e vírgula.
    """
    candidato = Candidato(
        nome=nome, email=email, telefone=telefone, cidade=cidade, linkedin=linkedin, 
        portfolio=portfolio, area=area, curso_superior=curso_superior, ingles=ingles, 
        justificativa_ia=justificativa_ia, match_ia=match_ia
    )
    
    resultado_json = candidato.model_dump()
    
    # Adiciona o campo 'status' que tem na sua planilha, mas que a IA não precisa preencher
    resultado_json['status'] = 'Analisado'
    
    nome_arquivo = 'base_agente.xlsx - Planilha1.csv'
    
    # Ordem EXATA das colunas como aparecem na sua imagem
    colunas_planilha = [
        'nome', 'email', 'telefone', 'cidade', 'linkedin', 'portfolio', 
        'area', 'curso_superior', 'ingles', 'justificativa_ia', 'match_ia', 'status'
    ]
    
    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as arquivo_csv:
        # O segredo está aqui: delimiter=';'
        writer = csv.DictWriter(arquivo_csv, fieldnames=colunas_planilha, delimiter=';')
        writer.writerow(resultado_json)
    
    print(f"\n[ARTEFATO GERADO] Candidato inserido na planilha '{nome_arquivo}':")
    print(json.dumps(resultado_json, indent=2, ensure_ascii=False))
    
    return {
        "status": "sucesso",
        "mensagem": f"Candidato processado e inserido na planilha com sucesso.",
        "dados_candidato": resultado_json
    }

# 3. Configuração do Agente Principal
root_agent = Agent(
    model='gemini-2.5-flash',
    name='analisador_curriculos',
    description="Agente especializado em ler currículos, extrair dados e salvá-los em uma planilha CSV.",
    instruction=instruction,
    tools=[gerar_json_e_salvar_planilha],
)