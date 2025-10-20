import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import os

st.title('Linha de Montagem - IANES')
st.write('')

# Caminho do CSV
vazio = "dados.csv"

# Session_state
if 'DF' not in st.session_state:
    if os.path.exists(vazio):
        st.session_state.DF = pd.read_csv(vazio)
    else:
        st.session_state.DF = pd.DataFrame(columns=['Data', 'Máquina', 'Turno', 'Peças Produzidas', 'Peças Defeituosas'])

DF = st.session_state.DF

# Colunas de botões
col1, col2, col3, col4, col5 = st.columns(5)

# Registros
if col1.button('Novos Registros'):
    with st.form('Dados de Produção', clear_on_submit=True):
        st.subheader('- Dados de Produção -')
        c1, c2, c3, c4 = st.columns(4)
        D = c1.date_input('Data:')
        M = c2.text_input('Máquina:')
        T = c3.selectbox('Turno:', ['Manhã', 'Tarde', 'Noite'])
        c1a, c2a = st.columns(2)
        PP = c1a.text_input('Peças Produzidas:')
        PD = c2a.text_input('Peças Defeituosas:')
        SAV = st.form_submit_button('Salvar')
        
        if SAV:
            try:
                novo = pd.DataFrame([{
                    'Data': str(D),
                    'Máquina': M,
                    'Turno': T,
                    'Peças Produzidas': int(PP),
                    'Peças Defeituosas': int(PD)
                }])
                st.session_state.DF = pd.concat([st.session_state.DF, novo], ignore_index=True)
                st.session_state.DF.to_csv(vazio, index=False)
                st.success('Dados salvos!')
                st.dataframe(st.session_state.DF)
            except ValueError:
                st.error('Preencha todos os campos corretamente!')

# Atualizar ou excluir
if col2.button('Atualizar ou Excluir Dados'):
    df = st.session_state.DF
    st.subheader('Registros atuais')
    st.dataframe(df)

    st.markdown("---")
    st.subheader('Editar ou Excluir Registro por Data')

    if not df.empty:
        datas_salvas = sorted(df['Data'].unique())
        acesso = st.selectbox('Selecione a data do registro:', datas_salvas)
        if acesso:
            filtro = df['Data'] == acesso
            if filtro.any():
                ind = df.index[filtro][0]
                st.write('Registro encontrado:')
                st.write(df.loc[ind])

                # Formulário de edição
                with st.form('Editar Linha', clear_on_submit=False):
                    st.write('Altere os valores abaixo:')
                    c1f, c2f, c3f = st.columns(3)
                    D_new = c1f.text_input('Data:', str(df.at[ind, 'Data']))
                    M_new = c2f.text_input('Máquina:', str(df.at[ind, 'Máquina']))
                    T_new = c3f.selectbox('Turno:', ['Manhã', 'Tarde', 'Noite'],
                                          index=['Manhã', 'Tarde', 'Noite'].index(str(df.at[ind, 'Turno'])))
                    c1f, c2f = st.columns(2)
                    PP_new = c1f.text_input('Peças Produzidas:', str(df.at[ind, 'Peças Produzidas']))
                    PD_new = c2f.text_input('Peças Defeituosas:', str(df.at[ind, 'Peças Defeituosas']))
                    salvar = st.form_submit_button('Salvar Alterações')

                    if salvar:
                        try:
                            df.at[ind, 'Data'] = D_new
                            df.at[ind, 'Máquina'] = M_new
                            df.at[ind, 'Turno'] = T_new
                            df.at[ind, 'Peças Produzidas'] = int(PP_new)
                            df.at[ind, 'Peças Defeituosas'] = int(PD_new)
                            st.session_state.DF = df
                            st.session_state.DF.to_csv(vazio, index=False)
                            st.success('Registro atualizado com sucesso!')
                            st.dataframe(st.session_state.DF)
                        except ValueError:
                            st.error('Preencha todos os campos corretamente!')

                # Excluir
                st.markdown("---")
                if st.button(f'Excluir registro da data {acesso}'):
                    df = df[df['Data'] != acesso]
                    st.session_state.DF = df
                    st.session_state.DF.to_csv(vazio, index=False)
                    st.success(f'Registro da data {acesso} excluído com sucesso!')
                    st.dataframe(st.session_state.DF)
            else:
                st.warning('Nenhum registro encontrado com essa data.')
    else:
        st.warning('O arquivo CSV está vazio — adicione registros primeiro.')

# Imagem
imagem = Image.open('ianesm.png')
imagem_red = imagem.resize((180, 180))
st.image(imagem_red)

# Download
with open(vazio, 'rb') as file:
    st.download_button(label='Baixar arquivo CSV',
                       data=file,
                       file_name='dados_producao.csv',
                       mime='text/csv')

