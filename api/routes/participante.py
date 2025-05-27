from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy import func
from io import StringIO
import pandas as pd
import codecs
from sqlalchemy import select

from api import model, schema
from api.database import get_db
from api.model import Participante
from api.email_utils import send_email
from api.enums import (
    GeneroEnum,
    EtniaEnum,
    EscolaridadeEnum,
    SituacaoTrabalhoEnum,
    PresencialEnum,
    FonteProgramaEnum,
    TipoPublicacao,
)

from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter()

ADMIN_USERS = {
    "gesyca@admin.com": {"senha": "senhaGesyca123", "nome": "Gesyca"},
    "alessandra@admin.com": {"senha": "senhaAlessandra123", "nome": "Alessandra"},
}

def to_csv_response(data, columns, filename):
    import pandas as pd

    df = pd.DataFrame(data, columns=columns)
    stream = StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)

    # Adiciona BOM para suportar acentos no Excel
    bom = codecs.BOM_UTF8.decode('utf-8')
    csv_content = bom + stream.read()
    stream = StringIO(csv_content)

    return StreamingResponse(stream, media_type="text/csv", headers={
        "Content-Disposition": f"attachment; filename={filename}"
    })

class AdminLoginRequest(BaseModel):
    email: EmailStr
    senha: str

class EmailRequest(BaseModel):
    email: EmailStr

# Função auxiliar para transformar enums em listas de dicionários
def enum_to_dict(enum_cls):
    return [{"value": e.name, "label": e.value} for e in enum_cls]

@router.get("/inscricao_form", status_code=status.HTTP_200_OK)
def inscricao_form():
    return {
        "genero": enum_to_dict(GeneroEnum),
        "etnia": enum_to_dict(EtniaEnum),
        "escolaridade": enum_to_dict(EscolaridadeEnum),
        "situacao_trabalho": enum_to_dict(SituacaoTrabalhoEnum),
        "deseja_participar_presencial": enum_to_dict(PresencialEnum),
        "como_soube_programa": enum_to_dict(FonteProgramaEnum),
        "tipo_publicacao": enum_to_dict(TipoPublicacao),
    }

@router.post("/addUser", status_code=status.HTTP_201_CREATED)
def criar_participante(participante: schema.ParticipanteCreate, db: Session = Depends(get_db)):
    try:
        db_participante = model.Participante(**participante.dict())
        db.add(db_participante)
        db.commit()
        db.refresh(db_participante)

        subject = "Inscrição realizada com sucesso"
        body = f"""
        <html>
        <body>
            <p>Olá {db_participante.nome},</p>

            <p>Caso tenha dúvidas, você pode responder este e-mail.</p>

            <p>Atenciosamente,<br>
            Equipe Mulheres Conectadas</p>
        </body>
        </html>
        """
        send_email(db_participante.email, subject, db_participante.nome)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Participante criado com sucesso.",
                "data": jsonable_encoder(db_participante)
            }
        )
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao salvar participante: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro inesperado: {str(e)}"
        )

@router.get("/users", response_model=list[schema.ParticipanteResponse], status_code=status.HTTP_200_OK)
def listar_participantes(db: Session = Depends(get_db)):
    return db.query(model.Participante).all()

@router.post("/validar_email")
async def validar_email(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    try:
        data = EmailRequest(**body)
    except ValidationError:
        return {"valid": False, "message": "Formato de e-mail inválido"}

    email_existe = db.query(Participante).filter_by(email=data.email).first()
    if email_existe:
        return {"valid": False, "message": "E-mail já cadastrado"}

    return {"valid": True}


@router.post("/admin/login")
def login_admin(admin: AdminLoginRequest):
    user = ADMIN_USERS.get(admin.email)
    if user and admin.senha == user["senha"]:
        return {"nome": user["nome"]}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas"
    )

