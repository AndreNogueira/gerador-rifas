"""python -m core <pasta_de_exemplos> <pasta_de_saida>  ->  auto-teste sem janela (ver core.autoteste.main)."""
import sys

from .autoteste import main

sys.exit(main())
