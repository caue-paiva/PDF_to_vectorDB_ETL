## PDF_TO_VECTORDB_ETL

:us:

# Extract-Transform-Load pipeline for extracting pdf contents and uploading to a vectorDB

## About the project

This project is part of the tech developed and used for a [research grant program](http://lattes.cnpq.br/2223448141926231) with the  **Brazilian National Council for Scientific and Technological Development (CNPq)** for the **R&D of Artificial Intelligence tech for educational purposes** within the reality of Brazilian High school students. The main AI/Chatbot application created for this program can be found on this [repo](https://github.com/caue-paiva/educa_gpt_publico) 

One of the features of the chatbot application is a **RAG** (retrieval augmented generation) feature that allows users to request **brazilian university admittance standardized test (ENEM)** questions to the LLM, permiting a more active study pattern focused on question-solving

To allow that feature to work well, **a dataset of ENEM questions and answers was needed**, but large scale data for that is hard to come by, thats where this project comes in.

For the Extraction and Load part, this project provides an **extractor of ENEM PDFs**, downloaded from the official [goverment website](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos), that **produces .txt or .json files** with the **test questions** and their respective correct answer or simply **streams the question data as strings to be used for other pipeline actions**

For the Load part, an **ETL class** was developed that takes the extracted strings from the previous step and **loads them into the Qdrant VectorDB**, given a certain Qdrant client and collection. **Metadata from each question, such as its subject and year is included** with each vector loaded into the collection

For **better observability and record-keeping**, a parameter can be passed into the ETL methods for **saving the extraction data** (how many questions were extracted , separated by year and subject) into a **CSV file using a pandas Dataframe**


## How to use the project

# 1) Clone the repository:
```bash
git clone  https://github.com/caue-paiva/PDF_to_vectorDB_ETL
```

# 2) Install the dependencies
```bash
pip install -r requirements.txt
```


# 3) Provide the necessary keys for the Qdrant and OpenAI APIs on the public_keys.env file
```
QDRANT_HOST = {your qdrant host URL}
QDRANT_API =  {qdrant api key}
QD_TEST_COLLECTION =  {the name of your qdrant collection}
OPENAI_API_KEY =  {openAI API key}
```

# 4) Import the ETL class 
```Python
from pdf_to_qdrant_etl import PdfToQdrantETL
```

# 5) Create a qdrant client instance
```Python 
client = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
)
```

# 6) Create a qdrant_etl instance
```Python
etl = PdfToQdrantETL(Qdrant_client=client)
```

# 7) user the ETL methods of the class

* 7.1) Extract the contents of a single test
```Python
etl.process_file(
    QD_collection_name= os.getenv("QD_TEST_COLLECTION"),
    save_extraction_stats= True,
    stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv"),
     #path to the .csv file that will save the extraction metadata
    test_pdf_path=  os.path.join("pdfs_enem","pdfs_enem/2020","2020_PV_impresso_D1_CD1.pdf"),
    #path to the  ENEM test pdf file 
    answers_pdf_path=os.path.join("pdfs_enem","pdfs_enem/2020","2020_GB_impresso_D1_CD1.pdf")
    #path to the answers PDF file associated with the test
)

```


*  7.2) Extract the contents of a folder with one or more tests
```Python
etl.process_folder(
    folder_path= os.path.join("pdfs_enem","2022"), #path to the directory with the test and answers pdf
    QD_collection_name= os.getenv("QD_TEST_COLLECTION"),
    save_extraction_stats= True,
    stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv")
   
)
```

<br>
<br>
<br>

## PDF_TO_VECTORDB_ETL

:brazil:

# Pipeline de Extração-Transformação-Carregamento para extrair conteúdos de pdf e carregar em um vectorDB

## Sobre o projeto

