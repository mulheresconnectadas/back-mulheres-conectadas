from sqlalchemy import Column, Integer, String, Date, Text, DateTime, Enum
from api.database import Base
from datetime import datetime

from api.enums import (
    GeneroEnum,
    EtniaEnum,
    EscolaridadeEnum,
    SituacaoTrabalhoEnum,
    PresencialEnum,
    FonteProgramaEnum,
    TipoPublicacao,
)

class Participante(Base):
    __tablename__ = "participantes"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    genero = Column(Enum(GeneroEnum), nullable=False)
    etnia = Column(Enum(EtniaEnum), nullable=False)
    escolaridade = Column(Enum(EscolaridadeEnum), nullable=False)
    contato = Column(String(50), nullable=False)

    situacao_trabalho = Column(Enum(SituacaoTrabalhoEnum), nullable=False)

    rede_social = Column(String(255), nullable=True)

    cidade = Column(String(255), nullable=False)

    deseja_participar_presencial = Column(Enum(PresencialEnum), nullable=False)
    como_soube_programa = Column(Enum(FonteProgramaEnum), nullable=False)

    autorizacao_lgpd = Column(Text, nullable=False)  # sim ou justificativa

    


class Publicacao(Base):
    __tablename__ = "publicacoes"

    id = Column(Integer, primary_key=True, index=True)
    legenda = Column(String, nullable=False)
    imagem_url = Column(String, nullable=False)
    tipo = Column(Enum(TipoPublicacao), nullable=False)
    data_publicacao = Column(DateTime, default=datetime.utcnow)
