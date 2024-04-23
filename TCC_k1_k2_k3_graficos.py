import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, date
import os
import glob
from scipy.interpolate import make_interp_spline, BSpline, CubicSpline # pra suavizar as linhas

# ----------------------------------------------------- Lendo os arquivos excel ----------------------------------------------------

# Selecionando todos os arquivos de vazao mensais
arquivos = glob.glob('dados mensais\\vazao_*.xlsx')

# Lista para armazenar os DataFrames de cada arquivo
dataframes = []

# Lendo cada arquivo em um DataFrame e adicionando à lista
for arquivo in arquivos:
    df = pd.read_excel(arquivo)
    dataframes.append(df)

# Concatenar os DataFrames em um único DataFrame
dados = pd.concat(dataframes)

# Tirando a hora "00:00:00" padrão python das datas 
dados['data'] = pd.to_datetime(dados['data']).dt.date

# Excluindo duas colunas sem dados que estão aparecendo no dataframe
dados = dados.drop(dados.columns[[3, 4]], axis=1)

# Substituindo as vazões de 0 por NaN
dados['vazão (L/s)'] = dados['vazão (L/s)'].replace(0, np.nan)

# Adicionando a coluna "dia_da_semana" às planilhas 
dados['dia_da_semana'] = pd.to_datetime(dados['data']).dt.day_name()

# Organizando a ordem das colunas
dados = dados[['data', 'dia_da_semana', 'hora', 'vazão (L/s)']]

#print("dados: \n", dados)

# --------------------------------------------------------------------- K1-------------------------------------------------------------


# Parâmetro x * desvio padrão pra determinar o intervalo trabalhado
desv = 1.5

# Calculando a média e o desvio padrão pra cada data
media_por_data = dados.groupby('data')['vazão (L/s)'].mean()
desvio_padrao_por_data = dados.groupby('data')['vazão (L/s)'].std()

#print("\n dados: \n",dados)

# Definindo os limites com os outliers sendo +-desv * desvio + média
limite_superior_por_data = media_por_data + desv * desvio_padrao_por_data
limite_inferior_por_data = media_por_data - desv * desvio_padrao_por_data

# GRÁFICO DOS DADOS ANTES DA FILTRAGEM


# # Plotando os dados de vazão ao longo do tempo
# plt.figure(figsize=(10, 10))

# # Plotando os limites superior e inferior do desvio padrão em relação à média por data
# plt.plot(media_por_data.index, media_por_data.values, color='red', label='Média por Data')
# plt.plot(limite_superior_por_data.index, limite_superior_por_data.values, color='green', label='Limite Superior')
# plt.plot(limite_inferior_por_data.index, limite_inferior_por_data.values, color='green', label='Limite Inferior')

# # Plotando os dados de vazão
# plt.scatter(dados['data'], dados['vazão (L/s)'], label='Vazão', color='blue', alpha=0.5, s=0.5)


# # Adicionando título e rótulos dos eixos
# plt.title('Vazão ao longo do tempo com Média e Desvio Padrão por Data')
# plt.xlabel('Data')
# plt.ylabel('Vazão (L/s)')

# # Adicionando legenda
# plt.legend()

# # Rotacionando os rótulos do eixo x para facilitar a leitura
# plt.xticks(rotation=45)

# # Exibindo o gráfico
# plt.grid(True)
# plt.tight_layout()
# plt.show()




# Aplicando esses limites para filtrar os dados correspondentes para cada data
dados_filtrados_por_data = {}

for data in dados['data'].unique():
    dados_data = dados[dados['data'] == data]
    filtro_superior_data = dados_data['vazão (L/s)'] <= limite_superior_por_data[data]
    filtro_inferior_data = dados_data['vazão (L/s)'] >= limite_inferior_por_data[data]
    dados_filtrados_por_data[data] = dados_data[filtro_superior_data & filtro_inferior_data]

# print("\n dados iniciais filtrados por data\n",dados_filtrados_por_data)

# Criando um DataFrame para armazenar as médias de vazão por data (VAZÕES MÉDIAS DIÁRIAS)
vazao_media_por_data_df = pd.DataFrame(columns=['data', 'vazão (L/s)'])