Este projeto faz parte da tecnologia desenvolvida e utilizada para um programa de [bolsas de pesquisa](http://lattes.cnpq.br/2223448141926231) com o Conselho Nacional de Desenvolvimento Científico e Tecnológico **(CNPq)** do Brasil para o **P&D de tecnologia de Inteligência Artificial para fins educacionais** dentro da realidade dos estudantes do Ensino Médio Brasileiro. O principal aplicativo AI/Chatbot criado para este programa pode ser encontrado neste [repositório](https://github.com/caue-paiva/educa_gpt_publico)


Uma das características do aplicativo chatbot é um recurso **RAG (retrieval augmented generation)** que permite aos usuários solicitar **questões do exame nacional do ensino médio (ENEM)** ao LLM, permitindo um padrão de estudo mais ativo focado na resolução de questões

Para permitir que esse recurso funcione bem, era necessário um **conjunto de dados de questões do ENEM e suas respostas** , mas dados em grande escala para isso são difíceis de obter, é aí que entra este projeto.

Para a parte de Extração e Carregamento, este projeto fornece um **extrator de PDFs do ENEM**, baixados do [site oficial](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/provas-e-gabaritos) do governo, que **produz arquivos .txt ou .json com as questões de teste e suas respectivas respostas corretas** ou simplesmente faz um **stream de dados das questões como strings** para serem usados em outras ações de pipeline

Para a parte de Carregamento, uma **classe ETL** foi desenvolvida que pega as **strings extraídas da etapa anterior e as carrega no Qdrant VectorDB**, dado um certo cliente e coleção Qdrant. **Metadados de cada questão**, como seu assunto e ano, são incluídos com cada vetor **carregado na coleção**

Para **melhor observabilidade e registro**, um parâmetro pode ser passado nos métodos ETL para **salvar os dados da extração** (quantas questões foram extraídas, separadas por ano e assunto) em um **arquivo CSV usando um Dataframe do pandas**

## Como usar o projeto

# 1) Clone o repositório:
```bash 
git clone https://github.com/caue-paiva/PDF_to_vectorDB_ETL 
```
# 2) Instale as dependências
```bash 
pip install -r requirements.txt 
```
# 3) Forneça as chaves necessárias para as APIs do Qdrant e OpenAI no arquivo public_keys.env
 ```
 QDRANT_HOST = {seu URL de host do qdrant} 
 QDRANT_API = {chave da api do qdrant} 
 QD_TEST_COLLECTION = {o nome da sua coleção qdrant} 
 OPENAI_API_KEY = {chave da API openAI} 
```
# 4) Importe a classe ETL
```Python
 from pdf_to_qdrant_etl import PdfToQdrantETL 
```
# 5) Crie uma instância do cliente qdrant
```Python 
client = qdrant_client.QdrantClient(  url=os.getenv("QDRANT_HOST"),  api_key=os.getenv('QDRANT_API'), ) 
```
# 6) Crie uma instância do qdrant_etl
```Python 
etl = PdfToQdrantETL(Qdrant_client=client) 
```
# 7) use os métodos ETL da classe

* 7.1) Extraia o conteúdo de um único teste
```Python
etl.process_file(
 QD_collection_name= os.getenv("QD_TEST_COLLECTION"),"
 save_extraction_stats= True,"
 stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv"),"
 #caminho para o arquivo .csv que salvará os metadados da extração"
test_pdf_path=  os.path.join("pdfs_enem","pdfs_enem/2020","2020_PV_impresso_D1_CD1.pdf"),
#caminho para o pdf com a prova do enem
answers_pdf_path=os.path.join("pdfs_enem","pdfs_enem/2020","2020_GB_impresso_D1_CD1.pdf")
#caminho para o pdf com o gabarito da prova do enem
```

*  7.2) Extrair os conteúdos de um folder com uma ou mais provas
```Python
etl.process_folder(
    folder_path= os.path.join("pdfs_enem","2022"), #camingo para o folder com os PDFs da prova e do gabairot
    QD_collection_name= os.getenv("QD_TEST_COLLECTION"),
    save_extraction_stats= True,
    stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv")
)
```

