<div style="text-align:center">
  <p style="font-size: 30px"> PIPELINE DE DADOS COM APACHE AIRFLOW </p>
  <p style="font-size: 30px"> ESCOPO DO PROJETO </p>
</div>


### Pré Requisitos:
```sh

 1º Instalar o Docker
 2º Criar um container com a imagem do Apache Airflow e um instância de banco de dados Postgres.

 3º No Apache Airflow
      3.1 Criar uma variável de conexão para o operador file_sensor_task.
      3.2 Criar uma variável com o caminho do arquivo de origem na máquina host.
      Template:
        Connection id: df_default
        Connection Type: File(path) 
        Host: /home/user/ed/APP/data/data_turbine.json
```


### Esse projeto consiste na criação de uma turbina eólica: 
```sh
Com um operador (PythonOperator) criar um processo para gerar dados simulados de uma turbina eólica, e pesistir esses dados em um diretório na máquina host  
Ex.: /home/user/ed/APP/data/

```
### Criar Sensor: 
```sh
O operador (FileSensor) deve monitorar a existência do arquivo data_turbine.json antes de prosseguir com outras tarefas.

 Esse operador deve possuir duas propriedades:

  filepath: 
    # Verifica se o arquivo existe antes de prosseguir.

  fs_conn_id:
    # Conexão com o arquivo através da conexão do Airflow. Conexão padrão fs_default.

```

### Ler Dados: 
```sh
Criar um operador (PythonOperator) para ler os dados no diretório (/home/user/ed/APP/data/data_turbine.json), e após o sensor  informar a existência dos dados, deve separar as variáveis e colocá-las em objetos xcom para ser compartilhado com o resto do pipeline.
O (PythonOperator) deve chamar dois grupos em paralelo: "group_check_temp e group_database" .

 O GROUP CHECK TEMP deve disparar um (e-mail de alerta) quando a temperatura da turbina for maior ou igual a 24 graus, ou um (e-mail informativo) em caso de temperatura menor que 24 graus.

 O GROUP DATABASE deve criar uma tabela (sensors) e persistir os dados nessa tabela.
```

### Decisão do PythonOperator: 
```sh
  O operador PythonOperator deve chamar dois grupos em paralelo.

    O BranchPythonOperator vai verificar o valor da temperatura do sensor, quando a temperatura for >=24 graus vai enviar um e-mail crítico de emergência.
    Quando a temperatura for <24 será enviado um e-mail informativo apenas.


  BranchPythonOperator:
    EmailOperator - E-mail de Emergência
    EmailOperator - E-mail Informativo

  Banco de dados:
    PostgresOperator - Criar Tabela em uma instância do Postgres
    PostgresOperator - Inserir dados no Postgres
```
 






    
    







 




