from pdf_to_qdrant_etl import PdfToQdrantETL
from dotenv import load_dotenv
import os , qdrant_client
load_dotenv(os.path.join("keys_public.env"))

client = qdrant_client.QdrantClient(
     url=os.getenv("QDRANT_HOST"),
     api_key=os.getenv('QDRANT_API'), 
)


etl = PdfToQdrantETL(Qdrant_client=client)

etl.process_folder(
    folder_path= os.path.join("pdfs_enem","2022"),
    QD_collection_name= os.getenv("QD_TEST_COLLECTION"),
    save_extraction_stats= True,
    stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv")
)

etl.process_file(
    QD_collection_name= os.getenv("QD_TEST_COLLECTION"),
    save_extraction_stats= True,
    stats_csv_path= os.path.join("extraction_metadata","test_extraction_metadata.csv"),
    test_pdf_path=  os.path.join("pdfs_enem","pdfs_enem/2020","2020_PV_impresso_D1_CD1.pdf"),
    answers_pdf_path=os.path.join("pdfs_enem","pdfs_enem/2020","2020_GB_impresso_D1_CD1.pdf")
)


"""
ETL test output (terminal):

 
 qntd inicial de vetores 167
Tentou inserir 37 questões do assunto math no vectorDB
Foram inseridas  37 questões do assunto math no vectorDB, para um total de 204 questões
Tentou inserir 29 questões do assunto natu no vectorDB
Foram inseridas  29 questões do assunto natu no vectorDB, para um total de 233 questões
 
 qntd inicial de vetores 233
texto da matéria eng vazio, pulando
Tentou inserir 3 questões do assunto spani no vectorDB
Foram inseridas  3 questões do assunto spani no vectorDB, para um total de 236 questões
Tentou inserir 24 questões do assunto lang no vectorDB
Foram inseridas  24 questões do assunto lang no vectorDB, para um total de 260 questões
Tentou inserir 26 questões do assunto huma no vectorDB
Foram inseridas  26 questões do assunto huma no vectorDB, para um total de 286 questões


Todas as questões das provas do folder (excluindo as com imagens) foram adicionadas, um total de 119 questões de 5 matérias diferentes 

"""