# Iterando sobre os dados filtrados para cada data
for data, dados_filtrados_data in dados_filtrados_por_data.items():
    vazao_media_data = dados_filtrados_data['vazão (L/s)'].mean()
    # Adicionando a média de vazão para a data atual ao DataFrame
   # vazao_media_por_data_df = vazao_media_por_data_df.append({'data': data, 'vazão (L/s)': vazao_media_data}, ignore_index=True)
    vazao_media_por_data_df = pd.concat([vazao_media_por_data_df, pd.DataFrame({'data': [data], 'vazão (L/s)': [vazao_media_data]})], ignore_index=True)

#print("\n Vazoes medias por data \n", vazao_media_por_data_df)

# Encontrando a vazão MÉDIA após filtragem (MÉDIA DAS MÉDIAS DIÁRIAS)
Qmedia_filtrada_data = vazao_media_por_data_df['vazão (L/s)'].mean()
print("\n vazao media filtrada por data", Qmedia_filtrada_data)

# Encontrando a vazão MÁXIMA após filtragem
Qmax_k1 = vazao_media_por_data_df['vazão (L/s)'].max()
print("\n Qmax k1: \n", Qmax_k1)

# k1
k1 = Qmax_k1/Qmedia_filtrada_data
print("\n k1: ", k1)


# -------------------------------------------------------------- GRÁFICO K1

# Plotando os dados de vazão ao longo do tempo
plt.figure(figsize=(10, 10))
x = vazao_media_por_data_df['data']
y = vazao_media_por_data_df['vazão (L/s)']

# plt.rcParams['xtick.labelsize'] = 16
# plt.rcParams['ytick.labelsize'] = 16

plt.plot(x, y, label='Vazão', color='blue')

# Plotando a linha da vazão média
plt.axhline(y=Qmedia_filtrada_data, color='red', linestyle='--', label='Vazão Média')

# Obtendo a data correspondente a vazao maxima
data_vazao_max = vazao_media_por_data_df.loc[vazao_media_por_data_df['vazão (L/s)'].idxmax(), 'data']
print("\n data da vazao maxima anual (pra k1): ", data_vazao_max)

# Plotar o ponto de vazão máxima
plt.scatter(data_vazao_max, Qmax_k1, color='red', label='Vazão máxima')

# Adicionando título e rótulos dos eixos
plt.title('Variação do consumo ao longo de 12 meses (k1)')
plt.xlabel('Data', fontsize = 18)
plt.ylabel('Vazão (L/s)', fontsize = 18)

# Adicionando legenda
plt.legend()

# Rotacionando os rótulos do eixo x para facilitar a leitura
plt.xticks(rotation=45)

# Exibindo o gráfico
plt.grid(True)
plt.tight_layout()
plt.show()

# -------------------------------------------------------------- k2 -------------------------------------------------------------------

# Calculando a média e o desvio padrão pra cada horário
media_por_horario = dados.groupby('hora')['vazão (L/s)'].mean()
desvio_padrao_por_horario = dados.groupby('hora')['vazão (L/s)'].std()

# Definindo os limites com os outliers sendo +-desv * desvio + média
limite_superior_por_horario = media_por_horario + desv * desvio_padrao_por_horario
limite_inferior_por_horario = media_por_horario - desv * desvio_padrao_por_horario


# GRÁFICO DOS DADOS ANTES DA FILTRAGEM


# # Plotando os dados de vazão ao longo do tempo
# plt.figure(figsize=(10, 10))

# # Plotando os limites superior e inferior do desvio padrão em relação à média por horário
# plt.plot(media_por_horario.index.astype(str), media_por_horario.values, color='red', label='Média por Horário')
# plt.plot(limite_superior_por_horario.index.astype(str), limite_superior_por_horario.values, color='green', label='Limite Superior')
# plt.plot(limite_inferior_por_horario.index.astype(str), limite_inferior_por_horario.values, color='green', label='Limite Inferior')

# # Convertendo os valores da coluna 'hora' para strings
# dados['hora'] = dados['hora'].astype(str)

# # Plotando os dados de vazão
# plt.scatter(dados['hora'], dados['vazão (L/s)'], label='Vazão', color='blue', alpha=0.5, s=2)  # Defina o tamanho dos pontos ajustando o valor de 's'

# # Adicionando título e rótulos dos eixos
# plt.title('Vazão ao longo do tempo com Média e Desvio Padrão por Horário')
# plt.xlabel('Hora')
# plt.ylabel('Vazão (L/s)')

