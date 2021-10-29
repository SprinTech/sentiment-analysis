import datetime

import pandas as pd
import seaborn as sns
import requests
import streamlit as st

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Personal diary API')

# Create sidebar element
tab_choice = st.sidebar.selectbox("Select tab you want to consult", ['Coach', 'Client', 'Sentiment analysis'])

# ------ ADD COACH ACTIONS -------- #
if tab_choice == 'Coach':
    coach_action = st.sidebar.selectbox("What do you want to do ?",
                                        ['Add new client', 'Delete client', 'Update client information',
                                         'Get client information', 'Get list of clients'])

    # Add new client to database
    if coach_action == 'Add new client':
        st.markdown('------')
        st.subheader('Add client form')

        # Create form to add client information
        with st.form(key='add_client_form'):
            first_name = st.text_input(label='First name')
            last_name = st.text_input(label='Last name')
            mail = st.text_input(label='Mail')
            phone = st.text_input(label='Phone')
            submit_button = st.form_submit_button(label='Submit')

            if submit_button:
                st.write(f'Client {last_name} {first_name} has been successfully added to database !')

                res = requests.post('http://127.0.0.1:8000/clients/', json={'first_name': first_name,
                                                                            'last_name': last_name,
                                                                            'mail': mail,
                                                                            'phone': phone})

    # Delete client from database
    if coach_action == 'Delete client':
        st.markdown('------')
        st.write('Which client do you want to remove ?')
        user_id = st.number_input(label="User ID", min_value=1, step=1)

        submit_button = st.button(label='Submit')
        if submit_button:
            st.write(f"User {user_id} has been successfully removed from database !")

            res = requests.delete(f'http://127.0.0.1:8000/clients/?id={user_id}')

    # Update client information
    if coach_action == 'Update client information':
        st.markdown('------')
        st.subheader('Update client information form')

        user_id = st.number_input(label="User ID", min_value=1, step=1)
        submit_user_id = st.button(label="Submit")

        if submit_user_id:
            with st.form(key='update_client_form'):
                first_name = st.text_input(label='First name')
                last_name = st.text_input(label='Last name')
                mail = st.text_input(label='Mail')
                phone = st.text_input(label='Phone')
                submit_button = st.form_submit_button(label='Submit')

                if submit_button:
                    st.write(f'Information about client {last_name} {first_name} has been successfully updated !')

                    res = requests.put(f'http://127.0.0.1:8000/clients/{user_id}', json={'first_name': first_name,
                                                                                         'last_name': last_name,
                                                                                         'mail': mail,
                                                                                         'phone': phone})
                    for k, v in res.json().items():
                        st.write(f'{k} : {v}')

    # Display information about clients
    if coach_action == 'Get list of clients':
        st.markdown('------')
        st.subheader('List of clients :')
        st.markdown(' ')
        res = requests.get('http://127.0.0.1:8000/clients/')
        st.dataframe(res.json())

    # Get information about a client
    if coach_action == 'Get client information':
        st.markdown('------')
        user_id = st.number_input(label="User ID", min_value=1, step=1)

        st.subheader('Informations')
        st.markdown(' ')

        res = requests.get(f"http://127.0.0.1:8000/clients/{user_id}")
        for k, v in res.json().items():
            st.write(f'{k} : {v}')

# ------ ADD CLIENT ACTIONS ------ #
if tab_choice == 'Client':
    client_action = st.sidebar.selectbox("What do you want to do ?",
                                         ['Add new post', 'Update today post', 'Read posts'])

    # Add new post to database
    if client_action == 'Add new post':
        st.markdown('------')

        user_id = st.text_input(label='Your User ID')

        if user_id:
            st.subheader('How do you feel today ? Write all you are thinking about !')
            user_text = st.text_input(label='Your message')

            if user_text:
                res = requests.post(f'http://127.0.0.1:8000/clients/{user_id}/post/',
                                    json={'text': user_text})
                st.write('You message has been successfully registered. See you tomorrow ! :)')

    # Update old post
    if client_action == 'Update today post':
        st.markdown('------')

        user_id = st.text_input(label='Your User ID')

        if user_id:
            st.subheader('Which message do you want to update ?')

            user_text = st.text_input(label='Your message')

            if user_text:
                res = requests.put(f'http://127.0.0.1:8000/clients/{user_id}/post/',
                                   json={'text': user_text})

                st.write('Your message has been successfully updated !')

    # Read all post that have been written
    if client_action == 'Read posts':
        st.markdown('------')
        st.subheader('Which message do you want to check ?')

        user_id = st.text_input(label='Your User ID')

        if user_id:
            start_date = st.date_input('Start date', datetime.date.today())
            end_date = st.date_input('End date', datetime.date.today())

            submit_button = st.button(label='Submit')

            if submit_button:
                res = requests.get(f'http://127.0.0.1:8000/clients/{user_id}/post/')
                df = pd.DataFrame(res.json())
                df = df.loc[(df['date_created'] <= str(end_date)) & (df['date_created'] >= str(start_date))]
                st.dataframe(df)

# ------ ADD SENTIMENT ANALYSIS PLOT ------ #
if tab_choice == 'Sentiment analysis':
    sentiment_analysis_action = st.sidebar.selectbox("Which wheel of emotion do you want to check",
                                                     ['Global wheel of emotion', 'Individual wheel of emotion'])

    # Check global wheel of emotion
    if sentiment_analysis_action == 'Global wheel of emotion':
        st.markdown('------')

        start_date = st.date_input('Start date', datetime.date.today())
        end_date = st.date_input('End date', datetime.date.today())

        submit_button = st.button(label='Submit')

        if submit_button:
            res = requests.get("http://127.0.0.1:8000/clients/posts/")
            df = pd.DataFrame(res.json())
            df = df.loc[(df['date_created'] <= str(end_date)) & (df['date_created'] >= str(start_date))]
            sns.countplot(x='sentiment', data=df)
            st.subheader(f"Mood trend between the {start_date} and the {end_date}")
            st.pyplot()

    # Check global wheel of emotion
    if sentiment_analysis_action == 'Individual wheel of emotion':
        st.markdown('------')
        st.write('From which user do you want to check wheel of emotion ?')

        user_id = st.number_input(label="User ID", min_value=1, step=1)

        if user_id:
            start_date = st.date_input('Start date', datetime.date.today())
            end_date = st.date_input('End date', datetime.date.today())

            submit_button = st.button(label='Submit')

            if submit_button:
                res = requests.get(f'http://127.0.0.1:8000/clients/{user_id}/post/')
                df = pd.DataFrame(res.json())
                df = df.loc[(df['date_created'] <= str(end_date)) & (df['date_created'] >= str(start_date))]
                sns.countplot(x='sentiment', data=df)
                st.subheader(f"Mood trend for user {user_id} between the {start_date} and the {end_date}")
                st.pyplot()
