"""O que os guias partilham: a frase final («o serviço é gratuito, sem registo…»), igual em todos, tirada do guia das escolas (uma só fonte, as 22 línguas)."""
from . import escolas, novas

FIM = {lg: d["fim"] for lg, d in {**escolas.DADOS, **novas.ESCOLAS}.items()}
