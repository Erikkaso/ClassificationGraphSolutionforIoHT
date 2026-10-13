# Classification Graph Solution for IoHT

Servidor de grafos de classificacao para aplicacoes de Internet of Health
Things, baseado na pesquisa de Evilasio Junior. O projeto contem a API Flask,
a persistencia MySQL, os pipelines de treinamento e os artefatos XML/JSON.

O PGRAFIT---A-Graph-Visualization e um repositorio separado que fornece
a interface para visualizar e consultar esses grafos. A conversao XML que
antes existia no backend do PGRAFIT agora e realizada por esta API.

## Requisitos e execucao local

- Python e dependencias de `Requirements.txt`. O ambiente local foi testado
  com Python 3.10; a imagem Docker utiliza Python 3.12.
- MySQL externo para inicializacao dos dados e otimizacao dos grafos.
- Node.js e o repositorio PGRAFIT apenas para executar a interface.

Na raiz deste repositorio:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r Requirements.txt
```

Configure a conexao em um arquivo `.env` ou nas variaveis do processo:

```dotenv
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=KnowlegeGraphDB
```

O nome padrao e `KnowlegeGraphDB`, com essa grafia. A conexao usa a porta
padrao do MySQL, 3306; `DB_PORT` ainda nao e lida pelo codigo.
Ao inicializar a conexao, a aplicacao tenta criar o banco e as tabelas
necessarias. O usuario MySQL precisa ter as permissoes correspondentes.

Inicie a API:

```powershell
python -B -m API.app
```

Alternativamente:

```powershell
python -B -m flask --app API.app run --host=127.0.0.1 --port=3000
```

A API fica em http://localhost:3000. Consultar status, converter XML e
baixar artefatos existentes nao exige conexao com o banco. A otimizacao exige
o MySQL e as relacoes armazenadas.

## Integracao com PGRAFIT

No repositorio PGRAFIT, configure `.env.local`:

```dotenv
CLASSIFICATION_API_URL=http://127.0.0.1:3000
```

Execute o frontend em outra porta:

```powershell
npm install
npm run dev -- --port 3001
```

Abra http://localhost:3001. O Next.js encaminha chamadas de
`/api/classification/...` para esta API. O backend Flask legado do PGRAFIT
na porta 5000 esta depreciado e nao precisa ser iniciado.

## Rotas

| Metodo | Rota | Resposta ou efeito |
| --- | --- | --- |
| GET | `/` | Texto `execute`; usado pelo healthcheck |
| POST | `/convert` | Converte o arquivo XML multipart `file`; retorna `json_content` como string JSON |
| GET | `/GraphRequest` | Download do XML completo |
| GET | `/GraphRequest?format=json` | Grafo completo em JSON |
| GET | `/OptimizeGraphRequest/<sensores>` | Gera e baixa o XML otimizado |
| GET | `/OptimizeGraphRequest/<sensores>/<porcentagem>` | Gera e baixa XML com filtro de probabilidade |
| GET | `/OptimizeGraphRequest/download.xml` | Download do ultimo XML otimizado |
| GET | `/saved_models` | Catalogo de caminhos relativos dos modelos |
| GET, POST | `/saved_model/<caminho>` | Download de um arquivo de modelo |
| GET | `/UpdateGraphRequest/0` | Consulta a solicitacao pendente |
| GET | `/UpdateGraphRequest/1` | Limpa a solicitacao |
| GET | `/UpdateGraphRequest/2` | Registra a solicitacao `graph_update` |

Sensores sao separados por underscore, como `acc_gyr`.
A porcentagem deve ser inteira, de 0 a 100. As rotas de otimizacao e de
download do grafo otimizado tambem aceitam `?format=json`.

A leitura do grafo completo em JSON usa `download/KnowledgeBase.json`
quando o arquivo existe; caso contrario, converte `KnowledgeBase.xml`.
Os dois formatos podem divergir se os artefatos forem atualizados separadamente.
Para grafos otimizados, a resposta JSON e convertida do XML gerado.

O conversor limita a requisicao a 16 MB. XML invalido retorna 400 no upload;
artefatos ausentes retornam 404, artefatos invalidos retornam 422 na leitura
JSON e falhas de otimizacao retornam 503.

## Docker

A imagem inclui API, worker legado, datasets, modelos e dependencias de
treinamento. Supervisor executa Gunicorn e `API/MainServer.py` no mesmo
container. O MySQL e o PGRAFIT permanecem externos.

```powershell
docker build -t classification-graph:complete .
docker run --name classification-graph `
  -p 3000:3000 `
  -e DB_HOST="host.docker.internal" `
  -e DB_USER="root" `
  -e DB_PASSWORD="sua_senha" `
  -e DB_NAME="KnowlegeGraphDB" `
  -e API_URL_BASE="http://127.0.0.1:3000" `
  -v "${PWD}\download:/app/download" `
  -v "${PWD}\Server\MLModels\saved_models:/app/Server/MLModels/saved_models" `
  classification-graph:complete
```

