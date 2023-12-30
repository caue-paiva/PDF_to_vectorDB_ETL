import os, qdrant_client
from re import L
from openai import OpenAI
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
#código feito para carregar novos documentos na qdrant cloud
load_dotenv(os.path.join("keys.env"))


openai_api_key = os.getenv('OPENAI_API_KEY') or 'OPENAI_API_KEY'
embed_client = OpenAI()
EMBEDDINGS_MODEL:str = 'text-embedding-ada-002'
COLLECTION_NAME:str = os.getenv("QD_COLLECTION_NAME")

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
me de uma questao sobre refugiados na nigeria 
"""

client = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
)
 
"""client.recreate_collection(  #collection "enem2" já existe com 0 vetores de tam 384 
        collection_name="enem2",
        vectors_config= VectorParams(size=384, distance=Distance.COSINE),
)"""





#print(response)

#print("\n\n")

docs = [test_question]
metadata = {"materia": "eng", "ano": 2020}




#print(client.get_collection(COLLECTION_NAME))  #antes da primeira adição tinhamos 44 vectors na collection


"""client.add(
  collection_name= COLLECTION_NAME,
  documents=  docs,
  metadata= metadata,
  ids= 1
)"""

#print(client.get_collection(COLLECTION_NAME))
"""search = client.query(
    collection_name=COLLECTION_NAME,
    query_text=query_test,
    limit=1
)

print (search)"""

"""client.upsert(
  collection_name= COLLECTION_NAME,
  points= [
      PointStruct(
          id = idx,
          vector = vector,
          payload= {"texto":test_question }
      )
      for idx, vector in enumerate(docs,48)
  ]
)"""

print("\n\n\n")

print(client.get_collection(COLLECTION_NAME))

#returned = client.query(
   # collection_name= COLLECTION_NAME,   
   # query_text= "testando",
    #limit=2,
#)


#print(returned)

#vectors_config = qdrant_client.http.models.VectorParams(size=1536,distance = qdrant_client.http.models.Distance.COSINE)
#configuração dos vetores, método de pesquisa (COSENO) e tamanho dos vetores (1536 é o tam usada pela openAI)


#retur = client.recreate_collection(collection_name=os.getenv("QD_COLLECTION_NAME"), vectors_config=vectors_config)
# essa linha de código serve para criar coleções do zero ou deletar existentes, cuidado ao mecher com ele

"""doc_store = Qdrant(
    client=client, 
    collection_name=os.getenv("QD_COLLECTION_NAME"), 
    embeddings=embed,
)"""




#adicionar docs para a vectorstore

"""def text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(  #objeto de cortar textos do langchain
    chunk_size = 2200, #cada chunk de texto tem no máximo 2200 caracteres, melhor numero que eu testei ate agora
    #mudar entre linux e windows parece resultar em problemas no textspitter, no windows o melhor parece ser 1600 caracteres, e no linux 1800 caracteres
    chunk_overlap  = 0,
    separators=["(Enem/"]  #divide partes do texto ao encontrar essa string, agrupa pedaços de texto entre a occorrencia dessa string
    )

    chunks = text_splitter.split_documents(text)

    return chunks
"""
"""loader = TextLoader("vector_DB_test/questoes_ling_redu.txt")  #carrega o arquivo txt à ser adicionado
documents = loader.load()

parsed_text = text_chunks(documents)  #extrai pedaços do texto e coloca num array
for i in range(len(parsed_text)):
    parsed_text[i] = parsed_text[i].page_content #extrai o texto em si, antes o texto estavo num obj langchain
    print("\n\n nova questão "+parsed_text[i]+ "\n\n")
"""

#print(type(parsed_text[0]))
#print(parsed_text[0])

#print(doc_store.add_texts(parsed_text)) #adiciona os novos pedaços de texto na doc_store, printar os vetores de return para verificar se deu certo


#print(client.get_collection(collection_name=os.getenv("QD_COLLECTION_NAME")))
#ver a coleção atual e ver se os novos vetores foram realmente adicionados

#ultima vez deu que tinha 38 vectors


"""def get_embeddings(text:str)->list[float]:
    response = embed_client.embeddings.create(
        input= test_question,
        model= EMBEDDINGS_MODEL
    )
    return response.data[0].embedding """

