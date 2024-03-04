from airflow import DAG 
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.email import EmailOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

from random import uniform
import json  # Para ler o Dado e as variáveis
import os    # Ler arq
import time

# Import Sensors:
from airflow.sensors.filesystem import FileSensor


# Parametros padrao que se aplica a todas as Dags:
default_args = {
    'depends_on_past' : False, # 
    'email': ['xxxx.xxx@gmail.com'],          # Onde será enviado em caso de falha
    'email_on_failure': True,                 # Envia um e-mail em caso de falhas   
    'email_on_retry': False,                  # Email um e-mail caso a tarefa seja executada automaticamente
    'retries': 1,                             # Define a qtde de tentativas
    'retry_delay': timedelta(seconds=10)      # Tempo para nova tentativa
    }   




dag = DAG('gera_dados_turbina', 
          description='gera_dados_turbina',           
          #schedule_interval=None,    
          schedule_interval='*/1 * * * *',        # schedule_interval='*/3 * * * *' Template p/ rodar a cada 3 min
          start_date=datetime(2024, 2, 4), 
          catchup=False,
          default_args=default_args,
          default_view='graph',
          doc_md='## Dag para registrar dados da turbina eólica')                        


# Definindo Grupos:
group_check_temp = TaskGroup('group_check_temp', dag=dag)
group_database = TaskGroup('group_database', dag=dag)


def gera_dados():  
    
    dados_pf    = round(uniform(0.7,1), 2)        
    dados_hp    = round(uniform(70,80), 2)
    dados_tp    = round(uniform(20,25), 2)

    delta = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
                                                    
    file_name   = 'data_turbine.json'
    source_path = f'/home/adriano/ed/APP/data/{file_name}'   

    registro = {'idtemp' : str(id), 
                'powerfactor' : str(dados_pf),
                'hydraulicpressure' : str(dados_hp) ,
                'temperature' : str(dados_tp) 
                ,'timestamp' : str(delta) }
    
    with open(source_path, 'w') as fp: 
        json.dump(registro, fp)

        

file_sensor_task = FileSensor(
    task_id='file_sensor_task', 
    filepath=Variable.get('path_file'),  # Variável criada no Airflow contendo o diretório da máq host
    fs_conn_id='fs_default',             # Variável criada no Airflow contendo a id da conexão. 
    poke_interval=60,                    # Intervalo entre verificações do arquivo (em segundos)
    dag=dag )



# Ler os dados do arquivo e carregar em variáveis xcom.
def process_file(**kwarg):
    with open(Variable.get('path_file')) as f:
        data = json.load(f)
        kwarg['ti'].xcom_push(key='idtemp',value=data['idtemp'])
        kwarg['ti'].xcom_push(key='powerfactor',value=data['powerfactor'])
        kwarg['ti'].xcom_push(key='hydraulicpressure',value=data['hydraulicpressure'])
        kwarg['ti'].xcom_push(key='temperature',value=data['temperature'])
        kwarg['ti'].xcom_push(key='timestamp',value=data['timestamp'])
    
    # Após ler e carregar os dados, excluir o arquivo.
    os.remove(Variable.get('path_file'))


def avalia_temp(**context):
    number = float( context['ti'].xcom_pull(task_ids='get_data_task', key="temperature"))
    if number >= 24 :
        return 'group_check_temp.send_email_alert_task'
    else:
        return 'group_check_temp.send_email_normal_task'



                             
check_temp_branc_task = BranchPythonOperator(
                                task_id = 'check_temp_branc_task',
                                python_callable=avalia_temp,
                                provide_context = True,
                                dag=dag,
                                task_group=group_check_temp)



get_data_task = PythonOperator(task_id='get_data_task',
                               python_callable=process_file,
                               provide_context=True,
                               dag=dag)

create_table_task = PostgresOperator(task_id="create_table_task",
                                postgres_conn_id='postgres', # conexão criado no Airflow
                                sql='''create table if not exists sensors 
                                        (  idtemp            varchar
                                         , powerfactor       varchar
                                         , hydraulicpressure varchar
                                         , temperature       varchar
                                         , timestamp         varchar
                                         );
                                    ''',
                                task_group=group_database,
                                dag=dag)

insert_data_task = PostgresOperator(task_id='insert_data_task',
                                    postgres_conn_id='postgres', # conexão criado no Airflow
                                    parameters=(
                                            # Expressão Jinja: Os valores serão substituídos em tempo de execução                                    
                                            '{{ ti.xcom_pull(task_ids="get_data_task",key="idtemp") }}',     
                                            '{{ ti.xcom_pull(task_ids="get_data_task",key="powerfactor") }}',     
                                            '{{ ti.xcom_pull(task_ids="get_data_task",key="hydraulicpressure") }}',     
                                            '{{ ti.xcom_pull(task_ids="get_data_task",key="temperature") }}',     
                                            '{{ ti.xcom_pull(task_ids="get_data_task",key="timestamp") }}'                                                                               
                                           ),
                                    sql = '''INSERT INTO sensors (  idtemp 
                                                                  , powerfactor
                                                                  , hydraulicpressure
                                                                  , temperature
                                                                  , timestamp
                                                                  )
                                                          VALUES (  %s
                                                                  , %s
                                                                  , %s
                                                                  , %s
                                                                  , %s
                                                                  ); 
                                          ''', # Os parâmetros %s precisam estar na mesma ordem dos campos da tabela sensors.
                                    task_group = group_database,
                                    dag=dag
                                    )




task_generates_data = PythonOperator(task_id='task_generates_data', python_callable=gera_dados, dag=dag)




send_email_alert_task = EmailOperator(
                                task_id='send_email_alert_task',
                                to='xxxx.xxxxx@gmail.com',
                                subject='Pipeline Airlfow',
                                html_content = '''<h3>Alerta de Temperatrura. </h3>
                                <p> Dag: Turbina de Vento </p>
                                ''',
                                task_group=group_check_temp,
                                dag=dag)

send_email_normal_task = EmailOperator(
                                task_id='send_email_normal_task',
                                to='xxxx.xxxxx.com',
                                subject='Pipeline Airlfow',
                                html_content = '''<h3>Temperaturas Normais. </h3>
                                <p> Dag: Turbina de Vento </p>
                                ''',
                                task_group=group_check_temp,
                                dag=dag)


# Definindo a precedência das Tasks dentro dos Grupos:
with group_check_temp:
    check_temp_branc_task >> [send_email_alert_task, send_email_normal_task]

'''
with group_database:
       create_table_task >> insert_data_task
'''

# Definindo a precedência das Tasks:
task_generates_data >> file_sensor_task 
file_sensor_task >> get_data_task
get_data_task >> group_check_temp
get_data_task >> group_database

