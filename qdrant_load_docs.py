import os, qdrant_client
from typing import Iterable
from openai import OpenAI
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
#código feito para carregar novos documentos na qdrant cloud
load_dotenv(os.path.join("keys.env"))


openai_api_key = os.getenv('OPENAI_API_KEY') or 'OPENAI_API_KEY'
embed_client = OpenAI()
EMBEDDINGS_MODEL:str = 'text-embedding-ada-002'
COLLECTION_NAME:str = os.getenv("QD_COLLECTION_NAME")
OPENAI_VECTOR_PARAMS = VectorParams(size=1536, distance= Distance.COSINE, hnsw_config= None, quantization_config=None, on_disk=None)


test_question:str = """(Enem/2020)  QUESTÃO 4          
A Minor Bird
I have wished a bird would fly away,
And not sing by my house all day;
Have clapped my hands at him from the door
When it seemed as if I could bear no more.
The fault must partly have been in me.
The bird was not to blame for his key.
And of course there must be something wrong
In wanting to silence any song.
FROST, R. West-running Brook. New York: Henry Holt and Company, 1928.
No poema de Robert Frost, as palavras “fault” e “blame” 
revelam por parte do eu lírico uma
A)culpa por não poder cuidar do pássaro. 
B)atitude errada por querer matar o pássaro. 
C)necessidade de entender o silêncio do pássaro. 
D)sensibilização com relação à natureza do pássaro. 
E)irritação quanto à persistência do canto do pássaro.

(RESPOSTA CORRETA): D"""

query_test:str = """
me de uma questao sobre No poema de Robert Frost, as palavras “fault” e “blame”
"""

client2 = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
)

def qdrant_recreate_collection(name:str, QDclient: qdrant_client.QdrantClient, parameters: VectorParams)->None:
   client2.recreate_collection(  #collection "enem2" já existe com 0 vetores de tam 384 
        collection_name="enem2",
        vectors_config=parameters
    )
 
def upsert_func(docs:list[list], QDclient: qdrant_client.QdrantClient)->None:
    print("upsert")
    QDclient.upsert(
    collection_name= COLLECTION_NAME,
    points= [
        PointStruct(
            id = idx,
            vector = vector,
            payload= {"texto":test_question, "materia": "eng", "ano": 2020}
        )
        for idx, vector in enumerate(docs,0)
    ]
    )

def add_func(in_docs:list, in_metadata:dict, vector_count:int = 1)->None:
  print("add")
  in_docs = [in_docs]
  in_metadata = [in_metadata]
  client2.add(
    collection_name= COLLECTION_NAME,
    documents=  in_docs,
    metadata=  in_metadata,
    ids= [vector_count+1]
  )

def get_openAI_embeddings(text:str)->list[float]:
    response = embed_client.embeddings.create(
        input= text,
        model= EMBEDDINGS_MODEL
    )
    return response.data[0].embedding

def vector_search(vector:list[float], QDclient)->list:
   search = QDclient.search(
    collection_name=COLLECTION_NAME,
    query_vector = vector,
    limit=1
   )

   return search

def text_chunk_splitter(text:str, split_key:str)->Iterable[str]: #a split key vai ser (RESPOSTA CORRETA)
   current_key_posi: int = 0
   CORRECT_ALTERNATIVE_BUFF: int = 22  #tamanho da split key até a alternativa correta:  (RESPOSTA CORRETA): D
   
   while (next_key_posi := text.find(split_key, current_key_posi)) != -1:
      str_slice:str = text[current_key_posi: next_key_posi + CORRECT_ALTERNATIVE_BUFF]
      current_key_posi = next_key_posi + CORRECT_ALTERNATIVE_BUFF  #começar a procurar da posição atual + buffer
      yield str_slice


get_payload = lambda x : x[0].payload

collection:object = client2.get_collection(COLLECTION_NAME)
vector_count:int = collection.vectors_count

print(vector_count)
print(f"my collection:  {collection}")
#metadata = {"materia": "eng", "ano": 2020}

upsert_func([get_openAI_embeddings(test_question)], client2)


#antes da primeira adição tinhamos 44 vectors na collection

#print(client2.get_collection(COLLECTION_NAME))

print(type(vector_search(get_openAI_embeddings(query_test),client2)))

print("\n\n\n")

#print(client.get_collection(COLLECTION_NAME))


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

