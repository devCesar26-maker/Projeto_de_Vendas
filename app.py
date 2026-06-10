import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# CONFIGURAÇÃO DE DESIGN E TEMA RESPONSIVO

st.set_page_config(
    page_title="Dashboard Executivo Premium",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para corrigir títulos, sidebar e KPIs em qualquer tema
st.markdown("""
    <style>
    /* Fundo principal */
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Força títulos e subtítulos a manterem cor fixa em qualquer tema */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #1e293b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }

    /* Ajuste para título principal */
    .stApp h1 { 
        font-size: calc(1.8rem + 1vw) !important; 
        font-weight: 700 !important;
        margin-top: 5px !important;
        padding-top: 0px !important;
    }

    /* Ajuste para subtítulos (gráficos) */
    .stApp h3 { 
        font-size: calc(1.25rem + 0.4vw) !important; 
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Labels da sidebar legíveis em qualquer tema */
    section[data-testid="stSidebar"] label p {
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }

    /* Grid Responsivo para KPIs */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 1.2rem !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        width: 100% !important;
    }

    /* Labels dos KPIs */
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: calc(0.85rem + 0.1vw) !important;
        letter-spacing: 0.05em;
    }

    /* Valores dos KPIs */
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] > div {
        color: #0f172a !important;
        font-size: calc(1.25rem + 0.3vw) !important;
        font-weight: 700 !important;
        margin-top: 4px;
    }

    /* Contêineres dos gráficos */
    .element-container, .stPlotlyChart {
        width: 100% !important;
    }

    .block-container {
        padding: 2rem 4vw !important;
    }

    hr {
        margin: 1.2rem 0 !important;
        border-color: #e2e8f0 !important;
    }

    /* Remove botão de collapse da sidebar */
    button[data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Paleta de Cores Corporativa Light
COR_BARRA_PROD    = "#2563eb"
COR_LINHA_PARETO  = "#f43f5e"
COR_BARRA_FILIAL  = "#10b981"
COR_TEXTO_TM      = "#2563eb"
COR_GRID          = "#f1f5f9"
COR_TEXTO_EIXO    = "#475569"

st.title("Painel Executivo")
st.markdown("---")

# 1. CARREGAMENTO DOS DADOS
@st.cache_data
def carregar_dados_base(base):
    return pd.read_csv(base)

df_base = carregar_dados_base("vendas_tech_limpo.csv")


# 2. PAINEL DE FILTROS INTERATIVOS (BARRA LATERAL)
st.sidebar.markdown("Filtros do Painel")

# 1. Filtro de Lojas
lista_lojas = sorted(list(df_base["Loja"].unique()))
loja_selecionada = st.sidebar.multiselect(
    "Filial / Loja:", 
    options=lista_lojas, 
    placeholder="Todas as Filiais"
)

# 2. Filtro de Produtos
lista_produtos = sorted(list(df_base["Produto"].unique()))
produto_selecionado = st.sidebar.multiselect(
    "Produto:", 
    options=lista_produtos, 
    placeholder="Todos os Produtos"
)

# 3. Filtro de Mês (Puxando direto da coluna Mes-Ano da base principal)
lista_mes = sorted(list(df_base["Mes-Ano"].unique()))
mes_selecionado = st.sidebar.multiselect(
    "Mês:", 
    options=lista_mes, 
    placeholder="Todos os meses"
)

# Lógica de Filtragem Dinâmica Cruzada
df_filtrado = df_base.copy()

if loja_selecionada:
    df_filtrado = df_filtrado[df_filtrado["Loja"].isin(loja_selecionada)]

if produto_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Produto"].isin(produto_selecionado)]

if mes_selecionado:
    df_filtrado = df_filtrado[df_filtrado["Mes-Ano"].isin(mes_selecionado)]

# 3. RECALCULO DINÂMICO DOS KPIs (Responsivo para Mobile)
faturamento_total = df_filtrado["Faturamento"].sum()
total_pedidos = df_filtrado["ID_Pedido"].nunique()
ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0

# No celular, st.columns empilha automaticamente para não quebrar a tela
card1, card2, card3 = st.columns([1, 1, 1])
fat_formatado = f"R$ {faturamento_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
pedidos_formatado = f"{int(total_pedidos):,}".replace(",", ".")
ticket_formatado = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

with card1:
    st.metric(label="FATURAMENTO TOTAL", value=fat_formatado)
with card2:
    st.metric(label="TOTAL DE PEDIDOS", value=pedidos_formatado)
with card3:
    st.metric(label="TICKET MÉDIO", value=ticket_formatado)

st.markdown("---")

# 4. PROCESSAMENTO DOS AGRUPAMENTOS

# Agrupamento de Pareto
analise_pareto = df_filtrado.groupby("Produto", observed=False)["Faturamento"].sum().reset_index()
analise_pareto = analise_pareto.sort_values(by="Faturamento", ascending=False).reset_index(drop=True)
analise_pareto["%_Representação"] = (analise_pareto["Faturamento"] / (faturamento_total if faturamento_total > 0 else 1)) * 100
analise_pareto["%_Acumulado"] = analise_pareto["%_Representação"].cumsum()

# Agrupamento de Filiais
analise_filial = df_filtrado.groupby("Loja", observed=False).agg(
    Faturamento_Regional=("Faturamento", "sum"),
    Quantidade_Pedidos=("ID_Pedido", "nunique")
).reset_index()
analise_filial["Ticket_Medio_Regional"] = analise_filial["Faturamento_Regional"] / analise_filial["Quantidade_Pedidos"]
analise_filial = analise_filial.sort_values(by="Faturamento_Regional", ascending=True).reset_index(drop=True)

# Agrupamento Mensal
analise_mensal = df_filtrado.groupby("Mes-Ano", observed=False)["Faturamento"].sum().reset_index()
analise_mensal = analise_mensal.sort_values(by="Mes-Ano").reset_index(drop=True)

# Agrupamento Semanal
ordem_dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
analise_semanal = df_filtrado.groupby("Dia_Semana", observed=False)["Faturamento"].sum().reset_index()
analise_semanal['Dia_Semana'] = pd.Categorical(analise_semanal['Dia_Semana'], categories=ordem_dias, ordered=True)
analise_semanal = analise_semanal.sort_values(by="Dia_Semana", ascending=False).reset_index(drop=True)


# 5. SEÇÃO DE GRÁFICOS INTERATIVOS 100% RESPONSIVOS (FONTE AUMENTADA)

# GRÁFICO 1: Curva de Pareto por Produto
st.subheader("Distribuição de Faturamento por Produto")

fig_pareto = go.Figure()
fig_pareto.add_trace(go.Bar(
    x=analise_pareto["Produto"], y=analise_pareto["Faturamento"],
    name="Faturamento", marker=dict(color=COR_BARRA_PROD, line=dict(width=0)),
    hovertemplate="<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>"
))
fig_pareto.add_trace(go.Scatter(
    x=analise_pareto["Produto"], y=analise_pareto["%_Acumulado"],
    name="% Acumulado", yaxis="y2", mode="lines+markers",
    line=dict(color=COR_LINHA_PARETO, width=3),
    marker=dict(size=8, color="#ffffff", line=dict(width=2, color=COR_LINHA_PARETO)),
    hovertemplate="<b>%{x}</b><br>Acumulado: %{y:.2f}%<extra></extra>"
))

fig_pareto.update_layout(
    template="plotly_white", showlegend=False, autosize=True, height=380,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff", margin=dict(l=10, r=10, t=14, b=50),
    yaxis=dict(
        title="Faturamento (R$)",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        tickformat="$,.0f",
        gridcolor=COR_GRID,
        tickfont=dict(size=11, color=COR_TEXTO_EIXO)
    ),
    yaxis2=dict(
        title="% Acumulado",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        overlaying="y", side="right", range=[0, 105], ticksuffix="%",
        showgrid=False,
        tickfont=dict(size=11, color=COR_TEXTO_EIXO)
    )
)
fig_pareto.update_xaxes(tickangle=25, tickfont=dict(size=11, color=COR_TEXTO_EIXO))
st.plotly_chart(fig_pareto, use_container_width=True)

st.markdown("---")

# GRÁFICO 2: Ranking de Filiais
st.subheader("Desempenho por Filial")

fig_lojas = go.Figure()
fig_lojas.add_trace(go.Bar(
    x=analise_filial["Faturamento_Regional"],
    y=analise_filial["Loja"],
    orientation='h',
    name="Faturamento",
    marker=dict(color=COR_BARRA_FILIAL, line=dict(width=0)), 
    hovertemplate="<b>Filial %{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>"
))

anotacoes = []
for index, row in analise_filial.iterrows():
    tm_formatado = f"TM: R$ {row['Ticket_Medio_Regional']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pedidos_num_formatado = f"{int(row['Quantidade_Pedidos']):,}".replace(",", ".")
    texto_rotulo = f" {tm_formatado} | Vol: {pedidos_num_formatado}"
    anotacoes.append(dict(
        x=row["Faturamento_Regional"], y=row["Loja"],
        text=texto_rotulo, xanchor='left', yanchor='middle',
        showarrow=False, font=dict(size=11, color=COR_TEXTO_EIXO), xshift=8
    ))
    
fig_lojas.update_layout(
    template="plotly_white", showlegend=False, annotations=anotacoes, autosize=True, height=420,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff", margin=dict(l=120, r=10, t=14, b=40),
    xaxis=dict(
        title="Faturamento Regional (R$)",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        tickformat="$,.0f",
        gridcolor=COR_GRID,
        tickfont=dict(size=11, color=COR_TEXTO_EIXO),
        autorange=True
    ),
    yaxis=dict(tickfont=dict(size=11, color=COR_TEXTO_EIXO, weight="bold"))
)

st.plotly_chart(fig_lojas, use_container_width=True)

st.markdown("---")

# GRÁFICO 3: Evolução Mensal do Faturamento
st.subheader("Faturamento Mensal")

fig_mensal = go.Figure()
fig_mensal.add_trace(go.Scatter(
    x=analise_mensal["Mes-Ano"],
    y=analise_mensal["Faturamento"],
    mode="lines+markers",
    name="Faturamento Mensal",
    line=dict(color=COR_BARRA_PROD, width=3, shape="spline"),
    marker=dict(size=8, color="#ffffff", line=dict(width=2, color=COR_BARRA_PROD)),
    hovertemplate="<b>Mês: %{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>"
))

fig_mensal.update_layout(
    template="plotly_white", showlegend=False, autosize=True, height=320,
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff", margin=dict(l=10, r=10, t=14, b=50),
    xaxis=dict(
        title="Período (Mês-Ano)",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        tickfont=dict(size=11, color=COR_TEXTO_EIXO),
        gridcolor=COR_GRID
    ),
    yaxis=dict(
        title="Faturamento (R$)",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        tickformat="$,.0f",
        gridcolor=COR_GRID,
        tickfont=dict(size=11, color=COR_TEXTO_EIXO)
    )
)
st.plotly_chart(fig_mensal, use_container_width=True)

st.markdown("---")

#GRÁFICO 4: Faturamento por Dia da Semana
st.subheader("Faturamento por Dia da Semana")

fig_semana = go.Figure()
fig_semana.add_trace(go.Bar(
    x=analise_semanal["Faturamento"],
    y=analise_semanal["Dia_Semana"],
    orientation='h',
    name="Faturamento",
    marker=dict(color=analise_semanal["Faturamento"], colorscale="Blues", line=dict(width=0)),
    hovertemplate="<b>%{y}</b><br>Faturamento Total: R$ %{x:,.2f}<extra></extra>"
))

fig_semana.update_layout(
    template="plotly_white", showlegend=False, autosize=True, height=360, 
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff", margin=dict(l=110, r=10, t=14, b=40),
    xaxis=dict(
        title="Faturamento Acumulado (R$)",
        title_font=dict(size=13, color=COR_TEXTO_EIXO, weight="bold"),
        tickformat="$,.0f",
        gridcolor=COR_GRID,
        tickfont=dict(size=11, color=COR_TEXTO_EIXO)
    ),
    yaxis=dict(tickfont=dict(color=COR_TEXTO_EIXO, size=11, weight="bold"), gridcolor="rgba(0,0,0,0)")
)
st.plotly_chart(fig_semana, use_container_width=True)
