import numpy as np
import pandas as pd
import seaborn as sns
import math
import plotly
import streamlit as st
from PIL import Image



def app():
    df=pd.read_csv('returntosport.csv', encoding='UTF-8', header =(0))
    name=st.selectbox('Athlete Name', df['Name'])
    nodalman= Image.open('nodalman.jpeg')

    client = df[ df['Name']== name]
    
    if client['InjSide'].iloc[0] == 'L':
        lknee= 'red'
        rknee= 'gray'
    elif client['InjSide'].iloc[0] == 'R':
        lknee = 'gray'
        rknee= 'red'
    
    #region Nodal Man Layout
    fig = plotly.graph_objects.Figure(data=[plotly.graph_objects.Scatter(
    x=[2.5, 3.6], y=[10, 10],
    #text=['R_Ankle:'+ str(rightank),'R_Leg:'+str(rightkn) , 'L_Leg:'+str(leftkn), 'L_Ankle:'+str(leftank), 'Hip&Trunk:'+str(round(trunkscore,2)),'UpperExt:'+str(shouldermob)],
    mode='markers',
    marker=dict(
        color=[rknee, lknee ],
        size=[40, 40],
    )
    )],
    layout=plotly.graph_objects.Layout(width=450, height= 750)
    )
    fig.update_xaxes(range=[0, 5],visible=False)
    fig.update_yaxes(range=[0, 30],visible=False)
    fig.add_layout_image(
        dict(
            source=nodalman,
            xref="x",
            yref="y",
            x=0,
            y=0,
            xanchor='left',
            yanchor='bottom',
            sizex=5,
            sizey=30,
            sizing="fill",
            opacity=1,
            layer="below")
    )
    
    #endregion
    
    #region Isometric Strength
    x = ['Quads', 'Hamstring']
    
    plot = plotly.graph_objects.Figure(data=[plotly.graph_objects.Bar(
        name = 'Left',
        y = x,
        x = [client['QuadLIso'].iloc[0], client['HamLIso'].iloc[0]]
    ,orientation='h',marker_color=lknee),
                        plotly.graph_objects.Bar(
        name = 'Right',
        y = x,
        x = [client['QuadRIso'].iloc[0],client['HamRIso'].iloc[0]]
    ,orientation='h',marker_color=rknee,marker_line_color='rgb(128,128,128)')
    ])
    plot.update_layout(autosize=False, height=300,width=550, title_text='Isometric Strength (N)')
    #endregion
    
    #region Distance Hops
    mecs = ['SL-Hop', 'Triple-Hop', 'Crossover-Hop', 'Timed Hop(ms)']
    
    mechplot = plotly.graph_objects.Figure(data=[plotly.graph_objects.Bar(
        name = 'Left',
        x = mecs,
        y = [client['XHopLAvg'].iloc[0], client['TriHopLAvg'].iloc[0], client['SLHopLAvg'].iloc[0], client['TimeHopLAvg'].iloc[0]*100]
    ,marker_color=lknee),
                        plotly.graph_objects.Bar(
        name = 'Right',
        x = mecs,
        y = [client['XHopRAvg'].iloc[0], client['TriHopRAvg'].iloc[0], client['SLHopRAvg'].iloc[0],client['TimeHopRAvg'].iloc[0]*100]
    ,marker_color=rknee,marker_line_color='rgb(128,128,128)')
    ])
    mechplot.update_layout(autosize=False, height=400,width=550, title_text='Hop Distance (in), Time (ms)')
    #endregion
    
    if client['QuadRIso'].iloc[0] >= client['QuadLIso'].iloc[0]:
        quadisoasym= round((1- (client['QuadLIso'].iloc[0] / client['QuadRIso'].iloc[0]))*100,2)
        
    elif client['QuadRIso'].iloc[0] < client['QuadLIso'].iloc[0]:
        quadisoasym= round((1- (client['QuadRIso'].iloc[0] / client['QuadLIso'].iloc[0]))*100,2)
        
    if client['HamLIso'].iloc[0] <= client['HamRIso'].iloc[0]:
        hamisoasym= round((1- (client['HamLIso'].iloc[0] / client['HamRIso'].iloc[0]))*100,2)
    elif client['HamLIso'].iloc[0] > client['HamRIso'].iloc[0]:
        hamisoasym= round((1- (client['HamRIso'].iloc[0] / client['HamLIso'].iloc[0]))*100,2)
        
    if client['SLHopLAvg'].iloc[0] <= client['SLHopRAvg'].iloc[0]:
        slhopasym= round((1- (client['SLHopLAvg'].iloc[0] / client['SLHopRAvg'].iloc[0]))*100,2)
    elif client['SLHopLAvg'].iloc[0] > client['SLHopRAvg'].iloc[0]:
        slhopasym= round((1- (client['SLHopRAvg'].iloc[0] / client['SLHopLAvg'].iloc[0]))*100,2)
        
        
    if client['TriHopLAvg'].iloc[0] <= client['TriHopRAvg'].iloc[0]:
        trihopasym= round((1- (client['TriHopLAvg'].iloc[0] / client['TriHopRAvg'].iloc[0]))*100,2)
    elif client['TriHopLAvg'].iloc[0] > client['TriHopRAvg'].iloc[0]:
        trihopasym= round((1- (client['TriHopRAvg'].iloc[0] / client['TriHopLAvg'].iloc[0]))*100,2)
        
    if client['XHopLAvg'].iloc[0] <= client['XHopRAvg'].iloc[0]:
        xhopasym= round((1- (client['XHopLAvg'].iloc[0] / client['XHopRAvg'].iloc[0]))*100,2)
    elif client['XHopLAvg'].iloc[0] > client['XHopRAvg'].iloc[0]:
        xhopasym= round((1- (client['XHopRAvg'].iloc[0] / client['XHopLAvg'].iloc[0]))*100,2)    
        
    if client['TimeHopLAvg'].iloc[0] <= client['TimeHopRAvg'].iloc[0]:
        timehopasym= round((1- (client['TimeHopLAvg'].iloc[0] / client['TimeHopRAvg'].iloc[0]))*100,2)
    elif client['TimeHopLAvg'].iloc[0] > client['TimeHopRAvg'].iloc[0]:
        timehopasym= round((1- (client['TimeHopRAvg'].iloc[0] / client['TimeHopLAvg'].iloc[0]))*100,2)
    
    if quadisoasym >=10 or hamisoasym >=10 or slhopasym>=10 or trihopasym >=10 or xhopasym >=10 or timehopasym >=10 or client['aclrts_score'].iloc[0] <64 or client['ikdc_score'].iloc[0] <84:
        result = 'High-Risk'
    else:
        result= 'Low-Risk'
    
    st.title('Return To Sport Report')
    st.write('__Presented by THE LAB__')
    st.header(name)

    col1, col2, col3 =st.columns([1,0.5,1])
    col1.markdown('**Date of Assessment:** ' + client['Date'].to_string(index= False))
    col2.markdown('**Sex:**  '+ client['Sex'].to_string(index= False))
    
    
    st.write('___')
    
    
    st.header('Assessment Summary')
    st.subheader('**Verdict**:  ' + result)
    if result == 'High-Risk':
        st.error('Based on the results for ' + client['Name'].to_string(index= False) + ' did not satisfy the requirements to safely return to sport.')
    elif result == 'Low-Risk':
        st.success('Based on the results for ' + client['Name'].to_string(index= False) + ' satisfy the requirements to safely return to sport.')
    st.title(' ')    
    st.markdown('___')
    
    col1, col2, col3 =st.columns([0.8,1,2])

    col1.subheader('Primary Activity:')
    col2.subheader(client['Primary_Activity'].to_string(index= False))
    col1.markdown('**Secondary Activity:**  '+ client['Secondary_Activity'].to_string(index= False))
    col1.markdown('**Dominant Side:** ' + client['LimbDom'].to_string(index= False))
    col1.markdown('**Date of Injury:** '+ client['Injdate'].to_string(index= False))
    
    
    col1.subheader('**Injury Side:** ')

    col2.title(' ')
    col2.title(' ')
    col2.header(' ')
    col2.write(' ')

    col2.subheader(client['InjSide'].to_string(index= False))
    col1.subheader('**Injury Type:**  ') 
    col2.subheader(client['InjType'].to_string(index= False))
    col1.subheader('**Injury Specs:**'  )
    col2.subheader(client['InjSpecs'].to_string(index= False))
    
    col1.title(' ')
    col1.markdown('**Mobility**')
    col1.markdown('Ankle Mobility [cm/deg] (10+/36°+): ')
    col1.markdown('Hip Internal Rotation (40°+) : ')
    col1.markdown('Hip External Rotation (55°+): ')
    col2.title(' ')
    col2.markdown('**Left|Right**')
    col2.markdown(client['Ankle_L_cm'].to_string(index= False)+'/'+client['Ankle_L_deg'].to_string(index= False)+' | '+ client['Ankle_R_cm'].to_string(index= False)+'/'+client['Ankle_R_deg'].to_string(index= False))
    col2.markdown(client['Hip_L_In'].to_string(index= False) + ' | ' + client['Hip_R_In'].to_string(index= False))
    col2.markdown(client['Hip_L_Ex'].to_string(index= False) + ' | ' + client['Hip_R_Ex'].to_string(index= False))
    
    col3.plotly_chart(fig)
    

    
    st.write('___')
    st.subheader('Results')
    
    col1, col2, col3 =st.columns([2,0.5,2])
    
    col1.plotly_chart(plot)
    col1.plotly_chart(mechplot)
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')

    col2.markdown('**Isometric Str. Asymmetry**')
    col2.markdown('Quads:  ' + str(quadisoasym) + '%')
    col2.markdown('Hamstring:  ' + str(hamisoasym) + '%')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')
    col2.write('  ')


    col3.write('  ')
    col3.write('  ')
    col3.write('  ')
    col3.write('  ')
    col3.write('Isometric strength is your ability to generate force with no changes in displacement with respect to your leg. The results of the isometric strength test will show the asymmetrical differences between your non-injured and injured leg.')
    col3.write('The isometric strength of the quadriceps is evaulated through knee extension intent, similar to a kicking motion. The isometric strength of the hamstrings is evaulated through knee flexion, a tuck or curling motion of your heel towards your butt.')
    
    if quadisoasym >= 10:
        col3.warning('**Verdict: High-Risk**')
        col3.write('There presents a significant asymmetry in isometric strength in the quadriceps (knee extension). This asymmetry is an indicator of injury risk. It is best advised to continue rehabilitation and strengthening of the knee.')
    elif hamisoasym >=10:
        col3.warning('**Verdict: High-Risk**')
        col3.write('There presents a significant asymmetry in isometric strength in the hamstrings (knee flexion). This asymmetry is an indicator of injury risk. It is best advised to continue rehabilitation and strengthening of the knee.')
    elif hamisoasym >=10 and quadisoasym>=10:
        col3.warning('**Verdict: High-Risk**')
        col3.write('There presents a significant asymmetry in isometric strength in the quadriceps (knee extension) and hamstrings (knee flexion). This asymmetry is an indicator of injury risk. It is best advised to continue rehabilitation and strengthening of the knee.')
    elif hamisoasym <10 and quadisoasym <10:
        col3.info('**Verdict: Low-Risk**')
        col3.write(client['Name'].to_string(index= False) + ' satisfies the isometric strength criteria of the protocol. There presents low asymmetry in isometric force production of either leg.')

    col2.markdown('**Hop Asymmetry**')
    col2.markdown('Single Leg:   '+str(slhopasym)+ '%')
    col2.markdown('Triple Hop:   '+str(trihopasym)+ '%')
    col2.markdown('Crossover :   '+str(xhopasym)+ '%')
    col2.markdown('Timed Hop :' + str(timehopasym)+'%')
    col3.markdown(' ')
    col3.markdown(' ')
    col3.write('The hop test provides a dynamic evaluation of both legs. It gives a comprehensive analysis of how the knee is controlled moving both forward and laterally. With time and distance objectives, it simulates sport specific movement patterns. Intolerance or lack of control during the hop assessment will greatly screen injury risks when an athlete is operating in a competitive setting.')
    if slhopasym>=10 or trihopasym >=10 or xhopasym >=10 or timehopasym >=10 :
        col3.error('**Verdict: High-Risk**')
        col3.markdown(client['Name'].to_string(index=False) + ' did not fulfill the criteria to return to sport safely. Based on the hop results, there presents a significant amount of asymmetry that puts the knee at risk.')
    elif slhopasym<10 or trihopasym <10 or xhopasym <10 or timehopasym <10 :
        col3.info('**Verdict: Low-Risk**')
        col3.markdown(client['Name'].to_string(index=False) + ' fulfilled the criteria to return to sport safely. Based on the hop results, the performance on either leg did not surpass the asymmetry threshold.')
    st.write('___')
    st.subheader('ACLr Return to Play and IKDC Subjective Knee Evaulation')
    st.title('  ')
    
    col1,col2=st.columns([0.2,1])
    
    col2.markdown('**ACL Return to Sport Evaluation Score (64):**   '+ round(client['aclrts_score'],2).to_string(index= False))
    col2.markdown('**International Knee Documentation Committee (IKDC) Subjective Knee Evaluation (84):**    '+ round(client['ikdc_score'],2).to_string(index= False))
    
    if client['aclrts_score'].iloc[0] < 64 or client['ikdc_score'].iloc[0] < 84:
        st.markdown(client['Name'].to_string(index= False) + ' did not meet the pyschological criteria to return to sport. Psychologically unprepared athletes can face an increase in re-injury rate.')
    elif client['aclrts_score'].iloc[0] >= 64 or client['ikdc_score'].iloc[0] >= 84:
        st.markdown(client['Name'].to_string(index= False) + ' has meet the pyschological criteria to return to sport.')
    col2.markdown('')
    
    st.markdown('___')
    st.subheader('Evaluation Breakdown')
    col1,col2= st.columns([1,1])

    col1.markdown('**ACL-RSI**: ' + client['aclrts_score'].to_string(index= False))
    col1.markdown('**IKDC**: ' + round(client['ikdc_score'],2).to_string(index= False))
    
    
    if quadisoasym <10:
        col1.markdown('**Quadiceps (Knee Extension) Isometric**:  Low-Risk')
    elif quadisoasym >=10:
        col1.markdown('**Quadiceps (Knee Extension) Isometric**:  High-Risk')
    if hamisoasym <10:
        col1.markdown('**Hamstring (Knee Flexion) Isometric**:  Low-Risk')
    elif hamisoasym >=10:
        col1.markdown('**Hamstring (Knee Flexion) Isometric**:  High-Risk')
    if slhopasym <10:
        col2.markdown('**Single Leg Hop**:  Low-Risk')
    elif slhopasym >=10:
        col2.markdown('**Single Leg Hop**:  High-Risk')
    if trihopasym <10:
        col2.markdown('**Triple Hop**:  Low-Risk')
    elif trihopasym >=10:
        col2.markdown('**Triple Hop**:  High-Risk')
    if xhopasym <10:
        col2.markdown('**Cross Hop**:  Low-Risk')
    elif xhopasym >=10:
        col2.markdown('**Cross Hop**:  High-Risk')
    if timehopasym <10:
        col2.markdown('**Timed Hop**:  Low-Risk')
    elif timehopasym >=10:
        col2.markdown('**Timed Hop**:  High-Risk')
    
    if pd.isna(client['Notes'].iloc[0]) is False:
        st.write(client['Notes'])
    
    
    st.write('___')
