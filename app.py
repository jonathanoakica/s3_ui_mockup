import streamlit as st
import numpy as np
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UI Mockup - K Numbers", layout='wide')

event = pd.read_csv('event_with_mock.csv')

st.sidebar.title('UI Mockup - K Numbers')

nums = list(event['udi_number'].unique())
nums.insert(0, '')
tresh = [i for i in range (5,100,5)]
tresh.insert(0, '')
selected = st.sidebar.selectbox('UDI Number:', nums)
treshold = st.sidebar.selectbox('Define a Threshold:', tresh)



#queried.reset_index(inplace=True, drop=True)
#queried['mdr_report_key'] = queried['mdr_report_key'].astype(str)


if selected != '':

    #selected_key = st.sidebar.selectbox('Choose a Report Key Number:', report_keys)

#---------------------Data preparations---------------------
    queried = event.query(f'udi_number == {selected}')
    queried.reset_index(drop=True, inplace=True)
    queried["date_of_event"] = pd.to_datetime(queried["date_of_event"])
    gbc = queried.groupby([queried['date_of_event'].dt.month])['date_of_event'].count()


    gbc_dict = {}
    for i,j in zip(gbc.index, gbc.values):
        i = str(i)
        gbc_dict[i] = j

    terms = list(queried['product_problems'])
    terms_dict = {}
    for i in terms:
        i = i.replace('[', '')
        i = i.replace(']', '')
        if ',' in i:
            lst = i.split(',')
            for j in lst:
                if j not in terms_dict:
                    terms_dict[j] = 1
                else:
                    terms_dict[j] += 1
        else:
            if i not in terms_dict:
                terms_dict[i] = 1
            else:
                terms_dict[i] += 1

    res = dict(sorted(terms_dict.items(), key = lambda x: x[1], reverse = True)[:5])
    res2 = []

    for i in res:
        top = i+': '+str(res[i])
        res2.append(top)

    date_of_event = queried['date_of_event'][0].date()
    device_manifacturing = queried['device_date_of_manufacturer'][0]
    product_code = queried['product_code'][0]
    days_from_release_to_failure = queried['days_from_release_to_failure'][0]
    days_from_implant_to_failure = queried['days_from_implant_to_failure'][0]
    date_of_implant = queried['date_of_implant'][0]
    brand = queried['brand'][0].split(',')[0]
    manufacturer_name = queried['manufacturer_name'][0]
    generic_name = queried['generic_name'][0]
    in_use = queried.in_use[0]
    failed = queried.failed[0]
    in_use_f = '{:,}'.format(in_use)
    failed_f = '{:,}'.format(failed)
    freq = (failed/in_use) * 100
    frequency = '%.0f%%' % (freq)
    #st.dataframe(queried)
    #st.header("K Number: "+selected)
    col1, col2, col3 = st.columns((5,1,5))

    with col1:
        st.markdown(f'<p style=""><b>Brand: </b>{brand}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Manufacturer: </b>{manufacturer_name}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Generic Name: </b>{generic_name}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Product Code: </b>{product_code}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Products In_use (Mock): </b>{in_use_f}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Products Failed: </b>{failed_f}</p>', unsafe_allow_html=True,)

    with col3:
        st.markdown(f'<p style=""><b>Common Problems: </b></p>', unsafe_allow_html=True,)
        for i in range(len(res)):
            st.write(res2[i])
        #st.write(res2[0])
        #st.write(res2[1])
        #st.write(res2[2])
        #st.write(res2[4])
        #st.write(res2[5])

    
    #st.markdown(' ', unsafe_allow_html=True,)
    st.subheader("Submission Number: "+str(queried.submission_number[0]))
    days = queried['days_from_release_to_failure'][0]
    col1a, col2a, col3a = st.columns((5,1,5))
    with col1a:
        st.markdown(f'<p ><b>Age of Device at Event From First Use (Mock):</b> <span style="color: blue;"><b>{days_from_implant_to_failure}<b></span></p>', unsafe_allow_html=True)
        st.markdown(f'<p><b>Age of Device at Event From Manufacture:</b> <span style="color: blue;"><b>{days}<b></span></p>', unsafe_allow_html=True)
        if treshold != '':
                if freq > treshold:
                    st.markdown(f'<p style="font-size: 26px;"><b>Device Failure Percentage:</b> <span style="color: red;"><b>{frequency}<b></span></p>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<p><b>Device Failure Percentage:</b> <span style="color: blue;"><b>{frequency}<b></span></p>', unsafe_allow_html=True)
    with col3a:
       

        st.markdown(f'<p style=""><b>Device date of Manufacture: </b>{device_manifacturing}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Device date of First Use: </b>{date_of_implant}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Device date of Event: </b>{date_of_event}</p>', unsafe_allow_html=True,)
    st.markdown(' ', unsafe_allow_html=True,)
    st.markdown(' ', unsafe_allow_html=True,)

    #st.subheader("Age of the Device at Event: "+str(days)+" days")
   
    col4, col5, col6 = st.columns((5,1,5))


    with col4:
        fig3 = px.histogram(queried, x="days_from_release_to_failure")

        # add a vertical line to highlight the chosen mdr_report_key

        fig3.add_vline(x=queried.loc[queried["days_from_release_to_failure"] == days, "days_from_release_to_failure"].iloc[0], 
                    line_dash="dash", line_color="red")
        fig3.update_layout(title='Distribution of Device Age at Event From Manufacure date', xaxis_title='Age of Device (Days)', yaxis_title='Count')
        st.plotly_chart(fig3)

    with col6:
        fig4 = px.histogram(queried, x="days_from_implant_to_failure")

        # add a vertical line to highlight the chosen mdr_report_key

        fig4.add_vline(x=queried.loc[queried["days_from_implant_to_failure"] == days, "days_from_implant_to_failure"].iloc[0], 
                    line_dash="dash", line_color="red")
        fig4.update_layout(title='Distribution of Device Age at Event From First Use date', xaxis_title='Age of Device (Days)', yaxis_title='Count')
        st.plotly_chart(fig4)           
        


    st.subheader("General information")
    col7, col8, col9 = st.columns((5,1,5))
    with col7:
        
        df_monthly_counts = queried.groupby(queried["date_of_event"].dt.month).size().reset_index(name="counts")
        df_monthly_counts["month"] = pd.to_datetime(df_monthly_counts["date_of_event"], format="%m").dt.month_name().str.slice(stop=3)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_monthly_counts["month"], y=df_monthly_counts["counts"]))
        fig2.update_layout(title='Distribution of Events per Month', xaxis={'tickmode': 'linear', 'dtick': 1})
        st.plotly_chart(fig2)

    with col9:

        grouped_data = queried.groupby('event_type')['event_type'].count()

        # Create a bar chart
        fig = go.Figure(data=[go.Bar(x=grouped_data.index, y=grouped_data.values)])

        # Set the chart title and axes labels
        fig.update_layout(title='Distribution of Event Types', xaxis_title='Event Type', yaxis_title='Count')
        st.plotly_chart(fig)




    

        
            

