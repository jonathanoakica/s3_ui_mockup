import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UI Mockup - K Numbers", layout='wide')

event = pd.read_csv('event_k_numbers_sample.csv')

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




    date_of_event = queried['date_of_event']
    device_manifacturing = queried['device_date_of_manufacturer']
    product_code = queried['product_code'][0]
    days_from_release_to_failure = queried['days_from_release_to_failure']
    product_problems = queried['product_problems']
    brand = queried['brand'][0].split(',')[0]
    manufacturer_name = queried['manufacturer_name'][0]
    generic_name = queried['generic_name'][0]




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

    st.subheader("General information")
    col4, col5, col6 = st.columns((5,1,5))


    with col4:
        
        df_monthly_counts = queried.groupby(queried["date_of_event"].dt.month).size().reset_index(name="counts")
        df_monthly_counts["month"] = pd.to_datetime(df_monthly_counts["date_of_event"], format="%m").dt.month_name().str.slice(stop=3)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df_monthly_counts["month"], y=df_monthly_counts["counts"]))
        fig2.update_layout(title='Seasonality', xaxis={'tickmode': 'linear', 'dtick': 1})
        st.plotly_chart(fig2)

    with col6:

        grouped_data = queried.groupby('event_type')['event_type'].count()

        # Create a bar chart
        fig = go.Figure(data=[go.Bar(x=grouped_data.index, y=grouped_data.values)])

        # Set the chart title and axes labels
        fig.update_layout(title='Distribution of Event Types', xaxis_title='Event Type', yaxis_title='Count')
        st.plotly_chart(fig)


    if selected_key:
        st.subheader("Report Key: "+str(selected_key))
        col7, col8, col9 = st.columns((5,1,5))

        queried_key = queried.query(f'mdr_report_key == {selected_key}')
        queried_key.reset_index(inplace=True, drop=True)
        with col7:
            fig3 = px.histogram(queried, x="days_from_release_to_failure")

            # add a vertical line to highlight the chosen mdr_report_key

            fig3.add_vline(x=queried.loc[queried["mdr_report_key"] == selected_key, "days_from_release_to_failure"].iloc[0], 
                        line_dash="dash", line_color="red")
            fig3.update_layout(title='Distribution Days to failure', xaxis_title='Days To Failure', yaxis_title='Count')
            st.plotly_chart(fig3)

        with col9:
            days = queried_key['days_from_release_to_failure'][0]
            st.markdown(f'<p style=""><b>Days to Failure: </b>{days}</p>', unsafe_allow_html=True,)
            st.markdown(' ', unsafe_allow_html=True,)
            with st.expander("MDR Text"):
                st.write(queried_key['mdr_text_1'][0])
            st.markdown(' ', unsafe_allow_html=True,)
            st.markdown(' ', unsafe_allow_html=True,)
            st.markdown(' ', unsafe_allow_html=True,)
            st.markdown(' ', unsafe_allow_html=True,)
            with st.expander("Manufacturer Text"):
                st.write(queried_key['manufacturer_narrative'][0])
            