# # Adicionando legenda
# plt.legend()

# # Rotacionando os rótulos do eixo x para facilitar a leitura
# plt.xticks(rotation=90)

# # Exibindo o gráfico
# plt.grid(True)
# plt.tight_layout()
# plt.show()



# Aplicando esses limites para filtrar os dados correspondentes para cada horário
dados_filtrados_por_horario = {}

for horario in dados['hora'].unique():
    dados_horario = dados[dados['hora'] == horario]
    filtro_superior = dados_horario['vazão (L/s)'] <= limite_superior_por_horario[horario]
    filtro_inferior = dados_horario['vazão (L/s)'] >= limite_inferior_por_horario[horario]
    dados_filtrados_por_horario[horario] = dados_horario[filtro_superior & filtro_inferior]

#print("\n dados completos depois do filtro: \n",dados_filtrados_por_horario)

# Criando um DataFrame para armazenar as médias (filtradas) de vazão por horario
vazao_media_por_horario_df = pd.DataFrame(columns=['hora', 'vazão (L/s)'])

# Iterando sobre os dados filtrados para cada horario
for horario, dados_filtrados_horario in dados_filtrados_por_horario.items():
    vazao_media_horario = dados_filtrados_horario['vazão (L/s)'].mean()
    # Adicionando a média de vazão para a data atual ao DataFrame
    vazao_media_por_horario_df = pd.concat([vazao_media_por_horario_df, pd.DataFrame({'hora': [horario], 'vazão (L/s)': [vazao_media_horario]})], ignore_index=True)

#print("\n vazao media por horario: \n",vazao_media_por_horario_df)

# Encontrando a vazão MÉDIA após filtragem
Qmedia_filtrada_horario = vazao_media_por_horario_df['vazão (L/s)'].mean()
#print("\n Qmedia filtrada horario", Qmedia_filtrada_horario)

# Encontrando a vazão MÁXIMA após filtragem
Qmax_k2 = vazao_media_por_horario_df['vazão (L/s)'].max()
print("\n Qmax k2: \n", Qmax_k2)

# k2
k2 = Qmax_k2/Qmedia_filtrada_horario
print("\n k2: ", k2)


# ---------------------------------------------------- k3 ----------------------------------------------------

# Encontrando a vazão MÍNIMA após filtragem
Qmin_k3 = vazao_media_por_horario_df['vazão (L/s)'].min()
print("\n qmin k3: \n", Qmin_k3)

# Valor de k3
k3 = Qmin_k3/Qmedia_filtrada_horario
print("\n k3: ", k3)


# -------------------------------------------------------------- GRÁFICO k2 e k3

# Plotando os dados de vazão ao longo do tempo
plt.figure(figsize=(14, 6))

# Converter a lista em uma série do pandas
#vazao_media_por_horario_series = pd.Series(vazao_media_por_horario.df)

# Plotar os dados de vazão ao longo do tempo
x = vazao_media_por_horario_df['hora'].astype(str)
y = vazao_media_por_horario_df['vazão (L/s)']
plt.plot(x, y, label='Vazão', color='blue')

# Plotando a linha da vazão média
plt.axhline(y=Qmedia_filtrada_horario, color='red', linestyle='--', label='Vazão Média')

# Obtendo a hora correspondente a VAZÃO MAXIMA
#linha_vazao_max = vazao_media_por_horario_df[vazao_media_por_horario_df == Qmax_k2]
hora_vazao_max = vazao_media_por_horario_df.loc[vazao_media_por_horario_df['vazão (L/s)'].idxmax(), 'hora']
print("\n hora da vazao maxima diaria (para k2): ", hora_vazao_max)
# Plotar o ponto de vazão máxima
plt.scatter(str(hora_vazao_max), Qmax_k2, color='red', label='Vazão máxima')


# Obtendo a data correspondente a VAZÃO MINIMA
#linha_vazao_min = vazao_media_por_horario_df[vazao_media_por_horario_df == Qmin_k3]
hora_vazao_min = vazao_media_por_horario_df.loc[vazao_media_por_horario_df['vazão (L/s)'].idxmin(), 'hora']
print("\n hora da vazao minima diaria (para k3): ", hora_vazao_min)
# Plotar o ponto de vazão mínima
plt.scatter(str(hora_vazao_min), Qmin_k3, color='green', label='Vazão mínima')

