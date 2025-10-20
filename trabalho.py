import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")
st.title('Linha de Montagem - IANES')
st.write('')

# caminho csv
vazio = "dados.csv"

# state
if 'DF' not in st.session_state:
    if os.path.exists(vazio):
        st.session_state.DF = pd.read_csv(vazio)
    else:
        st.session_state.DF = pd.DataFrame(columns=['Data', 'Máquina', 'Turno', 'Peças Produzidas', 'Peças Defeituosas'])

DF = st.session_state.DF

# seleção
opcao = st.sidebar.radio("Selecione a seção:", 
                         ['Adicionar Registro', 
                          'Atualizar/Excluir', 
                          'Funções Avançadas', 
                          'Gráficos', 
                          'Visualizar Registros'])

# adicionar
if opcao == 'Adicionar Registro':
    st.subheader('Adicionar Novo Registro')
    with st.form('form_novo_registro', clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        D = c1.date_input('Data:')
        M = c2.text_input('Máquina:')
        T = c3.selectbox('Turno:', ['Manhã', 'Tarde', 'Noite'])
        c1a, c2a = st.columns(2)
        PP = c1a.text_input('Peças Produzidas:')
        PD = c2a.text_input('Peças Defeituosas:')

        salvar_novo = st.form_submit_button('Salvar')
        if salvar_novo:
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
                st.success('Dados salvos com sucesso!')
                st.dataframe(st.session_state.DF)
            except ValueError:
                st.error('Preencha todos os campos corretamente!')

# atualizar/excluir
elif opcao == 'Atualizar/Excluir':
    df = st.session_state.DF
    st.subheader('Registros atuais')
    st.dataframe(df)

    if not df.empty:
        datas_salvas = sorted(df['Data'].unique())
        acesso = st.selectbox('Selecione a data do registro:', datas_salvas)
        if acesso:
            filtro = df['Data'] == acesso
            if filtro.any():
                ind = df.index[filtro][0]
                st.write('Registro encontrado:')
                st.write(df.loc[ind])

                with st.form('form_editar', clear_on_submit=False):
                    st.write('Altere os valores abaixo:')
                    c1f, c2f, c3f = st.columns(3)
                    D_new = c1f.text_input('Data:', str(df.at[ind, 'Data']))
                    M_new = c2f.text_input('Máquina:', str(df.at[ind, 'Máquina']))
                    T_new = c3f.selectbox('Turno:', ['Manhã', 'Tarde', 'Noite'],
                                          index=['Manhã', 'Tarde', 'Noite'].index(str(df.at[ind, 'Turno'])))
                    c1f, c2f = st.columns(2)
                    PP_new = c1f.text_input('Peças Produzidas:', str(df.at[ind, 'Peças Produzidas']))
                    PD_new = c2f.text_input('Peças Defeituosas:', str(df.at[ind, 'Peças Defeituosas']))
                    salvar_edit = st.form_submit_button('Salvar Alterações')

                    if salvar_edit:
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

                if st.button(f'Excluir registro da data {acesso}'):
                    df = df[df['Data'] != acesso]
                    st.session_state.DF = df
                    st.session_state.DF.to_csv(vazio, index=False)
                    st.success(f'Registro da data {acesso} excluído com sucesso!')
                    st.dataframe(st.session_state.DF)
    else:
        st.warning('Nenhum registro disponível.')

# ---------------------------
# FUNÇÕES AVANÇADAS
# ---------------------------
elif opcao == 'Funções Avançadas':
    st.subheader('Indicadores de Eficiência')
    ler_g = st.session_state.DF.copy()
    if not ler_g.empty:
        ler_g['Peças Produzidas'] = ler_g['Peças Produzidas'].astype(int)
        ler_g['Peças Defeituosas'] = ler_g['Peças Defeituosas'].astype(int)
        ler_g['Peças Boas'] = ler_g['Peças Produzidas'] - ler_g['Peças Defeituosas']
        ler_g['Eficiência (%)'] = (ler_g['Peças Boas'] / ler_g['Peças Produzidas'] * 100).round(2)

        st.dataframe(ler_g)

        for i, row in ler_g.iterrows():
            if row['Eficiência (%)'] < 90:
                st.error(f"Alerta: Eficiência menor que 90% em {row['Data']} - Máquina {row['Máquina']}")
            if row['Peças Produzidas'] < 90:
                st.error(f"Alerta: Produção abaixo de 90 peças em {row['Data']} - Máquina {row['Máquina']}")

        st.subheader('Média de Produção por Máquina')
        media_maq = ler_g.groupby('Máquina')['Peças Produzidas'].mean().round(2)
        st.dataframe(media_maq.reset_index())
    else:
        st.warning('Nenhum dado para calcular indicadores.')

# gráficos
elif opcao == 'Gráficos':
    st.subheader('Gráficos')
    ler_g = st.session_state.DF.copy()
    if not ler_g.empty:
        # Produção Diária Por Máquina
        st.write('### Produção Diária Por Máquina')
        maq = ler_g['Máquina'].unique()
        aces_maq = st.selectbox('Selecione uma máquina:', maq)
        maq_list = ler_g[ler_g['Máquina'] == aces_maq]
        plt.figure(figsize=(8, 4))
        plt.plot(maq_list['Data'], maq_list['Peças Produzidas'], 'd--', color = 'rebeccapurple')
        plt.ylabel('Peças Produzidas')
        plt.xlabel('Data')
        st.pyplot(plt)

        # Taxa de Defeitos
        st.write('### Taxa de Defeitos')
        dia = sorted(ler_g['Data'].unique())
        aces_dia = st.selectbox('Selecione uma data para defeitos:', dia)
        dia_list = ler_g[ler_g['Data'] == aces_dia]
        pp_d = dia_list['Peças Produzidas'].sum()
        pd_d = dia_list['Peças Defeituosas'].sum()
        x = ['Peças Produzidas', 'Peças Defeituosas']
        y = [pp_d, pd_d]
        fig, ax = plt.subplots(1, 2, figsize=(10, 4))
        ax[0].bar(x, y, color = ['indigo', 'darkmagenta'])
        ax[1].pie(y, labels=x, colors = ['indigo', 'darkmagenta'], autopct='%1.1f%%')
        st.pyplot(fig)
    else:
        st.warning('Nenhum dado disponível para gráficos.')

# vizualizar registros
elif opcao == 'Visualizar Registros':
    st.subheader('Visualizar Registros')
    ler_f = st.session_state.DF.copy()
    if not ler_f.empty:
        ler_f['Data'] = pd.to_datetime(ler_f['Data'])
        inicio, fim = st.date_input('Selecione um intervalo de tempo:',
                                    [ler_f['Data'].min(), ler_f['Data'].max()])
        filtro = (ler_f['Data'].notna()) & (ler_f['Data'] >= pd.to_datetime(inicio)) & (ler_f['Data'] <= pd.to_datetime(fim))
        f_data = ler_f.loc[filtro]
        st.dataframe(f_data)

        col1b, col2b, col3b = st.columns(3)
        maqf = col2b.selectbox('Selecione uma máquina:', f_data['Máquina'].unique())
        f_maq = f_data[f_data['Máquina'] == maqf]
        st.dataframe(f_maq)

        turnof = col3b.selectbox('Selecione um turno:', f_data['Turno'].unique())
        f_turno = f_data[f_data['Turno'] == turnof]
        st.dataframe(f_turno)
    else:
        st.warning('Nenhum registro disponível.')

# imagem/download
imagem = Image.open('ianesm.png')
imagem_red = imagem.resize((180, 180))
st.image(imagem_red)

with open(vazio, 'rb') as file:
    st.download_button(label = 'Baixar arquivo CSV',
                       data = file,
                       file_name = 'dados_producao.csv',
                       mime = 'text/csv')

