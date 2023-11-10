
import streamlit as st
from PIL import Image
import openai
from bardapi import Bard
import pandas as pd
import time
import json
from streamlit_chat import message
import os
import requests


openai.api_key="krishna"
# quest_data="/home/support/Semantic_search_3/Embeddings/quest.csv"

os.environ['_BARD_API_KEY'] = 'krishna'

token='krishna'
session = requests.Session()
session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
session.cookies.set("__Secure-1PSID", os.getenv("_BARD_API_KEY"))



with st.container():
    image1 = Image.open("/var/lib/jenkins/workspace/Python build/test/resources/prodapt_image.png")#prodapt logo
    st.sidebar.image(image1, width=125)
# col1, col2 = st.sidebar.columns(2)

model=st.sidebar.radio(
    "Choose the Model ",
    ('GPT-3.5','Bard')
    
)


# gpt_btn=col1.button("GPT-3.5")
# bard_btn=col2.button("Bard")

# placeholder=st.sidebar.empty()

new_session=st.sidebar.button("New chat")
st.sidebar.title("ProdaptGPT")
text_area_id = 'text'
user_input=st.sidebar.text_area(placeholder="Enter the text here",label="input",label_visibility="hidden",value='',key=text_area_id)
conversation = []
st.sidebar.markdown("---")

response_container=st.container()
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['generated']=[]
    st.session_state['past']=[]
    st.session_state['gen']=[]
    st.session_state['pas']=[]
    st.session_state['buttons']=[]
    st.session_state['active_button'] = None
    st.session_state['history']=""
    st.session_state['gen_b']=[]
    st.session_state['pas_b']=[]
    st.session_state['messages_b']=[]
    st.session_state['gen1_b']=[]
    st.session_state['pas1_b']=[]
    st.session_state['buttons_b']=[]
    st.session_state['active_button_b'] = None
    

def generate_response(prompt):

    st.session_state['messages'].append({"role": "user", "content": prompt})
    st.session_state['generated'].append(prompt)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})
    st.session_state['past'].append(response)
    if(len(st.session_state["generated"])==len(st.session_state["past"])):
        
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
    
   
    with open("/home/support/Semantic_search_3/Embeddings/conversation_history.json", "a") as file:
        json.dump(st.session_state['messages'], file)

def generate(input):
    
    bard = Bard(token=token, session=session, timeout=30)
    # prompt=f"Previous content :{st.session_state['history']}\n + Have knowlwdge of Previous content before answering the question."+"\n"+"question :{user_input}"+"\n"+"answer :"
    if(len(st.session_state['history'])==0):
        prompt=input
    else:
        prompt=input+"don't mention about conversation history, here is the conversation history so far: "+st.session_state['history']
    response = bard.get_answer(prompt)['content']
    st.session_state['messages_b'].append({"role": "user", "content": input})
    st.session_state['messages_b'].append({"role": "assistent", "content": response})
    st.session_state['gen_b'].append(input)
    st.session_state['pas_b'].append(response)
    if(len(st.session_state["gen_b"])==len(st.session_state["pas_b"])):
        
        for i in range(len(st.session_state['gen_b'])):
            message(st.session_state["gen_b"][i], key=str(i)+'bard')
            message(st.session_state["pas_b"][i], is_user=True, key=str(i) + '_user'+'bard')
    
    with open("/home/support/Semantic_search_3/Embeddings/conversation_history_bard.json", "a") as file:
        json.dump(st.session_state['messages_b'], file)
    st.session_state['messages_b']=[]
    
    st.session_state['history']+=f"{input}: {response} "

if(new_session and model=='GPT-3.5'):
    print("success") 
    if(len(st.session_state['generated'])>0):
        print("sucesss")
        st.session_state["gen"].append(st.session_state["generated"])
        st.session_state["pas"].append(st.session_state["past"])
        st.session_state['generated']=[]
        st.session_state['past']=[]
        st.session_state['messages']=[]
        st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]
elif(new_session and model=='Bard'):
    st.session_state['history']=""
    st.session_state['gen1_b'].append(st.session_state['gen_b'])
    st.session_state['pas1_b'].append(st.session_state['pas_b'])
    st.session_state['gen_b']=[]
    st.session_state['pas_b']=[]