# Adicionando título e rótulos dos eixos
plt.title('Variação do consumo ao longo de 1 dia (k2 e k3)')
plt.xlabel('Hora do dia', fontsize = 18)
plt.ylabel('Vazão (L/s)', fontsize = 18)

# Adicionando legenda
plt.legend()

# Rotacionando os rótulos do eixo x para facilitar a leitura
plt.xticks(rotation=90)

# Exibindo o gráfico
plt.grid(True)
plt.tight_layout()
plt.show()


#Análise do consumo diário pelo dia da semana

# SEGUNDA ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para as segundas-feiras
dados_segundas = dados[dados['dia_da_semana'] == 'Monday']

#print(dados_segundas)

# criando um dataframe pra salvar os dados
vazao_por_hora_seg = []

# Salvando os valores por hora
for horario in dados_segundas['hora'].unique():
    df = dados_segundas[dados_segundas['hora'] == horario]
    vazao_por_hora_seg.append(df)

dados_segundas_por_hora = pd.concat(vazao_por_hora_seg)

#print("\n dados segundas por hora: \n", dados_segundas_por_hora)

# Média por horario
media_horaria_seg = dados_segundas.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria seg: \n",media_horaria_seg)

# Desvio padrão opr horário
desvio_horario_seg = dados_segundas.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario seg: \n",desvio_horario_seg)

# Determinando os limites
lim_inf_seg = media_horaria_seg - desv * desvio_horario_seg
lim_sup_seg = media_horaria_seg + desv * desvio_horario_seg

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_seg = []

