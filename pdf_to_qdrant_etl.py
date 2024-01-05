from typing import Any, Callable
from enem_pdf_extractor import EnemPDFextractor
from qdrant_text_loader import QdrantTextLoader
import qdrant_client ,os 

"""
TODO
fazer uma classe de ETL que herde do QdrantTextLoader e do EnemPDFextractor para realizar a pipeline completa

modificar o  código do enem_pdf_extractor para colocar um tipo de retorna "str" para que a função não escreva em um arquivo mas sim retorne numa string o conteúdo extraido

"""

class PdfToQdrantETL():
    """
    Classe para extração de contéudos de PDFs do ENEM para carregamento  no VectorDB Qdrant, criado para  realização de tarefas de RAG com as questões do ENEM    
    
    OBS: Questões com imagens não são processadas e o contéudo dos PDFs é transformado em um arquivo TXT
    """

    __PDF_EXTRACT_OUTPUT_TYPE = "dict"

    enem_pdf_extractor: EnemPDFextractor
    qdrant_text_loader: QdrantTextLoader
    
    def __init__(self, Qdrant_client: qdrant_client.QdrantClient , process_questions_with_images: bool = False, ) -> None:
        """
        Construtor para a classe PdfToQdrantETL, essa classe contem instâncias privadas das classes EnemPDFextractor e QdrantTextLoader

        Args: 
            processs_questions_with_images (bool, default = False): indica se questões que tenham imagens deve ser extraídas ou não, caso seja True um número maior 
            de questões será extraída, porém essas questões potencialmente não terão o contexto importante das imagens, atrapalhando seu uso em tarefas de RAG ou treinamento de modelos de NLP
        """
        self.enem_pdf_extractor = EnemPDFextractor(
            output_type = self.__PDF_EXTRACT_OUTPUT_TYPE, 
            process_questions_with_images= process_questions_with_images
        )
        self.qdrant_text_loader = QdrantTextLoader(QDclient= Qdrant_client)
    
    def __count_pdfs_in_dir(self, path:str)->int:
        return len([file for file in os.listdir(path) if file.lower().endswith(".pdf") and os.path.isfile(os.path.join(path,file))] )

    def process_file(
        self, 
        QD_collection_name:str , 
        test_pdf_path: str , 
        answers_pdf_path: str , 
        save_extraction_stats: bool = False , 
        stats_csv_path: str = "" 
    )->None:
        """
        Função para processar um arquivo em PDF do enem e colocar seus conteúdos (questões e respostas) processados numa coleção do vectorDB do qdrant
    
        Args:
           QD_collection_name (str): nome da coleção do qdrant que vai receber esses conteúdos
           test_pdf_path (str): caminho pro arquivo da prova do ENEM
           answer_pdf_path(str): caminho para o arquivo de gabarito da prova do ENEM
                
        """
        
        extraction_return: dict[str,str] = self.enem_pdf_extractor.extract_pdf(test_pdf_path=test_pdf_path, answers_pdf_path=answers_pdf_path)

        if not isinstance(extraction_return, dict):
            raise TypeError(f"retorno da extração veio com tipo errado, era experado um dict mas foi retornado {type(extraction_return)}")
        
        self.qdrant_text_loader.dict_to_vectorDB(
            QD_collection= QD_collection_name,
            subjects_and_questions= extraction_return,
            save_extraction_stats= save_extraction_stats,
            stats_csv_path= stats_csv_path
        )
   
    def process_folder(
        self,
        folder_path:str,
        save_extraction_stats: bool = False,
        stats_csv_path = ""    
    )->None:
        
        if not os.path.isdir(folder_path):
            raise IOError("caminho especificado não é um diretório válido")
        else:
            pdf_num: int = self.__count_pdfs_in_dir(folder_path)
            if pdf_num < 2:
                raise IOError("o folder indicado contém menos que 2 arquivos PDFs, é necessário pelo menos 2 PDFs (uma prova e uma gabarito)")
            elif  (pdf_num % 2 != 0):
                raise IOError("o folder indicado contém um número ímpar de arquivos PDFs, é necessário pares de PDFs (uma prova e uma gabarito)")




