import pandas as pd
import streamlit as st
import plotly_express as px
import sqlite3
from datetime import date

st.set_page_config(page_title='RESYS Dashboard')#titre du page 
st.title('RESYS Dashboard')#titre taille 1
excel_file = st.file_uploader("Importez un fichier Excel", type=["xlsx"])

def nom(x):#LIBINDFAM nom des indices 
    query1=f'SELECT DISTINCT {x} FROM a ORDER BY {x} ASC'#selection des indices de refraction 
    cursor.execute(query1)
    resultat=cursor.fetchall()
    temp_df= pd.DataFrame(resultat, columns=[x])
    return (temp_df,resultat)

def nombre(a):#nombre total selon un critère a 
    query=f'SELECT COUNT(*)  FROM a GROUP BY {a}  ORDER BY {a} ASC' #le nombre total de linces selon indice temp_df2
    cursor.execute(query)
    resultat=cursor.fetchall()
    temp_df= pd.DataFrame(resultat, columns=['nombre TOTAL'])
    return (temp_df,resultat)

def pourcentage_total(resultat): #f(nombre(,)[1])%total
    temp_df=pd.DataFrame()
    for i in range (0,len(resultat)):
        temp_df1=pd.DataFrame([[resultat[i][0]/nombre_ligne*100]],columns=[' %total'])#pourcentage de verre selon l indice
        temp_df=pd.concat([temp_df,temp_df1],axis=0)
    return temp_df

def nombre_pass(x):
        result_df = pd.DataFrame()
        temp_df7 = pd.DataFrame()

        for i in [1, 2, 3]:#nombre de linces de chaque pass 
            query = f"SELECT COUNT(b.{x})FROM(SELECT distinct {x} FROM a) AS c LEFT JOIN a AS b ON b.{x}=c.{x} AND b.QTE={i} GROUP BY c.{x} ORDER BY c.{x} "
            cursor.execute(query)
            resultat3 = cursor.fetchall()
            temp_df5 = pd.DataFrame(resultat3, columns=[f" {i} pass"])
            result_df = pd.concat([result_df, temp_df5], axis=1)
            resultat = []
            for j in range(len(resultat3)):
                resultat.append((resultat3[j][0] / nombre(x)[1][j][0] * 100,))
            temp_df6 = pd.DataFrame(resultat, columns=[f"pourcentage {i} pass"])#pourcentage par rapport a chaque critere de linces
            temp_df7 = pd.concat([temp_df7, temp_df6], axis=1)

        return result_df, temp_df7

def concat_nombre(a):
    x=nom(a)[0]
    y=nombre_pass(a)[0]
    z=nombre(a)[0]
    w=pourcentage_total(nombre(a)[1])
    for i in [x,y,z,w]:
        i.reset_index(drop=True, inplace=True)
    result_df = pd.concat([x,y,z,w], axis=1)   
    return result_df

def concat_pourcentage(a) :      
    result_df1 = pd.concat([nom(a)[0],nombre_pass(a)[1]], axis=1)#tableau indice pourcentage 
    return result_df1


def graph(x):
    for i in x:
        st.header('classification by '+i)
        #pie char
        df=pd.read_excel(excel_file1,sheet_name=i+'1',usecols='A,F')#selection des donnés pourcentage de chaque partie de x
        a=df.columns.tolist()
        pie_char=px.pie(df,title='Distribution of Each '+i+' in Total Quantity',values=' %total',names=a[0])
        st.plotly_chart(pie_char)
        #multi bar char
        df=pd.read_excel(excel_file1,sheet_name=i+'1',usecols='A:D')
        a=df.columns.tolist()
        bar_chart = px.bar(df, title='Pass Distribution', x=a[0], y=[' 1 pass',' 2 pass',' 3 pass'],barmode='group')
        bar_chart.update_xaxes(type='category')
        bar_chart.update_layout(width=800, height=600)
        st.plotly_chart(bar_chart)
        #pie char of each part
        df=pd.read_excel(excel_file1,sheet_name=i+'2',usecols='A:D')#selection des donnés
        for j in range (len(df)):
            ligne=df.loc[j]
            pie_char=px.pie(df,title='Distribution of '+str(ligne[0]),values=[ligne[1],ligne[2],ligne[3]],names=['pourcentage 1 pass' ,'pourcentage 2 pass ','pourcentage 3 pass'])
            st.plotly_chart(pie_char)
    return 0

