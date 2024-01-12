from enem_pdf_extractor import EnemPDFextractor
from qdrant_text_loader import QdrantTextLoader
import qdrant_client ,os , re

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
    __ANSWER_PDF_IDENTIFIER = "GB"
    __TEST_PDF_IDENTIFIER = "PV"

    enem_pdf_extractor: EnemPDFextractor
    qdrant_text_loader: QdrantTextLoader
    
    def __init__(self, Qdrant_client: qdrant_client.QdrantClient , process_questions_with_images: bool = False, ) -> None:
        """
        Construtor para a classe PdfToQdrantETL, essa classe contem instâncias privadas das classes EnemPDFextractor e QdrantTextLoader

        Args: \n
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

    def __pair_test_answers_pdfs(self,path:str)->list[ tuple[str,str] | None]:
        """
        retorna uma lista de tuplas com as provas e seus gabaritos (prova no index 0 e gabarito no index 1) \n
        caso uma prova não tenha um gabarito correspondente, retorna uma lista vazia 
        
        """
        DAY_PATTERN = r"D[12]"
        TEST_COLOR_PATTERN = r"CD[1-9]"
        test_pdfs:list[str] = []
        answers_pdfs:list[str] = []
        file_pairs: list[tuple[str,str]] = []

        for file in os.listdir(path):
            if self.__ANSWER_PDF_IDENTIFIER in file:
                answers_pdfs.append(file)
            elif self.__TEST_PDF_IDENTIFIER in file:
                test_pdfs.append(file)
        
        for test_pdf in test_pdfs:
            pdf_day:str = re.findall(DAY_PATTERN,test_pdf)[0]
            pdf_color:str = re.findall(TEST_COLOR_PATTERN,test_pdf)[0]

            for answer_pdf in answers_pdfs:
                if pdf_color in answer_pdf and pdf_day in answer_pdf:
                    file_pairs.append((os.path.join(path,test_pdf),os.path.join(path,answer_pdf)))
                    break
            else:
                return []
        
        return file_pairs # type: ignore
        
    def process_file(
        self, 
        QD_collection_name:str , 
        test_pdf_path: str , 
        answers_pdf_path: str , 
        save_extraction_stats: bool = False , 
        stats_csv_path: str = "" 
    )->bool:
        """
        Função para processar um arquivo em PDF do enem e colocar seus conteúdos (questões e respostas) processados numa coleção do vectorDB do qdrant
    
        Args: \n
        QD_collection_name (str): nome da coleção do qdrant que vai receber esses conteúdos \n
        test_pdf_path (str): caminho pro arquivo da prova do ENEM \n
        answer_pdf_path(str): caminho para o arquivo de gabarito da prova do ENEM \n
        save_extraction_stats (bool, default = False): Salvar ou não estatísticas da quantidade de questões carregadas no vectorDB, separadas por ano e matéria  \n
        stats_csv_path (str, default = ""): caso o argumento acima seja True, qual deve ser o caminho do arquivo .csv em que esses dados serão guardados
                
        """
        
        extraction_return: dict[str,str]  = self.enem_pdf_extractor.extract_pdf(test_pdf_path=test_pdf_path, answers_pdf_path=answers_pdf_path)

        if not isinstance(extraction_return, dict):
            raise TypeError(f"retorno da extração veio com tipo errado, era experado um dict mas foi retornado {type(extraction_return)}")
        
        return self.qdrant_text_loader.dict_to_vectorDB(
            QD_collection= QD_collection_name,
            subjects_and_questions= extraction_return,
            save_extraction_stats= save_extraction_stats,
            stats_csv_path= stats_csv_path
        )
   
    def process_folder(
        self,
        folder_path:str,
        QD_collection_name:str , 
        save_extraction_stats: bool = False,
        stats_csv_path = ""    
    )->None:
        """
        Função para processar um folder inteiro de PDFs do ENEM e carregar seus conteúdos (questões e respostas) numa coleção do Qdrant vectorDB

        OBS: o folder deve conter pares compostos por provas do ENEM e seus respectivos gabaritos ,
        ex: 
           Prova: 2020_PV_impresso_D1_CD1.pdf

           Gabarito associado: 2020_GB_impresso_D1_CD1.pdf
        
        Args: \n
        QD_collection_name (str): nome da coleção do qdrant que vai receber esses conteúdos \n
        folder_path (str): caminho para o folder/diretório onde os PDFs estão \n
        save_extraction_stats (bool, default = False): Salvar ou não estatísticas da quantidade de questões carregadas no vectorDB, separadas por ano e matéria  \n
        stats_csv_path (str, default = ""): caso o argumento acima seja True, qual deve ser o caminho do arquivo .csv em que esses dados serão guardados
    
        """
        
        if not os.path.isdir(folder_path):
            raise IOError("caminho especificado não é um diretório válido")
        else:
            pdf_num: int = self.__count_pdfs_in_dir(folder_path)
            if pdf_num < 2:
                raise IOError("o folder indicado contém menos que 2 arquivos PDFs, é necessário pelo menos 2 PDFs (uma prova e uma gabarito)")
            elif  (pdf_num % 2 != 0):
                raise IOError("o folder indicado contém um número ímpar de arquivos PDFs, é necessário pares de PDFs (uma prova e uma gabarito)")
            
        test_answer_pdf_pairs: list[tuple] | None = self.__pair_test_answers_pdfs(folder_path)

        if not test_answer_pdf_pairs:
            raise IOError("não foi possível associar cada prova no folder com um gabarito compatível")
        
        return_flag: bool = True
        for test,answer in test_answer_pdf_pairs:
            result: bool = self.process_file(
                 QD_collection_name= QD_collection_name,
                 test_pdf_path= test,
                 answers_pdf_path= answer,
                 save_extraction_stats= save_extraction_stats,
                 stats_csv_path= stats_csv_path
            )

            if not result:
                print(f"não foi possível adicionar informações do par prova {test} e gabarito {answer}")
                return_flag = False
        
        return return_flag
            






