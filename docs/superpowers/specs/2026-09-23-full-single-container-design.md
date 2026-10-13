# Imagem Completa em Container Único

## Objetivo

Entregar uma imagem Docker que contenha a API Flask, o processo de retreinamento automático, os datasets e todas as dependências de machine learning. O MySQL permanece externo e é acessado por variáveis de ambiente.

## Decisões

- Usar Python 3.10, alinhado ao ambiente validado do projeto.
- Usar uma única imagem e um único container para API e treinamento.
- Usar Supervisor para manter os dois processos ativos:
  - Gunicorn para `API.app:app` na porta 3000.
  - Worker de retreinamento para o processo de atualização do grafo.
- Manter o MySQL fora do container.
- Persistir `/app/download` e `/app/Server/MLModels/saved_models` por volumes Docker.
- Configurar banco por `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` e `DB_NAME`.
- Executar os processos com usuário não-root.

## Fluxo de execução

```text
Container
├── Gunicorn → API Flask :3000
└── Worker → consulta atualização → treina modelos → atualiza banco
                                      └→ publica XML/JSON/modelos

MySQL externo ← conexão por DB_*
Volumes       ← download/ e saved_models/
```

O worker aguardará a API estar disponível, consultará o estado de atualização com timeout e executará um único pipeline compartilhado com o treinamento manual. O pipeline será responsável por pré-processar os datasets, treinar ANN, Decision Tree, Random Forest e SVM, atualizar o grafo e gerar XML/JSON.

## Correções de aplicação necessárias

- Extrair o fluxo de `Server/MainFunctions.py` para uma função chamável, evitando treinamento durante importação.
- Fazer `API/ServerProcessApi.py` chamar esse pipeline em vez dos imports legados inexistentes.
- Corrigir os caminhos Windows para `pathlib.Path`, incluindo datasets, XML, JSON e modelos.
- Usar `DB_NAME` na conexão em vez de manter o banco fixo no código.
- Corrigir as dimensões de entrada ONNX para 9 características (ACC) e 18 (ACC + GYR).
- Verificar retorno dos conversores ONNX/ORT e usar o mesmo interpretador Python do container.
- Publicar artefatos apenas depois que treinamento, banco e exportações terminarem com sucesso.
- Manter o estado de atualização até o término do pipeline e registrar falhas para nova tentativa.

## Docker

- Copiar `Requirements.txt` antes de instalar dependências.
- Instalar dependências completas de treinamento.
- Copiar explicitamente `API`, `Server` e `download`.
- Excluir `.env`, `.git`, `venv`, caches e testes do contexto com `.dockerignore`.
- Adicionar healthcheck para `/`.
- Usar `supervisord` como processo principal do container.

## Verificação

1. Construir a imagem sem erros.
2. Iniciar o container apontando `DB_HOST` para o MySQL externo.
3. Confirmar healthcheck e `/`.
4. Confirmar downloads do grafo e dos modelos.
5. Confirmar otimização `acc_gyr` e `acc/50`.
6. Disparar uma atualização e observar o worker até gerar novos artefatos.
7. Validar que os arquivos gerados são XML/JSON válidos e que os modelos esperados existem.

## Fora do escopo

- Colocar MySQL dentro da imagem.
- Resolver os conflitos Git preexistentes em modelos, XMLs e bytecodes.
- Transformar o sistema em múltiplos containers nesta etapa.
