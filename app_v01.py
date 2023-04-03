import streamlit as st
import numpy as np
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UI Mockup - K Numbers", layout='wide')

event = pd.read_csv('event_k_sample_freq.csv')

st.sidebar.title('UI Mockup - K Numbers')

nums = list(event['k_number'])[:1000]
nums.insert(0, '')

selected = st.sidebar.selectbox('Choose a K Number:', nums)
queried = event.query(f'k_number == "{selected}"')
queried.reset_index(inplace=True, drop=True)
#queried['mdr_report_key'] = queried['mdr_report_key'].astype(str)
report_keys = list(queried['mdr_report_key'])
report_keys.insert(0, '')
selected_key = st.sidebar.selectbox('Choose a Report Key Number:', report_keys)
if selected != '':

    #selected_key = st.sidebar.selectbox('Choose a Report Key Number:', report_keys)

#---------------------Data preparations---------------------

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
    days_from_release_to_failure = queried['days_from_release_to_failure']
    product_problems = queried['product_problems']
    brand = queried['brand'][0].split(',')[0]
    manufacturer_name = queried['manufacturer_name'][0]
    generic_name = queried['generic_name'][0]
    frequency = queried['frequency'][0]



    st.header("K Number: "+selected)
    col1, col2, col3 = st.columns((5,1,5))

    with col1:
        st.markdown(f'<p style=""><b>Brand: </b>{brand}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Manufacturer: </b>{manufacturer_name}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Generic Name: </b>{generic_name}</p>', unsafe_allow_html=True,)
        st.markdown(f'<p style=""><b>Product Code: </b>{product_code}</p>', unsafe_allow_html=True,)

    with col3:
        st.markdown(f'<p style=""><b>Common Problems: </b></p>', unsafe_allow_html=True,)
        st.write(res2[0])
        st.write(res2[1])
        st.write(res2[2])

    
    

    if selected_key:
        queried_key = queried.query(f'mdr_report_key == {selected_key}')
        queried_key.reset_index(inplace=True, drop=True)
        days = queried_key['days_from_release_to_failure'][0]
        st.markdown(' ', unsafe_allow_html=True,)
        st.subheader("Report Key: "+str(selected_key))

        col1a, col2a, col3a = st.columns((5,1,5))
        with col1a:
            st.markdown(f'<p style=""><b>Device date of Event: </b>{date_of_event}</p>', unsafe_allow_html=True,)
            st.markdown(f'<p style=""><b>Device date of Manufacture: </b>{device_manifacturing}</p>', unsafe_allow_html=True,)

        with col3a:

            with st.expander("MDR Text"):
                st.write(queried_key['mdr_text_1'][0])
            with st.expander("Manufacturer Text"):
                st.write(queried_key['manufacturer_narrative'][0])


        st.markdown(' ', unsafe_allow_html=True,)
        st.markdown(' ', unsafe_allow_html=True,)

        st.subheader("Age of the Device at Event: "+str(days)+" days")
        st.markdown(f'<p style="font-size: 26px;"><b>Device Failure Percentage:</b> <span style="color: red;"><b>{frequency}<b></span></p>', unsafe_allow_html=True)

        col4, col5, col6 = st.columns((5,1,5))


        with col4:
            fig3 = px.histogram(queried, x="days_from_release_to_failure")

            # add a vertical line to highlight the chosen mdr_report_key

            fig3.add_vline(x=queried.loc[queried["mdr_report_key"] == selected_key, "days_from_release_to_failure"].iloc[0], 
                        line_dash="dash", line_color="red")
            fig3.update_layout(title='Distribution of Device Age at Event', xaxis_title='Age of Device (Days)', yaxis_title='Count')
            st.plotly_chart(fig3)

        with col6:
                
            ecdf = sm.distributions.ECDF(queried['days_from_release_to_failure'])

            # calculate the percentiles
            p0 = queried['days_from_release_to_failure'].min()
            p100 = queried['days_from_release_to_failure'].max()
            selected_device_days = queried.loc[queried["mdr_report_key"] == selected_key, "days_from_release_to_failure"].iloc[0]
            selected_percentile = ecdf(selected_device_days) * 100

            # create the line plot
            fig4 = go.Figure()

            fig4.add_trace(go.Scatter(
                x=[p0, selected_device_days, p100],
                y=[0, selected_percentile, 100],
                mode="lines",
                line=dict(color="blue", width=3),
                name="Selected Device Percentile"
            ))

            fig4.add_trace(go.Scatter(
                x=[p0, p100],
                y=[0, 100],
                mode="lines",
                line=dict(color="gray", width=1),
                fill="tonexty",
                fillcolor="lightgray",
                name="0th to 100th Percentile"
            ))

            fig4.update_layout(title='Percentile of Selected Device', xaxis_title='Age of Device (Days)', yaxis_title='Percentile',
                            xaxis=dict(range=[p0, p100]), yaxis=dict(range=[0, 100]))

            # add vertical line to highlight the selected device
            fig4.add_vline(x=selected_device_days, 
               line_dash="dash", 
               line_color="blue", 
               annotation_text=f"{selected_percentile:.2f}th percentile", 
               annotation_font=dict(size=14, color='red'))

            st.plotly_chart(fig4)
    
    
    if selected_key:
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




    

        
            

