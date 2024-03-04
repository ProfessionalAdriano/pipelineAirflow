from airflow.models import BaseOperator             # Contem todos os elemntos base de um operador
from airflow.utils.decorators import apply_defaults # Adiciona funcionalidades a mais em uma função sem precisar modificar ela.
import pandas as pd                                 # Será utilizado para persistir o dado


class BigDataOperator():

    @apply_defaults
    def __init__(self,
                 path_to_csv_file,
                 path_to_save_file,
                 separator=';',
                 file_type='parquet',
                 *args,             # Nº variável de argumentos, e esse argumentos tem uma posição certa.
                 **kwargs           # nº variável de argumentos, no estilo chave e valor.                 
                 ) -> None:         # None --> Sign. que essa função não retorna nada.      
          
        # CONSTRUTOR:
        # Criando propriedade para receber os argumentos passados no construtor da classe.  
        super().__init__(*args,**kwargs)        
        self.path_to_csv_file = path_to_csv_file        # Origem 
        self.path_to_save_file = path_to_save_file      # Destino 
        self.separator = separator
        self.file_type = file_type


def execute(self, context):
    df = pd.read_csv(self.path_to_csv_file, sep= self.separator)
    if self.file_type == 'parquet':
        df.to_parquet(self.path_to_save_file)
    elif self.file_type == 'json':
        df.to_json(self.path_to_save_file)
    else:
        raise ValueError("O valor é inválido")
    

