# Medições no Render (a sério)

Medido em **2026-11-13** no serviço real (`gerador-rifas`, plano gratuito, Frankfurt, versão **3.28.0** então em produção) com `scripts/medir_render.py` e as métricas do próprio Render. Substitui as estimativas antigas, feitas num contentor local com `--cpus=0.1`.

## Como repetir
```
uv run python scripts/medir_render.py --url https://gerador-rifas.onrender.com --tamanhos 500 2000 5000 10000 --saida medicoes.json
uv run python scripts/medir_render.py --url … --tamanhos 30000                       # o teto
uv run python scripts/medir_render.py --url … --tamanhos 10000 --modo varios          # ZIP com vários PDFs
uv run python scripts/medir_render.py --url … --template aleatorio_s1.pdf --algarismos aleatorio_s1_algarismos.pdf
```
Cria uma sessão por medição, gera, descarrega (só conta o tamanho) e apaga a sessão: nada fica no servidor. **Gera carga a sério** e o serviço só faz uma geração de cada vez para toda a gente: medir fora de horas. A CPU e a memória leem-se no painel (`/admin`) ou nas métricas do Render (`get_metrics`) na janela da medição.

## Resultados (template de exemplo com várias rifas por página, algarismos em PDF)

| Números | Modo | Gerar | Ritmo | Ficheiro |
|---:|---|---:|---:|---:|
| 500 | um PDF | 0,8 s | 600/s | 0,12 MB |
| 2 000 | um PDF | 4,2 s | 480/s | 0,23 MB |
| 5 000 | um PDF | 9,3 s | 540/s | 0,45 MB |
| 10 000 | um PDF | 18,4 s | 540/s | 0,83 MB |
| **30 000** (o teto) | um PDF | **57,7 s** | 520/s | 2,35 MB |
| 10 000 | vários PDFs (ZIP) | 20,2 s | 495/s | 3,42 MB |

Outros templates (5 000 números, um PDF): `aleatorio_s1.pdf` 9,6 s (520/s); `template_exemplo_1_rifa_a4.pdf` (uma rifa por folha, A4) 10,9 s (460/s). O ritmo é **linear** em todo o intervalo medido e parecido entre templates.

Pedidos pequenos (típicos): carregar o template 0,2–0,6 s, os algarismos 0,5–0,9 s (3,3 s na 1.ª vez com um PNG), «calcular» ≈ 0,1 s, pré-visualizar 0,09–0,2 s, descarregar 0,2–0,7 s. O serviço já estava acordado (o anti-sono chama `/health`): `acordar_s` ≈ 0,2 s; o *cold start* de um serviço adormecido não se mediu.

### Recursos (métricas do Render durante as medições)
- **CPU:** o limite é **0,15** (não 0,1) e o gerador **gasta-o todo** enquanto gera (máx. 0,15).
- **Memória:** 154 MiB em repouso; **máx. ≈ 187 MiB** de 512 MiB (limite) depois de gerar 30 000 números: sobra mais de metade.
- Disco efémero: o maior resultado (30 000 números) tem 2,35 MB.

## O que isto muda
- As estimativas antigas (5 000 ≈ 25 s, 20 000 ≈ 85 s, a 0,1 CPU) eram **2,5× pessimistas**: o ritmo real é ≈ **520 números/s**.
- Com `MAX_NUMEROS = 30 000` a geração mais longa dura **≈ 1 min**, dez vezes abaixo do `JOB_MAX_MIN` (10 min) e com memória de sobra: **o teto atual é seguro e conservador**.
- **Extrapolação (não medida acima de 30 000):** 60 000 ≈ 2 min; 100 000 ≈ 3,2 min. A memória cresceu pouco (≈ +33 MiB ao longo de toda a sessão de medições), mas ninguém a mediu a 100 000.
- **Recomendação:** não mexer no código. O custo de subir o teto não é a CPU nem a memória mas a **fila**: só corre uma geração de cada vez, por isso um pedido de 100 000 deixa os outros à espera ≈ 3 min. Se quiseres mais volume para já, define `MAX_NUMEROS=60000` no Render (Environment), repete o script com `--tamanhos 60000` e vê as métricas; acima disso faz mais sentido como oferta paga («mais volume por pedido», `docs/PLANO_PRODUTO.md`).
- O **limite de pedidos por IP** e o `API_MAX_NUMEROS_LOTE` (3 × `MAX_NUMEROS`) continuam a proteger contra abuso; com ≈ 520 números/s, um lote da API de 90 000 números ocupa o serviço ≈ 3 min.