if(model=='GPT-3.5'):
    if len(st.session_state["gen"]) > len(st.session_state['buttons']):
        g = len(st.session_state["gen"]) - len(st.session_state['buttons'])
        for i in range(g):
            st.session_state['buttons'].append(False)

    # Display the buttons
    if(len(st.session_state['buttons'])>0):
        for i, button_state in enumerate(st.session_state['buttons']):
            button_label = f"Chat {i + 1}"
            if st.sidebar.button(button_label, key=button_label):
                st.session_state['active_button'] = i

    # Display the corresponding column based on the active button
    active_button = st.session_state['active_button']
    if active_button is not None:
        for i in range(len(st.session_state['gen'][active_button])):
            generated_content = st.session_state["gen"][active_button][i]
            past_content = st.session_state["pas"][active_button][i]
            message(generated_content, key=f"generated_{active_button}"+str(i))
            message(past_content, is_user=True,key=f"past_{active_button}"+ '_user'+str(i))
elif(model=='Bard'):
    if len(st.session_state["gen1_b"]) > len(st.session_state['buttons_b']):
        g = len(st.session_state["gen1_b"]) - len(st.session_state['buttons_b'])
        for i in range(g):
            st.session_state['buttons_b'].append(False)
            
    # Display the buttons
    if(len(st.session_state['buttons'])>0):
        for i, button_state in enumerate(st.session_state['buttons_b']):
            button_label = f"Chat {i + 1}"
            if st.sidebar.button(button_label, key=button_label):
                st.session_state['active_button_b'] = i
                

    # Display the corresponding column based on the active button
    active_button = st.session_state['active_button_b']
    if active_button is not None:
        for i in range(len(st.session_state['gen1_b'][active_button])):
            generated_content = st.session_state["gen1_b"][active_button][i]
            past_content = st.session_state["pas1_b"][active_button][i]
            message(generated_content, key=f"generated_{active_button}"+str(i))
            message(past_content, is_user=True,key=f"past_{active_button}"+ '_user'+str(i))   


if st.sidebar.button("Send") and user_input!="" :
    # st.write(f'<script>document.getElementById("{text_area_id}").value = "";</script>', unsafe_allow_html=True)
    # print(user_input)
    if(model=="GPT-3.5"):
        generate_response(user_input)
    elif(model=="Bard"):
        generate(user_input)
    # placeholder.empty()
    # st.session_state["text"] = ""
    




















    # st.write("Generated:", st.session_state["gen"][active_button])
    # st.write("Past:", st.session_state["pas"][active_button])
    # message(st.session_state["gen"][active_button]) #, key=f"generated_{active_button}")
    # message(st.session_state["pas"][active_button]) #, is_user=True, key=f"generated_{active_button}" + '_user')

#     for i in  range(len(st.session_state["gen"])):
#         button_label = f"Row {i+1}"
#         if st.sidebar.button(button_label):
#         # Display the corresponding column of gen and pas
#             print("hhafsjkddsbjkgl")
#             k=0
#             for j in range(len(st.session_state["gen"][i])):
#                 message(st.session_state["gen"][i][j])
#                 message(st.session_state["past"][i][j])

#     print(len(st.session_state['gen']))
#     print(len(st.session_state['pas']))
# if(len(st.session_state["gen"])>st.session_state['f']):
#     # print(len(st.session_state['gen']),st.session_state['f'],end="?\n")
#     g=len(st.session_state["gen"])-st.session_state['f']
#     for i in range(g):
#         button_label=st.sidebar.button(f"Row {len(st.session_state['buttons'])+1}")
#         st.session_state['buttons'][button_label] = False
#     st.session_state['f']=len(st.session_state['gen'])
#     # print(len(st.session_state['buttons']),st.session_state['f'],end="\\\n")

# if(len(st.session_state['buttons'])>0):
#     for button_label, button_state in st.session_state['buttons'].items():
#         if st.sidebar.button(button_label, key=button_label):
#             st.session_state['buttons'][button_label] = not button_state
            
#     for button_label, button_state in st.session_state['buttons'].items():
#         if button_state:
#             button_index = int(button_label.split()[-1]) - 1
#             st.write("Generated:", st.session_state["gen"][button_index])
#             st.write("Past:", st.session_state["pas"][button_index])
#     for button_label in st.session_state['buttons']:
#         if st.sidebar.button(button_label,key=button_label):
#             # Find the index of the button in the buttons list
#             button_index = st.session_state['buttons'].index(button_label)
#             # Display the corresponding column of gen and pas
#             st.write("Generated:", st.session_state["gen"][button_index])
#             st.write("Past:", st.session_state["pas"][button_index])
# #     
# if(len(st.session_state['past'])>0): 
# if(st.sidebar.button("clear")):
#     # st.write(f'<script>document.getElementById("{text_area_id}").value = "";</script>', unsafe_allow_html=True)
#     input_value = st.session_state.get(text_area_id, "")
#     st.session_state[text_area_id] = ""










