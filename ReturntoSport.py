import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from scipy import integrate


df=pd.read_csv('returntosport.csv', encoding='UTF-8', header =(0))
df= pd.DataFrame(columns= df.columns)
df.loc[df.shape[0]]=float('NaN')

def djapp(fpl,fpr,kg,RoCsensitivity):
    Fg=kg*9.81

    i=0
    j=0
    tl1=[0]
    tl2=[0]
    tr1=[0]
    tr2=[0]

#adjusting for drop vert, since initial start there are no forces on the plates, step until theres impact
    while fpl['Fz'][i] <10:
        i+=1
    while fpr['Fz'][j] <10:
        j+=1

    touchL=int(i)
    touchR=int(j)
    #finding air time
    while fpl['Fz'][i]> 10:
        i+=1
        i1=i
        tl1=fpl['Time'][i]

    while fpr['Fz'][j]> 10:
        j+=1
        j1=j
        tr1= fpr['Time'][j]
        
    takeoffindex=int(j)

    while fpl['Fz'][i] <10:
        i+=1
        tl2=fpl['Time'][i]
        
    while fpr['Fz'][j] <10:
        j+=1
        tr2=fpr['Time'][j]

    airtime= min(tl2-tl1,tr2-tr1)
    takeoff= max(tl1,tr1)

    #smaller larger step size in finding derivative for higher rate of change between f[i+1] and f[i]
    steps=int(len(fpr['Fz'])/10)
    t=[0]*steps
    FzR=[0]*steps
    FzL=[0]*steps

    #storing larger stepsize
    for k in range(steps):
        FzR[k]= fpr['Fz'][k*10]
        FzL[k]= fpl['Fz'][k*10]
        t[k]= fpr['Time'][k*10]
        k+=1
    #numpy derivative function
    fzr_p= np.diff(FzR) *10
    fzl_p= np.diff(FzL) *10
    #store together in table for export to csv
    #getting rid of f[@x=0] to match array size as derivative will have size (n-1)
    t.pop(0)
        
    #finding peak concentric maxima

    #iterating backwards, from Fz=0 at takeoff, loop until value stops increasing
    while fpr['Fz'][j1-1] > fpr['Fz'][j1]:
        j1-= 1
    while fpl['Fz'][i1-1] > fpl['Fz'][i1]:
        i1-= 1
    #as rate of change approaches 0, noise in the data can falsely detect maximum even when rate of change is not 0 yet
    #initiate larger stepsize at point of first stoppage
    kr1=j1//10
    kl1=i1//10
    kr2=kr1
    kl2=kl1
    #from takeoff stepping backwards, we aim to search for the local maximum (Peak Con. Force) when derivative is near 0
    #and after the rate of changes from negative to positive
    while fzr_p[kr1] <5:
        kr1-=1
    while fzl_p[kl1] <5:
        kl1-=1
    #(point k1 'right') to indicate the point prior to the peak con. force maximum
    #stores value between kr1 and kr2 then search for maximum value
    rpcfdjrange=[0]*((kr2-kr1)*10)
    lpcfdjrange=[0]*((kl2-kl1)*10)
    for jj in range((kr2-kr1)*10):
        rpcfdjrange[jj]=fpr['Fz'][(kr1*10)+jj]
        jj+=1
    for ii in range((kl2-kl1)*10):
        lpcfdjrange[ii]=fpl['Fz'][(kl1*10)+ii]
        ii+=1
        
    rpcfdj=(max(rpcfdjrange))
    lpcfdj=(max(lpcfdjrange))
    jj=rpcfdjrange.index(rpcfdj)
    ii=lpcfdjrange.index(lpcfdj)
    rpcfdjloc= kr1*10 + jj
    lpcfdjloc=kl1*10 + ii

    #print(fpl['Time'][kl1*10+ii],fpr['Time'][kr1*10+jj],rpcfdj, lpcfdj)
    #print(kr1,kr2,kl1,kl2)

    #rate of change same stepsize
    Fzr_p= np.diff(fpr['Fz']) 
    Fzl_p= np.diff(fpl['Fz']) 

    #Impact Spike 1
    a=0
    b=0
    impact1Larr=[0]*1000
    impact1Rarr=[0]*1000
    
    while Fzl_p[touchL + b]> -RoCsensitivity:
        b+=1
        impact1Larr[b]=fpl['Fz'][touchL +b]
    while Fzr_p[touchR + a]> -30:
        a+=1
        impact1Rarr[a]= fpr['Fz'][touchR +a]

    

    impact1L= max(impact1Larr)
    impact1R= max(impact1Rarr)
    impact1Lloc=impact1Larr.index(impact1L)
    impact1Rloc=impact1Rarr.index(impact1R)

    impact2Larr=[0]*(lpcfdjloc-impact1Lloc)
    impact2Rarr=[0]*(rpcfdjloc-impact1Rloc)

    #impact spike 2
    #from impact spike 1 to peak con, maximum points
    for i in range (lpcfdjloc-impact1Lloc):
        impact2Larr[i]= fpl['Fz'][impact1Lloc + i]
        i+=1
    for j in range (rpcfdjloc-impact1Rloc):
        impact2Rarr[j]=fpr['Fz'][impact1Rloc + j]
        j+=1
        
    impact2L= max(impact2Larr)
    impact2R= max(impact2Rarr)

    #from 18inch drop jump box
    Nmperkg=5.45
    estimatedimpulse= kg*Nmperkg
    #note this is an approximation
    Impulse1R=0
    Impulse1L=0
    n= 1
    m=1

    while Impulse1R + Impulse1L < estimatedimpulse:
        dImpulseR= fpr['Fz'][touchR:touchR+n]
        dTimeR= fpr['Time'][touchR:touchR+n]
        dImpulseL= fpl['Fz'][touchL:touchL+m]
        dTimeL= fpl['Time'][touchL:touchL+m]
        Impulse1R=integrate.simps(dImpulseR,dTimeR)
        Impulse1L=integrate.simps(dImpulseL,dTimeL)
        n+=1
        m+=1
    propulsionR=touchR+n
    propulsionL=touchL+m

    dImpulseR= fpr['Fz'][propulsionR:takeoffindex] - Fg/2
    dTimeR= fpr['Time'][propulsionR:takeoffindex]
    dImpulseL= fpl['Fz'][propulsionL:takeoffindex] - Fg/2
    dTimeL= fpl['Time'][propulsionL:takeoffindex]

    netImpulseR=integrate.simps(dImpulseR,dTimeR)
    netImpulseL=integrate.simps(dImpulseL,dTimeL)
    print(netImpulseR, netImpulseL)

    return(airtime, rpcfdj,lpcfdj,impact1L, impact1R,impact2L, impact2R, Impulse1R, Impulse1L,n, m , netImpulseR, netImpulseL)




