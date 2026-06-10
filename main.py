import pandas as pd


# 1. LEITURA DOS DADOS BRUTOS
df_vendas = pd.read_csv("vendas_tech.csv", encoding='utf-8', low_memory=False)

# mantenha a linha abaixo. Caso contrário, pode removê-la.
df_loja = pd.read_excel("gerentes_lojas.xlsx")


# 2. HIGIENIZAÇÃO E TRATAMENTO DOS DADOS (ETL)

# Cria uma cópia real na memória para evitar o SettingWithCopyWarning
df_analise = df_vendas.copy()

# Exclui colunas desnecessárias
df_analise = df_analise.drop(columns=["Data_Base"], errors='ignore')

# Converte a coluna Data para Datetime antes do tratamento de texto
df_analise["Data"] = pd.to_datetime(df_analise["Data"], format="%Y-%m-%d")

# Preenche valores vazios na Loja conforme o contexto comercial
df_analise["Loja"] = df_analise["Loja"].fillna("Online")

# Exclui espaços vazios nas extremidades dos campos de texto
colunas_texto = ["Loja", "Produto", "Cliente"]
df_analise[colunas_texto] = df_analise[colunas_texto].map(lambda x: x.strip() if isinstance(x, str) else x)

# Padronização de escrita (Garante letras maiúsculas e corrige o "de" do Rio)
df_analise["Loja"] = df_analise["Loja"].str.title().str.replace(" De ", " de ")
df_analise["Produto"] = df_analise["Produto"].str.title()

# Remove duplicatas de IDs de pedidos
df_analise = df_analise.drop_duplicates(subset=["ID_Pedido"])

# Cria coluna do faturamento bruto por item do pedido
df_analise["Faturamento"] = df_analise["Preco_Unitario"] * df_analise["Qtd"]

#Cria coluna de Mes-Ano
df_analise["Mes-Ano"]=df_analise["Data"].dt.strftime("%Y-%m")

#Criando a coluna de dia da semana e atribuindo o valor correto em cada data
mapeamento_dias = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}

df_analise["Dia_Semana"]=df_analise["Data"].dt.day_name().map(mapeamento_dias)


#EXPORTANDO A BASE DE DADOS
df_analise.to_csv("vendas_tech_limpo.csv", index=False)