O exemplo usa Docker Desktop e MySQL no host. Para outro servidor ou ambiente
Linux, configure `DB_HOST` com um endereco acessivel pelo container.
Garanta permissao de escrita nas pastas de artefatos montadas.

`API_URL_BASE` configura a comunicacao do worker com esta API.
`CLASSIFICATION_API_URL` e a variavel do PGRAFIT; em containers separados,
ela deve apontar para o nome DNS do servico Classification e a porta interna.

O container roda como usuario `graph`, publica a porta 3000 e verifica
a rota `/`. Esse healthcheck confirma a resposta da API, nao a saude do
MySQL nem a conclusao de um treinamento. Recrie a imagem apos alterar o codigo.

## Treinamento e limitacoes atuais

`Server/MainFunctions.py` contem o pipeline de treinamento e exportacao.
`API/MainServer.py` consulta as solicitacoes e aciona a implementacao legada
em `API/ServerProcessApi.py`.

O treinamento automatico ainda possui pendencias de importacao, inicializacao
e caminhos. A imagem inclui os componentes, mas isso nao garante que o
retreinamento completo esteja funcional.

As solicitacoes ficam em memoria no processo da API. Reiniciar o processo
limpa esse estado. As rotas atuais nao informam progresso nem conclusao,
e limpar uma solicitacao nao interrompe um treinamento ja iniciado.

O artefato `download/KnowledgeBase.xml` existente contem marcadores de
conflito de merge. Sua leitura como XML precisa ser corrigida; a interface
pode carregar o JSON exportado enquanto isso.

## Datasets

Para adicionar um dataset:

1. Coloque os arquivos em `Server/Datasets/Source/`.
2. Implemente o leitor em `Server/Datasets/DatasetManipulation/Format/`,
   seguindo os exemplos `Dataset1.py` e `Dataset2.py`.
3. Ajuste o processamento em `Server/Datasets/DatasetManipulation/Preprocessing/`
   quando houver novos sensores ou combinacoes.
4. Atualize `Server/MainFunctions.py` com as entradas, modelos e relacoes.

## Verificacao

```powershell
python -B -m unittest discover -s tests -v
```

Os testes da integracao usam arquivos temporarios e simulam a otimizacao
para nao depender do MySQL. A verificacao manual pelo PGRAFIT tambem foi
realizada com o MySQL local.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| `API/app.py` | Rotas Flask e downloads |
| `API/converter.py` | Conversao XML usada pelo upload e pelas respostas JSON |
| `API/MainServer.py` | Loop do worker legado |
| `Server/Database/` e `Server/DAO/` | Conexao, tabelas e acesso ao grafo |
| `Server/MLModels/` | Treinamento e modelos salvos |
| `Server/Datasets/` | Fontes e processamento dos datasets |
| `download/` | Grafos exportados |
| `docker/supervisord.conf` | Configuracao dos processos do container |