def app():
    df=pd.read_csv('returntosport.csv', encoding='UTF-8', header =(0))

    logo= Image.open('Lab_FullColor.jpg')
    col1,col2,col3 =st.columns([1,1,1])
    col2.image(logo,width=300)
    st.write('____________________')
    st.title('Return to Sport Assessment')
    st.write('__Presented by__')
    st.write('__Dr. Zach Finer, DPT__')
    name=st.selectbox('Athlete Name', df['Name'])
    person= df[df['Name']==name]
    index = person.index.values.astype(int)[0]
    
    injType= st.selectbox('Injury Type',['ACLr', 'ACLr with meniscus debridement', 'ACLr with meniscus repair','None'])
    injSide= st.radio('Side of Injury', ['L','R'])
    injSpec= st.selectbox('Injury Specifics',['Bone-Petalla-Bone Graft','Hamstring autograft','Quad tendon autograft','Allograft(donor)','N/A'])

    notes= st.text_area('Additional Notes')

    col1, col2 = st.columns(2)

    st.write('___')
    st.subheader('Performance Metrics')

    st.write('**Mobility**')
    col1, col2 =st.columns([1,1])

    ankleLcm=col1.number_input('Ankle Mob (cm) - Left')
    ankleLdeg=col1.number_input('Ankle Mob (deg) - Left')
    hipLin=col1.number_input('Hip Internal Rotation (deg) - Left')
    hipLex=col1.number_input('Hip External Rotation (deg) - Left')
    
    ankleRcm=col2.number_input('Ankle Mob (cm) - Right')
    ankleRdeg=col2.number_input('Ankle Mob (deg) - Right')
    hipRin=col2.number_input('Hip Internal Rotation (deg) - Right')
    hipRex=col2.number_input('Hip External Rotation (deg) - Right')

    st.write('___')

    st.write("**Isometric Strength Test**")
    col1,col2= st.columns([1,1])
    Llength= col1.number_input('Left Leg Length (m)')
    Rlength=col2.number_input('Right Leg Length (m)')
    QuadLiso=col1.number_input('Left Quad - Isometric Force [N]')
    QuadRiso=col2.number_input('Right Quad - Isometric Force [N]')
    HamLiso= col1.number_input('Left Hamstr - Isometric Force [N]')
    HamRiso= col2.number_input('Right Hamstr - Isometric Force [N]')

        
    st.write('___')

    st.write("**Single Leg Hop - Distance Test**")
    col1,col2= st.columns([1,1])
    slhopL1= col1.number_input('Left Single Leg Hop - Trial 1 (in)')
    slhopL2= col1.number_input('Left Single Leg Hop - Trial 2 (in)')
    slhopL3= col1.number_input('Left Single Leg Hop - Trial 3 (in)')
    slhopR1= col2.number_input('Right Single Leg Hop - Trial 1 (in)')
    slhopR2= col2.number_input('Right Single Leg Hop - Trial 2 (in)')
    slhopR3= col2.number_input('Right Single Leg Hop - Trial 3 (in)')


    st.write('___')

    st.write("**Triple Hop - Distance Test**")
    col1,col2= st.columns([1,1])
    TriHopL1= col1.number_input('Left Triple Hop - Trial 1 (in)')
    TriHopL2= col1.number_input('Left Triple Hop - Trial 2 (in)')
    TriHopL3= col1.number_input('Left Triple Hop - Trial 3 (in)')
    TriHopR1= col2.number_input('Right Triple Hop - Trial 1 (in)')
    TriHopR2= col2.number_input('Right Triple Hop - Trial 2 (in)')
    TriHopR3= col2.number_input('Right Triple Hop - Trial 3 (in)')

        
    st.write('___')

    st.write("**Cross-over Hop - Distance Test**")
    col1,col2= st.columns([1,1])
    XHopL1= col1.number_input('Left Cross-over Hop - Trial 1 (in)')
    XHopL2= col1.number_input('Left Cross-over Hop - Trial 2 (in)')
    XHopL3= col1.number_input('Left Cross-over Hop - Trial 3 (in)')
    XHopR1= col2.number_input('Right Cross-over Hop - Trial 1 (in)')
    XHopR2= col2.number_input('Right Cross-over Hop - Trial 2 (in)')
    XHopR3= col2.number_input('Right Cross-over Hop - Trial 3 (in)')

    

    st.write('___')
    
    
    st.write("**Time Hop**")
    col1,col2= st.columns([1,1])
    TimeHopL1= col1.number_input('Left Time Hop - Trial 1 (seconds)')
    TimeHopL2= col1.number_input('Left Time Hop - Trial 2 (seconds)')
    TimeHopL3= col1.number_input('Left Time Hop - Trial 3 (seconds)')
    TimeHopR1= col2.number_input('Right Time Hop - Trial 1 (seconds)')
    TimeHopR2= col2.number_input('Right Time Hop - Trial 2 (seconds)')
    TimeHopR3= col2.number_input('Right Time Hop - Trial 3 (seconds)')

    st.write('___')

    st.write("**Drop Jump**")
    djstatus=st.checkbox('Drop Jump') 
    
    if djstatus is True:
        RoCsensitivity= st.slider('Rate of Change Sensitivity', min_value=0, max_value=100, value=50,step=1, key=2)
        bwkgs= st.number_input('Bodyweight (lbs)')/2.205
        col1,col2,col3, col4= st.columns([1,0.5,1,1])
        
        djhip= col1.number_input('Hip Angle',key=2)
        djknee= col3.number_input('Knee Angle',key=2)
        djfeet= col1.number_input('Vert (ft)')
        djinch= col3.number_input('Vert (in)')

        leftdjfp = col1.file_uploader("Upload Left Forceplate", type=['txt'],key=2)
        rightdjfp = col3.file_uploader("Upload Right Forceplate", type=['txt'],key=2)
        if leftdjfp is not None:
            dfldj= pd.read_csv(leftdjfp, header =(0),sep='\t')
        if rightdjfp is not None:
            dfrdj= pd.read_csv(rightdjfp, header =(0),sep='\t')
        
        if rightdjfp is not None and leftdjfp is not None and bwkgs>0:
            djairtime, rpcfdj, lpcfdj, djimpact1L, djimpact1R, djimpact2L, djimpact2R, djbrakeImpulseR, djbrakeImpulseL, braketimel, braketimeR, djpushImpulseR, djpushImpulseL =djapp (dfldj, dfrdj, bwkgs,RoCsensitivity)


    
        elif rightdjfp is None:
            st.warning('No Right Forceplate Data')
        elif leftdjfp is None:
            st.warning('No Left Forceplate Data')
        elif bwkgs==0:
            st.warning('No Bodyweight')
    st.dataframe(df)

    st.write('___')
    if st.button('Save & Publish'):
        #df= pd.concat([df, df], axis=0)
        df.loc[index,'InjType']= injType
        df.loc[index,'InjSpecs']= injSpec
        df.loc[index,'Notes']= notes
        df.loc[index,'InjSide']=injSide
        df.loc[index,'Ankle_L_cm']= ankleLcm
        df.loc[index,'Ankle_L_deg']= ankleLdeg
        df.loc[index,'Hip_L_In']= hipLin
        df.loc[index,'Hip_L_Ex']= hipLex
        df.loc[index,'Ankle_R_cm']= ankleRcm
        df.loc[index,'Ankle_R_deg']=ankleRdeg
        df.loc[index,'Hip_R_In']= hipRin
        df.loc[index,'Hip_R_Ex']= hipRex
        df.loc[index,'Llength']= Llength
        df.loc[index,'Rlength']= Rlength
        df.loc[index,'QuadLIso']= QuadLiso
        df.loc[index,'QuadRIso']= QuadRiso
        df.loc[index,'HamLIso']= HamLiso
        df.loc[index,'HamRIso']= HamRiso
        df.loc[index,'SLHop1L'] = slhopL1
        df.loc[index,'SLHop2L'] = slhopL2
        df.loc[index,'SLHop3L'] = slhopL3
        df.loc[index,'SLHopLAvg'] = (slhopL1 + slhopL2 + slhopL3)/3
        df.loc[index,'SLHop1R'] = slhopR1
        df.loc[index,'SLHop2R'] = slhopR2
        df.loc[index,'SLHop3R'] = slhopR3
        df.loc[index,'SLHopRAvg'] =  (slhopR1+slhopR2+slhopR3)/3
        df.loc[index,'TriHop1L'] = TriHopL1
        df.loc[index,'TriHop2L'] = TriHopL2
        df.loc[index,'TriHop3L'] = TriHopL3
        df.loc[index,'TriHopLAvg'] = (TriHopL1 + TriHopL2 + TriHopL3)/3
        df.loc[index,'TriHop1R'] = TriHopR1
        df.loc[index,'TriHop2R'] = TriHopR2
        df.loc[index,'TriHop3R'] = TriHopR3
        df.loc[index,'TriHopRAvg'] = (TriHopR1 + TriHopR2 + TriHopR3)/3
        df.loc[index,'XHop1L'] = XHopL1
        df.loc[index,'XHop2L'] = XHopL2
        df.loc[index,'XHop3L'] = XHopL3
        df.loc[index,'XHopLAvg'] = (XHopL1 + XHopL2 + XHopL3)/3
        df.loc[index,'XHop1R'] = XHopR1
        df.loc[index,'XHop2R'] = XHopR2
        df.loc[index,'XHop3R'] = XHopR3
        df.loc[index,'XHopRAvg'] = (XHopR1 + XHopR2 + XHopR3)/3
        
        df.loc[index,'TimeHop1L'] = TimeHopL1
        df.loc[index,'TimeHop2L'] = TimeHopL2
        df.loc[index,'TimeHop3L'] = TimeHopL3
        df.loc[index,'TimeHopLAvg'] = (TimeHopL1 + TimeHopL2 + TimeHopL3)/3
        df.loc[index,'TimeHop1R'] = TimeHopR1
        df.loc[index,'TimeHop2R'] = TimeHopR2
        df.loc[index,'TimeHop3R'] = TimeHopR3
        df.loc[index,'TimeHopRAvg'] = (TimeHopR1 + TimeHopR2 + TimeHopR3)/3
        if djstatus is True:
            df.loc[index,'DV_H']= djhip
            df.loc[index,'DV_K']= djknee
            df.loc[index,'dj_airtime']= djairtime
            df.loc[index,'DV_PeakCon_R']= rpcfdj
            df.loc[index,'DV_PeakCon_L']= lpcfdj
            df.loc[index,'dj_impact1L']= djimpact1L
            df.loc[index,'dj_impact1R']= djimpact1R
            df.loc[index,'dj_impact2L']= djimpact2L
            df.loc[index,'dj_impact2R']= djimpact2R
            df.loc[index,'dj_brakeImpulseL']= djbrakeImpulseL
            df.loc[index,'dj_brakeImpulseR']= djbrakeImpulseR
            df.loc[index,'djbraketime']= max(braketimel,braketimeR)
            df.loc[index,'djpushImpulseL']= djpushImpulseL
            df.loc[index,'djpushImpulseR']= djpushImpulseR
            df.loc[index,'DJ_VERT']= (12*djfeet)+djinch
        
        
        df.to_csv('returntosport.csv', index=False)
        st.success("Saved")
        #concat that bitch
