from enem_pdf_extractor import EnemPDFextractor
from qdrant_text_loader import QdrantTextLoader
import qdrant_client ,os 

"""
TODO
fazer uma classe de ETL que herde do QdrantTextLoader e do EnemPDFextractor para realizar a pipeline completa

modificar o  código do enem_pdf_extractor para colocar um tipo de retorna "str" para que a função não escreva em um arquivo mas sim retorne numa string o conteúdo extraido

"""

class PdfToQdrantETL(EnemPDFextractor,QdrantTextLoader):
    """
    Classe para extração de contéudos de PDFs do ENEM para carregamento  no VectorDB Qdrant, criado para  realização de tarefas de RAG com as questões do ENEM    
    
    OBS: Questões com imagens não são processadas e o contéudo dos PDFs é transformado em um arquivo TXT
    """
    

    def __init__(self, output_type: str, process_questions_with_images: bool = True) -> None:
        super().__init__(output_type, process_questions_with_images)


