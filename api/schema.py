from datetime import date, datetime
from pydantic import BaseModel, EmailStr, AnyUrl, HttpUrl, field_validator 
from typing import Optional

from api.enums import (
    GeneroEnum,
    EtniaEnum,
    EscolaridadeEnum,
    SituacaoTrabalhoEnum,
    PresencialEnum,
    FonteProgramaEnum,
    TipoPublicacao,
)

class ParticipanteBase(BaseModel):
    nome: str
    email: EmailStr
    data_nascimento: date
    genero: GeneroEnum
    etnia: EtniaEnum
    escolaridade: EscolaridadeEnum
    contato: str
    situacao_trabalho: SituacaoTrabalhoEnum
    rede_social: str
    cidade: str
    deseja_participar_presencial: PresencialEnum
    como_soube_programa: FonteProgramaEnum
    autorizacao_lgpd: str

    # Validadores

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode estar vazio")
        return v

    @field_validator("contato")
    @classmethod
    def contato_valido(cls, v):
        if not v.strip():
            raise ValueError("Contato é obrigatório")
        if len(v) < 8:
            raise ValueError("Contato parece estar incompleto")
        return v

    @field_validator("cidade")
    @classmethod
    def cidade_valida(cls, v):
        if not v.strip():
            raise ValueError("Cidade não pode estar vazia")
        return v

    @field_validator("autorizacao_lgpd")
    @classmethod
    def lgpd_obrigatoria(cls, v):
        if not v.strip():
            raise ValueError("É necessário aceitar a LGPD ou justificar")
        return v

    @field_validator("data_nascimento")
    @classmethod
    def nascimento_passado(cls, v):
        if v >= date.today():
            raise ValueError("Data de nascimento deve estar no passado")
        return v

class ParticipanteCreate(ParticipanteBase):
    pass

class ParticipanteResponse(ParticipanteBase):
    id: int

    class Config:
        from_attributes = True

class PublicacaoCreate(BaseModel):
    legenda: str
    imagem_url: HttpUrl  # ou str, caso aceite qualquer texto
    tipo: TipoPublicacao

class PublicacaoResponse(PublicacaoCreate):
    id: int
    data_publicacao: datetime

    class Config:
        from_attributes = True