for horario in dados_segundas_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_segundas_por_hora[dados_segundas_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_seg[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_seg[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_seg.append(dados_horario[filtro_limite])

dados_filtrados_seg_concat = pd.concat(dados_filtrados_seg)
#print("\n dados filtrados seg: \n", dados_filtrados_seg)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_seg = dados_filtrados_seg_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
print("\n Segunda: \n",Qmed_hor_seg)


# TERÇA ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para as terças-feiras
dados_terças = dados[dados['dia_da_semana'] == 'Tuesday']

#print(dados_terças)

# criando um dataframe pra salvar os dados
vazao_por_hora_ter = []

# Salvando os valores por hora
for horario in dados_terças['hora'].unique():
    df = dados_terças[dados_terças['hora'] == horario]
    vazao_por_hora_ter.append(df)

dados_terça_por_hora = pd.concat(vazao_por_hora_ter)

#print("\n dados terça por hora: \n", dados_terça_por_hora)

# Média por horario
media_horaria_ter = dados_terças.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria ter: \n",media_horaria_ter)

# Desvio padrão por horário
desvio_horario_ter = dados_terças.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario ter: \n",desvio_horario_ter)

# Determinando os limites
lim_inf_ter = media_horaria_ter - desv * desvio_horario_ter
lim_sup_ter = media_horaria_ter + desv * desvio_horario_ter

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_ter = []

for horario in dados_terça_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_terça_por_hora[dados_terça_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_ter[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_ter[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_ter.append(dados_horario[filtro_limite])

dados_filtrados_ter_concat = pd.concat(dados_filtrados_ter)
#print("\n dados filtrados ter: \n", dados_filtrados_ter)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_ter = dados_filtrados_ter_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
#print("\n Qmed hor ter: \n",Qmed_hor_ter)


# QUARTA ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para as quartas-feiras
dados_quartas = dados[dados['dia_da_semana'] == 'Wednesday']

#print(dados_quartas)

# criando um dataframe pra salvar os dados
vazao_por_hora_qua = []

# Salvando os valores por hora
for horario in dados_quartas['hora'].unique():
    df = dados_quartas[dados_quartas['hora'] == horario]
    vazao_por_hora_qua.append(df)

dados_quarta_por_hora = pd.concat(vazao_por_hora_qua)

#print("\n dados quarta por hora: \n", dados_quarta_por_hora)

# Média por horario
media_horaria_qua = dados_quartas.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria qua: \n",media_horaria_qua)

# Desvio padrão por horário
desvio_horario_qua = dados_quartas.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario qua: \n",desvio_horario_qua)

# Determinando os limites
lim_inf_qua = media_horaria_qua - desv * desvio_horario_qua
lim_sup_qua = media_horaria_qua + desv * desvio_horario_qua

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_qua = []

for horario in dados_quarta_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_quarta_por_hora[dados_quarta_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_qua[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_qua[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_qua.append(dados_horario[filtro_limite])

dados_filtrados_qua_concat = pd.concat(dados_filtrados_qua)
#print("\n dados filtrados ter: \n", dados_filtrados_qua)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_qua = dados_filtrados_qua_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
print("\n Qmed hor qua: \n",Qmed_hor_qua)


# QUINTA ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para as quintas-feiras
dados_quintas = dados[dados['dia_da_semana'] == 'Thursday']

#print(dados_quintas)

# criando um dataframe pra salvar os dados
vazao_por_hora_qui = []

# Salvando os valores por hora
for horario in dados_quintas['hora'].unique():
    df = dados_quintas[dados_quintas['hora'] == horario]
    vazao_por_hora_qui.append(df)

dados_quinta_por_hora = pd.concat(vazao_por_hora_qui)

#print("\n dados quinta por hora: \n", dados_quinta_por_hora)

# Média por horario
media_horaria_qui = dados_quintas.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria qui: \n",media_horaria_qui)

# Desvio padrão por horário
desvio_horario_qui = dados_quintas.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario qui: \n",desvio_horario_qui)

# Determinando os limites
lim_inf_qui = media_horaria_qui - desv * desvio_horario_qui
lim_sup_qui = media_horaria_qui + desv * desvio_horario_qui

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_qui = []

for horario in dados_quinta_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_quinta_por_hora[dados_quinta_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_qui[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_qui[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_qui.append(dados_horario[filtro_limite])

dados_filtrados_qui_concat = pd.concat(dados_filtrados_qui)
#print("\n dados filtrados qui: \n", dados_filtrados_qui)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_qui = dados_filtrados_qui_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
#print("\n Qmed hor qui: \n",Qmed_hor_qui)

# SEXTA ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para as sextas-feiras
dados_sextas = dados[dados['dia_da_semana'] == 'Friday']

#print(dados_sextas)

# criando um dataframe pra salvar os dados
vazao_por_hora_sex = []

# Salvando os valores por hora
for horario in dados_sextas['hora'].unique():
    df = dados_sextas[dados_sextas['hora'] == horario]
    vazao_por_hora_sex.append(df)

dados_sexta_por_hora = pd.concat(vazao_por_hora_sex)

#print("\n dados sexta por hora: \n", dados_sexta_por_hora)

# Média por horario
media_horaria_sex = dados_sextas.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria sex: \n",media_horaria_sex)

# Desvio padrão por horário
desvio_horario_sex = dados_sextas.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario sex: \n",desvio_horario_sex)

# Determinando os limites
lim_inf_sex = media_horaria_sex - desv * desvio_horario_sex
lim_sup_sex = media_horaria_sex + desv * desvio_horario_sex

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_sex = []

for horario in dados_sexta_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_sexta_por_hora[dados_sexta_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_sex[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_sex[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_sex.append(dados_horario[filtro_limite])

dados_filtrados_sex_concat = pd.concat(dados_filtrados_sex)
#print("\n dados filtrados sex: \n", dados_filtrados_sex)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_sex = dados_filtrados_sex_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
#print("\n Qmed hor sex: \n",Qmed_hor_sex)


# SÁBADO ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para os sabados
dados_sabados = dados[dados['dia_da_semana'] == 'Saturday']

#print(dados_sab)

# criando um dataframe pra salvar os dados
vazao_por_hora_sab = []

# Salvando os valores por hora
for horario in dados_sabados['hora'].unique():
    df = dados_sabados[dados_sabados['hora'] == horario]
    vazao_por_hora_sab.append(df)

dados_sabado_por_hora = pd.concat(vazao_por_hora_sab)

#print("\n dados sabado por hora: \n", dados_sabado_por_hora)

# Média por horario
media_horaria_sab = dados_sabados.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria sab: \n",media_horaria_sab)

# Desvio padrão por horário
desvio_horario_sab = dados_sabados.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario sab: \n",desvio_horario_sab)

# Determinando os limites
lim_inf_sab = media_horaria_sab - desv * desvio_horario_sab
lim_sup_sab = media_horaria_sab + desv * desvio_horario_sab

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_sab = []

for horario in dados_sabado_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_sabado_por_hora[dados_sabado_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_sab[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_sab[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_sab.append(dados_horario[filtro_limite])

dados_filtrados_sab_concat = pd.concat(dados_filtrados_sab)
#print("\n dados filtrados sab: \n", dados_filtrados_sab)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_sab = dados_filtrados_sab_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
#print("\n Qmed hor sab: \n",Qmed_hor_sab)


# DOMINGO ------------------------------------------------------------------------------------------------------------------------------

# Filtrando os dados para os sabados
dados_dom = dados[dados['dia_da_semana'] == 'Sunday']

#print(dados_dom)

# criando um dataframe pra salvar os dados
vazao_por_hora_dom = []

# Salvando os valores por hora
for horario in dados_dom['hora'].unique():
    df = dados_dom[dados_dom['hora'] == horario]
    vazao_por_hora_dom.append(df)

dados_dom_por_hora = pd.concat(vazao_por_hora_dom)

#print("\n dados domingo por hora: \n", dados_dom_por_hora)

# Média por horario
media_horaria_dom = dados_dom.groupby('hora')['vazão (L/s)'].mean()

#print("\n media horaria dom: \n",media_horaria_dom)

# Desvio padrão por horário
desvio_horario_dom = dados_dom.groupby('hora')['vazão (L/s)'].std()

#print("\n desvio horario dom: \n",desvio_horario_dom)

# Determinando os limites
lim_inf_dom = media_horaria_dom - desv * desvio_horario_dom
lim_sup_dom = media_horaria_dom + desv * desvio_horario_dom

# criando um dataframe pra salvar os dados filtrados
dados_filtrados_dom = []

for horario in dados_dom_por_hora['hora'].unique():
    # Filtrar os dados para o horário atual
    dados_horario = dados_dom_por_hora[dados_dom_por_hora['hora'] == horario]
    # Verificar se a vazão está dentro do intervalo entre os limites
    filtro_limite = (dados_horario['vazão (L/s)'] >= lim_inf_dom[horario]) & (dados_horario['vazão (L/s)'] <= lim_sup_dom[horario])
    # Se a vazão estiver dentro do intervalo, salvar os dados dessa linha
    dados_filtrados_dom.append(dados_horario[filtro_limite])

dados_filtrados_dom_concat = pd.concat(dados_filtrados_dom)
#print("\n dados filtrados dom: \n", dados_filtrados_dom)

# Pra cada hora igual, retornar uma media das vazoes correspondentes
Qmed_hor_dom = dados_filtrados_dom_concat.groupby('hora')['vazão (L/s)'].mean()

# Exibir a média das vazões correspondentes para cada hora
#print("\n Qmed hor dom: \n",Qmed_hor_dom)

# ------------------------------------------------------------- Curvas

# Dados das médias de vazões por hora para cada dia da semana
medias_por_dia_da_semana = {
    'Segunda': Qmed_hor_seg,
    'Terça': Qmed_hor_ter,
    'Quarta': Qmed_hor_qua,
    'Quinta': Qmed_hor_qui,
    'Sexta': Qmed_hor_sex,
    'Sábado': Qmed_hor_sab,
    'Domingo': Qmed_hor_dom
}

# Configurações do gráfico
plt.figure(figsize=(14, 6))  # Tamanho do gráfico

# Plotar as curvas de média das vazões por hora para cada dia da semana
for dia, medias in medias_por_dia_da_semana.items():
    # Converter os índices (datas) em strings
    datas_str = [str(data) for data in medias.index]
    plt.plot(datas_str, medias.values, label=dia)

# Adicionar rótulos aos eixos
plt.xlabel('Hora do dia', fontsize = 18)
plt.ylabel('Vazão média (L/s)', fontsize = 18)

# Adicionar um título ao gráfico
plt.title('Consumo médio diário ao longo dos dias da semana')

plt.grid(True)

# Rotacionar as informações do eixo x para melhor visualização
plt.xticks(rotation=90)

# Adicionar uma legenda
plt.legend()

# Mostrar o gráfico
plt.tight_layout()  # Ajustar layout para evitar sobreposição de legendas
plt.show()

