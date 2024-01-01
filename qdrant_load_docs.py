import os, qdrant_client, re
import pandas as pd
from typing import Iterable
from openai import OpenAI
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import UpdateResult
from dotenv import load_dotenv
#código feito para carregar novos documentos na qdrant cloud
load_dotenv(os.path.join("keys.env"))

"""
Guarda metadados sobre quais arquivos ja foram add no vectorDB
ja foram: 2020 eng (3) e espa (5) e humanas (34) (sem imagens) todas as qustões add

solução usar o pandas para criar um CSV com as colunas sendo as matérias e as linhas sendo o ano e algo pra identificar se foram as add ou o total de questões do arquivo

"""


openai_api_key = os.getenv('OPENAI_API_KEY') or 'OPENAI_API_KEY'
embed_client = OpenAI()
EMBEDDINGS_MODEL:str = 'text-embedding-ada-002'
COLLECTION_NAME:str = os.getenv("QD_COLLECTION_NAME")
OPENAI_VECTOR_PARAMS = VectorParams(size=1536, distance= Distance.COSINE, hnsw_config= None, quantization_config=None, on_disk=None)
YEAR_PATTERN:str = "20\d{2}" #padrões REGEX para pegar o ano e a matéria de cada arquivo das questões
SUBJECT_PATTERN: str = "_(.{3,}?)_" #padrão para achar a matéria da questão eng, lang, huma.....
CORRECT_ANSWER_STR: str = "(RESPOSTA CORRETA)"
SUBJECT_NAMES: set[str] = {"eng", "huma" , "lang", "spani","math", "natu"}


client2 = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
)

def qdrant_recreate_collection(name:str, QDclient: qdrant_client.QdrantClient, parameters: VectorParams)->None:
   client2.recreate_collection(  #collection "enem2" já existe com 0 vetores de tam 384 
        collection_name="enem2",
        vectors_config=parameters
    )
 
def get_openAI_embeddings(text:str)->list[float]:
    response = embed_client.embeddings.create(
        input= text,
        model= EMBEDDINGS_MODEL
    )
    return response.data[0].embedding

def QDvector_search(vector:list[float], QDclient :qdrant_client.QdrantClient, target_collection:str , vector_num:int = 1)->list:
   search = QDclient.search(
    collection_name=target_collection,
    query_vector = vector,
    limit= vector_num
   )
   return search

def text_chunk_splitter(text:str, split_key:str)->Iterable[str]: #a split key vai ser (RESPOSTA CORRETA)
   """
   Iterador que retorna a proxima substr que corresponde a uma questão inteira
   """
   current_key_posi: int = 0
   CORRECT_ALTERNATIVE_BUFF: int = 22  #tamanho da split key até a alternativa correta:  (RESPOSTA CORRETA): D
   
   while (next_key_posi := text.find(split_key, current_key_posi)) != -1:
      str_slice:str = text[current_key_posi: next_key_posi + CORRECT_ALTERNATIVE_BUFF]
      current_key_posi = next_key_posi + CORRECT_ALTERNATIVE_BUFF  #começar a procurar da posição atual + buffer
      yield str_slice

def etl_metadata_saving(
      stats_csv_path:str, 
      current_year:int, 
      subject: str, 
      all_questions:int,
      added_questions:int
    )->None:
   
    if ".csv" not in stats_csv_path:
      raise IOError("Arquivo não é do tipo CSV")
    
    ALL_QUESTIONS_INDEX: str = f"{current_year} todas questoes" #esses vão ser o nome dos indexes (linhas) do DF para guardar os valores do total de questões de um arquivo e do total add desse arqui
    ADDED_QUESTIONS_INDEX: str = f"{current_year} questoes add"

    if os.path.exists(stats_csv_path):
      df = pd.read_csv(stats_csv_path, index_col= 0)
    else:
      df = pd.DataFrame()
    
    if subject not in df.columns:
      df[subject] = None
    
    if ALL_QUESTIONS_INDEX not in df.index:
       df.loc[ALL_QUESTIONS_INDEX] = None
       df.loc[ADDED_QUESTIONS_INDEX] = None
    
    df.at[ALL_QUESTIONS_INDEX, subject] = all_questions
    df.at[ADDED_QUESTIONS_INDEX, subject] = added_questions

    df.to_csv(stats_csv_path, index=True)

