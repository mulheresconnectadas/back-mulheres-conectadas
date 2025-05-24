from enum import Enum

class GeneroEnum(str, Enum):
    mulher_cisgenero = "Mulher cisgenera"
    homem_cisgenero = "Homem cisgenero"
    mulher_transexual = "Mulher transexual/transgenera"
    homem_transexual = "Homem transexual/transgenero"
    travesti = "Travesti"
    nao_binario = "Nao binario"
    prefiro_nao_responder = "Prefiro nao responder"
    outro = "Outro"

class EtniaEnum(str, Enum):
    branca = "branca"
    preta = "preta"
    parda = "parda"
    amarela = "amarela"
    indigena = "indigena"
    outro = "outro"

class EscolaridadeEnum(str, Enum):
    fundamental_incompleto = "fundamental incompleto"
    fundamental_completo = "fundamental completo"
    medio_incompleto = "medio incompleto"
    medio_completo = "medio completo"
    superior_incompleto = "superior incompleto"
    superior_completo = "superior completo"
    outro = "outro"

class SituacaoTrabalhoEnum(str, Enum):
    empregado = "empregado"
    desempregado = "desempregado"
    estudante = "estudante"
    autônomo = "autonomo"
    em_transicao_de_carreira = "em transicao de carreira"
    outro = "outro"

class PresencialEnum(str, Enum):
    sim = "sim"
    nao = "nao"
    talvez = "talvez"

class FonteProgramaEnum(str, Enum):
    instagram = "instagram"
    linkedin = "linkedin"
    whatsapp = "whatsapp"
    tv = "tv"
    outros = "outros"

class TipoPublicacao(str, Enum):
    blog = "blog"
    noticia = "noticia"