def intervalle_date(df):#donner intervalle de date min et max 
    conn=sqlite3.connect(':memory:')
    df.to_sql('a', conn, if_exists='replace')
    cursor = conn.cursor()
    query=f'SELECT MIN(AAAA) , MIN(MM) , MIN(DD) FROM a '
    cursor.execute(query)
    x=cursor.fetchall()
    x[0]=date(*x[0])#x ou y sont des listes de tuples 
    query=f'SELECT MAX(AAAA) , MAX(MM) , MAX(DD) FROM a '
    cursor.execute(query)
    y=cursor.fetchall()
    y[0]=date(*y[0])#x et y doivent etre liste de date 
    return [x,y]


        
#programme principale 

if excel_file is not  None:
    df = pd.read_excel(excel_file)
    conn = sqlite3.connect(':memory:')
    # Enregistrement du DataFrame dans la table 'a' de la base de données
    df.to_sql('a', conn, if_exists='replace')
    cursor = conn.cursor()
    nombre_ligne = len(df)
    st.write('Linses Classification by Passes')
    result_df=pd.DataFrame()
    for i in [1,2,3]:
        query=f'SELECT COUNT(*)FROM a WHERE QTE={i}'
        cursor.execute(query)
        resultat=cursor.fetchall()
    
        column_name1 = f"{i}er pass"
        column_name='pourcentage'+f"{i}er pass"
        
        temp_df = pd.DataFrame(resultat, columns=[column_name1])  # temporary data frame
        temp_df1 = pd.DataFrame([[resultat[0][0] / nombre_ligne * 100]], columns=[column_name])#data frame pourcentage
        temp_df = pd.concat([temp_df, temp_df1], axis=1)
        result_df = pd.concat([result_df, temp_df], axis=1)
    bar_chart = px.bar(result_df, title='Pass Distribution (number)', x=['1st pass ','2nd pass','3rd pass'], y=[result_df.loc[0][0],result_df.loc[0][2],result_df.loc[0][4]])
    bar_chart.update_layout(
        xaxis_title='Pass Number',  # Nom de l'axe des abscisses
        yaxis_title='Quantity'
    )
    pie_char=px.pie(result_df,title='Distribution of  Total Quantity',values=[result_df.loc[0][1],result_df.loc[0][3],result_df.loc[0][5]],names=['pourcentage 1 pass' ,'pourcentage 2 pass ','pourcentage 3 pass'])
    st.plotly_chart(bar_chart)
    st.plotly_chart(pie_char)
        
    result_df=pd.DataFrame()#empty data frame
    with pd.ExcelWriter('result.xlsx', engine='openpyxl') as writer:
        # Write 'result_df' to 'indice pass' sheet
        concat_nombre('LIBINDFAM').to_excel(writer, sheet_name='indice1', index=False)
    
        # Write 'result_df1' to 'indice pourcentage' sheet
        concat_pourcentage('LIBINDFAM ').to_excel(writer, sheet_name='indice2', index=False)
        
        concat_nombre('TYPORD').to_excel(writer, sheet_name='ordre1', index=False)
        concat_pourcentage('TYPORD').to_excel(writer, sheet_name='ordre2', index=False)
        
        concat_nombre('LIBTEIFAM').to_excel(writer, sheet_name='type1', index=False)
        concat_pourcentage('LIBTEIFAM').to_excel(writer, sheet_name='type2', index=False)
    excel_file1='result.xlsx'
    
    
    
        
    
    
    
    graph(selected_options)