def text_to_vectorDB(
      txt_file_path:str, 
      QDclient:qdrant_client.QdrantClient, 
      target_collection:str, 
      save_extraction_stats: bool = False,
      stats_csv_path: str = ""
      )->None:
  
    if ".txt" not in txt_file_path:
       raise IOError("essa função apenas aceita arquivos .TXT")

    if not isinstance(txt_file_path, str):
        raise TypeError("path para o arquivo não é uma string")

    if not isinstance(QDclient,qdrant_client.QdrantClient):
        raise TypeError("Argumento do cliente do Qdrant não é do tipo suportadp")
 
    backslash_index: int = txt_file_path.rfind("/") #vai da direita pra esquerda até ahcar o primeiro / , isso é para isolar apenas o nome do arquivo no path e permitir achar a matéria
    file_str:str = txt_file_path[backslash_index+1 : len(txt_file_path)]

    if not (matches_list_year := re.findall(YEAR_PATTERN,file_str)):
       raise IOError("Nome do arquivo não tem referencia ao ano da prova")
    else:
       test_year: int = int(matches_list_year[0])
    
    if not (matches_list_subj := re.findall(SUBJECT_PATTERN, file_str)):
       raise IOError("Nome do arquivo não tem referencia à matéria das questões")
    else:  
        subject:str = matches_list_subj[0]
    print(subject)
    collection:object = QDclient.get_collection(target_collection)
    print(collection)
    vector_count:int = collection.vectors_count     #esse vai ser o id que o vetor a ser inserido vai ter, ele depende da quantidade de vetores já existentes
    start_amount: int = vector_count  #o primeiro vetor foi add com id=0 , o segundo com id=1, então o ID do novo vai ser a qntd de vetores ja existentes
    
    with open(txt_file_path, "r") as f:
        entire_text: str = f.read()

    for text_chunk in text_chunk_splitter(entire_text, CORRECT_ANSWER_STR):  #
        vectors:list[list[float]] =  [get_openAI_embeddings(text_chunk)]
        
        QDclient.upsert(
            collection_name= target_collection,
            points= [
             PointStruct(
               id = idx,
               vector = vector,
               payload= {"page_content":text_chunk, "metadata": {"materia": subject, "ano": test_year}}
             )
            for idx, vector in enumerate(vectors,vector_count)] 
        )
        vector_count += 1
    
    all_new_questions: int = vector_count - start_amount
    print(f"Tentou inserir {all_new_questions} questões no vectorDB") #quantidade de novas questões

    final_vector_count: int  = QDclient.get_collection(target_collection).vectors_count #mudança na qntd de vetores no vector db
    questions_added: int = final_vector_count - start_amount
    print(f"Foram inseridas  {questions_added} questões no vectorDB")   

    if save_extraction_stats:
        etl_metadata_saving(
           stats_csv_path=stats_csv_path,
           current_year= test_year,
           subject= subject,
           all_questions= all_new_questions,
           added_questions= questions_added 
        )  

    if all_new_questions !=  questions_added:
       print("Não foi possível adicional todas as questões no vectorDB") 

text_to_vectorDB(
    txt_file_path="2020_D2_/2020_math_questions.txt", 
    QDclient=client2, 
    target_collection= COLLECTION_NAME,
    save_extraction_stats=True,
    stats_csv_path = "qdrant_extraction_data.csv"
)

print(client2.get_collection(COLLECTION_NAME))

"""print(QDvector_search(
   vector= get_openAI_embeddings("refugiado nigeriano"),
   QDclient= client2,
   target_collection=COLLECTION_NAME
))"""


#get_payload = lambda x : x[0].payload
#collection:object = client2.get_collection(COLLECTION_NAME)
#vector_count:int = collection.vectors_count

#collection:object = client2.get_collection(COLLECTION_NAME)

#antes da primeira adição tinhamos 44 vectors na collection

#print(client2.get_collection(COLLECTION_NAME))

#print(client.get_collection(COLLECTION_NAME))

#extract_text("2020_D1_/2020_huma_questions.txt")



"""

#adicionar docs para a vectorstore
def text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(  #objeto de cortar textos do langchain
    chunk_size = 2200, #cada chunk de texto tem no máximo 2200 caracteres, melhor numero que eu testei ate agora
    #mudar entre linux e windows parece resultar em problemas no textspitter, no windows o melhor parece ser 1600 caracteres, e no linux 1800 caracteres
    chunk_overlap  = 0,
    separators=["(Enem/"]  #divide partes do texto ao encontrar essa string, agrupa pedaços de texto entre a occorrencia dessa string
    )

    chunks = text_splitter.split_documents(text)

    return chunks

loader = TextLoader("vector_DB_test/questoes_ling_redu.txt")  #carrega o arquivo txt à ser adicionado
documents = loader.load()

parsed_text = text_chunks(documents)  #extrai pedaços do texto e coloca num array
for i in range(len(parsed_text)):
    parsed_text[i] = parsed_text[i].page_content #extrai o texto em si, antes o texto estavo num obj langchain


#print(type(parsed_text[0]))
#print(parsed_text[0])

#print(doc_store.add_texts(parsed_text)) #adiciona os novos pedaços de texto na doc_store, printar os vetores de return para verificar se deu certo


#print(client.get_collection(collection_name=os.getenv("QD_COLLECTION_NAME")))
#ver a coleção atual e ver se os novos vetores foram realmente adicionados

#ultima vez deu que tinha 38 vectors


def get_embeddings(text:str)->list[float]:
    response = embed_client.embeddings.create(
        input= test_question,
        model= EMBEDDINGS_MODEL
    )
    return response.data[0].embedding """

#returned = client.query(
   # collection_name= COLLECTION_NAME,   
   # query_text= "testando",
    #limit=2,
#)

"""def QD_upsert_func(text:str, 
    vectors:list[list], 
    QDclient: qdrant_client.QdrantClient, 
    start_id: int ,
    question_year:int,
    question_subject:str,   
    target_collection: str        
)->None:
    
    QDclient.upsert(
    collection_name= target_collection,
    points= [
        PointStruct(
            id = idx,
            vector = vector,
                payload= {"page_content":text, "metadata": {"materia": question_subject, "ano": question_year}}
        )
        for idx, vector in enumerate(vectors,start_id)
    ]
    )"""

"""def QDadd_func(in_docs:list, in_metadata:dict, vector_count:int = 1)->None:
  print("add")
  in_docs = [in_docs]
  in_metadata = [in_metadata]
  client2.add(
    collection_name= COLLECTION_NAME,
    documents=  in_docs,
    metadata=  in_metadata,
    ids= [vector_count+1]
  )"""