@router.get("/inscricoes/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # 1. Inscrições por cidade - Pizza
    por_cidade = (
        db.query(Participante.cidade, func.count().label("total"))
        .group_by(Participante.cidade)
        .all()
    )

    # 2. Escolaridade dos inscritos - Bar chart
    por_escolaridade = (
        db.query(Participante.escolaridade, func.count().label("total"))
        .group_by(Participante.escolaridade)
        .all()
    )

    # 3. Situação de trabalho atual - Horizontal bar chart
    por_situacao_trabalho = (
        db.query(Participante.situacao_trabalho, func.count().label("total"))
        .group_by(Participante.situacao_trabalho)
        .all()
    )

    # Dicionários para normalização
    escolaridade_map = {
        "fundamental completo": "Fundamental Completo",
        "fundamental incompleto": "Fundamental Incompleto",
        "medio completo": "Médio Completo",
        "medio incompleto": "Médio Incompleto",
        "superior completo": "Superior Completo",
        "superior incompleto": "Superior Incompleto",
        "outro": "Outro"
    }

    situacao_trabalho_map = {
        "empregado": "Empregado",
        "desempregado": "Desempregado",
        "estudante": "Estudante",
        "autonomo": "Autônomo",
        "outro": "Outro"
    }

    return {
        "por_cidade": {
            "labels": [c for c, _ in por_cidade],
            "data": [t for _, t in por_cidade]
        },
        "por_escolaridade": {
            "labels": [
                escolaridade_map.get(e.lower(), e) for e, _ in por_escolaridade
            ],
            "data": [t for _, t in por_escolaridade]
        },
        "por_situacao_trabalho": {
            "labels": [
                situacao_trabalho_map.get(s.lower(), s) for s, _ in por_situacao_trabalho
            ],
            "data": [t for _, t in por_situacao_trabalho]
        }
    }
 


@router.get("/escolaridade_por_etnia")  # Group bar chart
def escolaridade_por_etnia(db: Session = Depends(get_db)):
    resultados = (
        db.query(model.Participante.etnia, model.Participante.escolaridade, func.count())
        .group_by(model.Participante.etnia, model.Participante.escolaridade)
        .all()
    )

    # Normalizações para exibição
    etnia_map = {
        "branca": "Branca",
        "parda": "Parda",
        "preta": "Preta",
        "indigena": "Indígena",
        "amarela": "Amarela",
        "outra": "Outra"
    }

    escolaridade_map = {
        "fundamental completo": "Fundamental Completo",
        "fundamental incompleto": "Fundamental Incompleto",
        "medio completo": "Médio Completo",
        "medio incompleto": "Médio Incompleto",
        "superior completo": "Superior Completo",
        "superior incompleto": "Superior Incompleto",
        "outro": "Outro"
    }

    # Preparar listas únicas com normalização
    etnias_raw = {r[0] for r in resultados}
    escolaridades_raw = {r[1] for r in resultados}

    etnias = sorted([etnia_map.get(e.lower(), e) for e in etnias_raw])
    escolaridades = sorted([escolaridade_map.get(es.lower(), es) for es in escolaridades_raw])

    # Inicializar estrutura de dados
    data_map = {e: {es: 0 for es in escolaridades} for e in etnias}

    # Preencher contagens com normalização
    for etnia_raw, escolaridade_raw, count in resultados:
        etnia = etnia_map.get(etnia_raw.lower(), etnia_raw)
        escolaridade = escolaridade_map.get(escolaridade_raw.lower(), escolaridade_raw)
        data_map[etnia][escolaridade] = count

    # Formatar em datasets
    datasets = []
    for escolaridade in escolaridades:
        datasets.append({
            "label": escolaridade,
            "data": [data_map[etnia][escolaridade] for etnia in etnias]
        })

    return {
        "labels": etnias,
        "datasets": datasets
    }



from api.enums import PresencialEnum

@router.get("/presencial_top_cidades") 
def presencial_top_cidades(db: Session = Depends(get_db)):
    # 1. Top 3 cidades com mais inscritos
    subquery = (
        db.query(model.Participante.cidade)
        .group_by(model.Participante.cidade)
        .order_by(func.count().desc())
        .limit(3)
        .subquery()
    )

    # 2. Consulta: cidade x deseja_participar_presencial
    resultados = (
        db.query(
            model.Participante.cidade,
            model.Participante.deseja_participar_presencial,
            func.count()
        )
        .filter(model.Participante.cidade.in_(subquery))
        .group_by(
            model.Participante.cidade,
            model.Participante.deseja_participar_presencial
        )
        .all()
    )

    cidades = sorted(list({r[0] for r in resultados}))

    # Labels padronizadas
    opcoes_labels = ['Sim', 'Não', 'Talvez']

    # Mapeia os valores do banco para labels padronizadas
    normalizacao = {
        'sim': 'Sim',
        'nao': 'Não',
        'não': 'Não',  # extra, por garantia
        'talvez': 'Talvez'
    }

    # Inicializa estrutura
    data_map = {
        cidade: {label: 0 for label in opcoes_labels}
        for cidade in cidades
    }

    for cidade, deseja_presencial, count in resultados:
        resposta_normalizada = normalizacao.get(deseja_presencial.lower(), deseja_presencial)
        if resposta_normalizada in opcoes_labels:
            data_map[cidade][resposta_normalizada] = count

    # Gera datasets para o gráfico
    datasets = []
    for label in opcoes_labels:
        datasets.append({
            "label": label,
            "data": [data_map[cidade][label] for cidade in cidades]
        })

    return {
        "labels": cidades,
        "datasets": datasets
    }

@router.get("/exportar_inscricoes")
def exportar_inscricoes(db: Session = Depends(get_db)):
    # Buscar todos os participantes
    participantes = db.query(model.Participante).all()

    # Nome das colunas baseado nos atributos do modelo
    colunas = [column.name for column in model.Participante.__table__.columns]

    # Criar buffer e writer com BOM
    output = io.StringIO()
    writer = csv.writer(output)

    # Escrever cabeçalho
    writer.writerow(colunas)

    # Escrever linhas com os dados
    for p in participantes:
        linha = [getattr(p, col) for col in colunas]
        writer.writerow(linha)

    # Adicionar BOM manualmente
    output.seek(0)
    bom = codecs.BOM_UTF8.decode("utf-8")
    csv_com_bom = bom + output.read()

    # Novo stream com conteúdo final
    final_stream = io.StringIO(csv_com_bom)

    return StreamingResponse(
        final_stream,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inscricoes.csv"}
    )


@router.get("/inscricoes/stats/cidade/csv")
def get_csv_por_cidade(db: Session = Depends(get_db)):
    data = (
        db.query(Participante.cidade, func.count().label("total"))
        .group_by(Participante.cidade)
        .all()
    )
    return to_csv_response(data, ["Cidade", "Total"], "inscricoes_por_cidade.csv")


@router.get("/inscricoes/stats/escolaridade/csv")
def get_csv_por_escolaridade(db: Session = Depends(get_db)):
    data = (
        db.query(Participante.escolaridade, func.count().label("total"))
        .group_by(Participante.escolaridade)
        .all()
    )
    escolaridade_map = {
        "fundamental completo": "Fundamental Completo",
        "fundamental incompleto": "Fundamental Incompleto",
        "medio completo": "Médio Completo",
        "medio incompleto": "Médio Incompleto",
        "superior completo": "Superior Completo",
        "superior incompleto": "Superior Incompleto",
        "outro": "Outro"
    }
    data = [(escolaridade_map.get(e.lower(), e), t) for e, t in data]
    return to_csv_response(data, ["Escolaridade", "Total"], "inscricoes_por_escolaridade.csv")


@router.get("/inscricoes/stats/situacao_trabalho/csv")
def get_csv_por_situacao_trabalho(db: Session = Depends(get_db)):
    data = (
        db.query(Participante.situacao_trabalho, func.count().label("total"))
        .group_by(Participante.situacao_trabalho)
        .all()
    )
    situacao_trabalho_map = {
        "empregado": "Empregado",
        "desempregado": "Desempregado",
        "estudante": "Estudante",
        "autonomo": "Autônomo",
        "outro": "Outro"
    }
    data = [(situacao_trabalho_map.get(s.lower(), s), t) for s, t in data]
    return to_csv_response(data, ["Situação de Trabalho", "Total"], "inscricoes_por_situacao_trabalho.csv")



@router.get("/escolaridade_por_etnia/csv")
def csv_escolaridade_por_etnia(db: Session = Depends(get_db)):
    resultados = (
        db.query(model.Participante.etnia, model.Participante.escolaridade, func.count())
        .group_by(model.Participante.etnia, model.Participante.escolaridade)
        .all()
    )

    # Mapas de normalização
    etnia_map = {
        "branca": "Branca",
        "parda": "Parda",
        "preta": "Preta",
        "indigena": "Indígena",
        "amarela": "Amarela",
        "outra": "Outra"
    }

    escolaridade_map = {
        "fundamental completo": "Fundamental Completo",
        "fundamental incompleto": "Fundamental Incompleto",
        "medio completo": "Médio Completo",
        "medio incompleto": "Médio Incompleto",
        "superior completo": "Superior Completo",
        "superior incompleto": "Superior Incompleto",
        "outro": "Outro"
    }

    # Preparar listas únicas com normalização
    etnias_raw = {r[0] for r in resultados}
    escolaridades_raw = {r[1] for r in resultados}

    etnias = sorted([etnia_map.get(e.lower(), e) for e in etnias_raw])
    escolaridades = sorted([escolaridade_map.get(es.lower(), es) for es in escolaridades_raw])

    # Inicializar estrutura de dados
    data_map = {e: {es: 0 for es in escolaridades} for e in etnias}

    # Preencher contagens
    for etnia_raw, escolaridade_raw, count in resultados:
        etnia = etnia_map.get(etnia_raw.lower(), etnia_raw)
        escolaridade = escolaridade_map.get(escolaridade_raw.lower(), escolaridade_raw)
        data_map[etnia][escolaridade] = count

    # Montar DataFrame
    rows = []
    for etnia in etnias:
        row = {"Etnia": etnia}
        row.update(data_map[etnia])
        rows.append(row)

    df = pd.DataFrame(rows)
    return to_csv_response(df.values.tolist(), df.columns.tolist(), "escolaridade_por_etnia.csv")

@router.get("/presencial_top_cidades/csv")
def csv_presencial_top_cidades(db: Session = Depends(get_db)):
    # Top 3 cidades com mais inscritos
    subquery = (
    db.query(model.Participante.cidade)
    .group_by(model.Participante.cidade)
    .order_by(func.count().desc())
    .limit(3)
    .subquery()
    )

    resultados = (
    db.query(
        model.Participante.cidade,
        model.Participante.deseja_participar_presencial,
        func.count()
    )
    .filter(model.Participante.cidade.in_(select(subquery.c.cidade)))  # <- CORRIGIDO
    .group_by(
        model.Participante.cidade,
        model.Participante.deseja_participar_presencial
    )
    .all()
)

    cidades = sorted(list({r[0] for r in resultados}))

    opcoes_labels = ['Sim', 'Não', 'Talvez']
    normalizacao = {
        'sim': 'Sim',
        'nao': 'Não',
        'não': 'Não',
        'talvez': 'Talvez'
    }

    # Inicializar dados
    data_map = {
        cidade: {label: 0 for label in opcoes_labels}
        for cidade in cidades
    }

    for cidade, deseja_presencial, count in resultados:
        resposta_normalizada = normalizacao.get(deseja_presencial.lower(), deseja_presencial)
        if resposta_normalizada in opcoes_labels:
            data_map[cidade][resposta_normalizada] = count

    # Montar DataFrame
    rows = []
    for cidade in cidades:
        row = {"Cidade": cidade}
        row.update(data_map[cidade])
        rows.append(row)

    df = pd.DataFrame(rows)
    return to_csv_response(df.values.tolist(), df.columns.tolist(), "presencial_top_cidades.csv")