# Funções avançadas
if col3.button('Funções Avançadas'):
    st.subheader('Indicadores de Eficiência')

    ler_g = st.session_state.DF.copy()
    if not ler_g.empty:
        ler_g['Peças Produzidas'] = ler_g['Peças Produzidas'].astype(int)
        ler_g['Peças Defeituosas'] = ler_g['Peças Defeituosas'].astype(int)
        ler_g['Peças Boas'] = ler_g['Peças Produzidas'] - ler_g['Peças Defeituosas']
        ler_g['Eficiência (%)'] = (ler_g['Peças Boas'] / ler_g['Peças Produzidas'] * 100).round(2)

        st.dataframe(ler_g)

        # Alertas
        for i, row in ler_g.iterrows():
            if row['Eficiência (%)'] < 90:
                st.error(f"Alerta: Eficiência menor que 90% em {row['Data']} - Máquina {row['Máquina']}")
            if row['Peças Produzidas'] < 90:
                st.error(f"Alerta: Produção abaixo de 90 peças em {row['Data']} - Máquina {row['Máquina']}")

        # Média de produção
        st.subheader('Média de Produção por Máquina')
        media_maq = ler_g.groupby('Máquina')['Peças Produzidas'].mean().round(2)
        st.dataframe(media_maq.reset_index())
    else:
        st.warning('Nenhum dado para calcular indicadores.')

# Gráficos
if col5.button('Gráficos'):
    col_g1, col_g2 = st.columns(2)

    # Produção Diária Por Máquina
    if col_g1.button('Produção Diária Por Máquina'):
        st.header('Produção Diária Por Máquina')
        ler_g = st.session_state.DF.copy()
        if not ler_g.empty:
            ler_g['Peças Produzidas'] = ler_g['Peças Produzidas'].astype(int)
            maq = ler_g['Máquina'].unique()
            aces_maq = st.selectbox('Selecione uma máquina:', maq)
            maq_list = ler_g[ler_g['Máquina'] == aces_maq]
            plt.figure(figsize=(8, 4))
            plt.plot(maq_list['Data'], maq_list['Peças Produzidas'], 'd--', cmap='magma')
            plt.ylabel('Peças Produzidas')
            plt.xlabel('Data')
            st.pyplot(plt)
        else:
            st.warning('Nenhum dado para gerar gráfico.')

    # Taxa de Defeitos
    if col_g2.button('Taxa de defeitos'):
        st.header('Taxa de Defeitos')
        ler_g = st.session_state.DF.copy()
        if not ler_g.empty:
            ler_g['Peças Produzidas'] = ler_g['Peças Produzidas'].astype(int)
            ler_g['Peças Defeituosas'] = ler_g['Peças Defeituosas'].astype(int)
            dia = sorted(ler_g['Data'].unique())
            aces_dia = st.selectbox('Selecione uma data:', dia)
            dia_list = ler_g[ler_g['Data'] == aces_dia]
            pp_d = dia_list['Peças Produzidas'].sum()
            pd_d = dia_list['Peças Defeituosas'].sum()
            x = ['Peças Produzidas', 'Peças Defeituosas']
            y = [pp_d, pd_d]
            fig, ax = plt.subplots(1, 2, figsize=(10, 4))
            ax[0].bar(x, y, color=['indigo', 'darkmagenta'])
            ax[1].pie(y, labels=x, colors=['indigo', 'darkmagenta'], autopct='%1.1f%%')
            st.pyplot(fig)
        else:
            st.warning('Nenhum dado para gerar gráfico.')

# Vizualizar registros
if col4.button('Vizualizar Registros'):
    st.subheader('Visualizar Registros')
    col1b, col2b, col3b = st.columns(3)
    ler_f = st.session_state.DF.copy()
    if not ler_f.empty:
        ler_f['Data'] = pd.to_datetime(ler_f['Data'])
        inicio, fim = st.date_input('Selecione um intervalo de tempo:',
                                    [ler_f['Data'].min(), ler_f['Data'].max()])
        filtro = (ler_f['Data'].notna()) & (ler_f['Data'] >= pd.to_datetime(inicio)) & (ler_f['Data'] <= pd.to_datetime(fim))
        f_data = ler_f.loc[filtro]
        st.dataframe(f_data)

        # Filtro por máquina
        maqf = col2b.selectbox('Selecione uma máquina:', f_data['Máquina'].unique())
        f_maq = f_data[f_data['Máquina'] == maqf]
        st.dataframe(f_maq)

        # Filtro por turno
        turnof = col3b.selectbox('Selecione um turno:', f_data['Turno'].unique())
        f_turno = f_data[f_data['Turno'] == turnof]
        st.dataframe(f_turno)
    else:
        st.warning('Nenhum registro disponível.')
