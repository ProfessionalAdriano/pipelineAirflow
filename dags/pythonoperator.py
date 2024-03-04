from airflow import DAG 
from airflow.operators.python import PythonOperator
from datetime import datetime 
import pandas as pd
import statistics as sts

dag = DAG('pythonoperator', 
        description="pythonoperator",
        schedule_interval=None, 
        start_date=datetime(2024, 2, 22), 
        catchup=False)     


def data_cleaner():
    dataset = pd.read_csv("/opt/airflow/data/Churn.csv", sep=";")
    dataset.columns = [ "id", "score", "estado", "genero", "idade", "patrimonio", "saldo", "produtos", "temcartcredito", "ativo", "salario", "saiu" ]  
    
    mediana = sts.median(dataset['salario'])
    dataset['salario'].fillna(mediana, inplace=True) # Persiste alteracao da coluna

    dataset['genero'].fillna('masculino', inplace=True) # Substitui valores null por masculino

    mediana = sts.median(dataset['idade'])
    dataset.loc[(dataset["idade"] < 0 ) | 
                (dataset['idade'] > 120 ), 'idade' ] = mediana
    
    dataset.drop_duplicates(subset='id', keep='first', inplace=True)
    
    
    dataset.to_csv("/opt/airflow/data/Churn_clean.csv", sep=";", index=False)   
    return dataset    


#Execute Function 
#data_cleaner()


task1 = PythonOperator(task_id='task1', python_callable=data_cleaner, dag=dag)
task1






