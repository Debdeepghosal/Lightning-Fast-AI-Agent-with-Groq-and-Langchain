from langchain_groq import ChatGroq
import os

GROQ_API_KEY=os.environ['GROQ_API_KEY']




llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile",max_tokens=4000,)

#########################################################################################################
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool



class CalculatorInput(BaseModel):
    a: int = Field(description="first input")
    b: int = Field(description="second input")



def multiply(a: int,b: int) -> int:
    """square of a number"""
    return int(a)*int(b)


calculator = StructuredTool.from_function(
    func=multiply,
    name="multiply",
    description="multiply two numbers given as input",
    args_schema=CalculatorInput,
    return_direct=True,
)

####################################################################################################

from langchain.tools import StructuredTool

def create_file_tool(file_contents: str, file_path: str) -> str:
    """
    Function that creates a file with the contents
    and file path provided as inputs.
    """
    with open(file_path, "w") as f:
        f.write(file_contents)

    return "File created \n"

create_file_tool = StructuredTool.from_function(create_file_tool)
tools = [ create_file_tool]

#####################################################################################################

from langchain_community.utilities import GoogleSerperAPIWrapper

from langchain_core.tools import Tool

search = GoogleSerperAPIWrapper()



search_tool=Tool(
    name="google search",
    func=search.run,
    description="provides you with google search results",
)
tools.append(search_tool)

#######################################################################################################

import requests
from bs4 import BeautifulSoup


def webscraper(url:str) -> str:
  """
  Function that scrapes the html content of any website given its url as input.
  """
  response=requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  content_str=''
  for h in soup.find_all(['h1','h2','h3']):
    content_str=content_str+","+h.get_text()
  for p in soup.find_all('p'):
    content_str=content_str+","+p.get_text()
  # return soup.get_text()
  if len(content_str) >10000:
    content_str=content_str[:10000]
  return content_str

web_scraping_tool= StructuredTool.from_function(webscraper)
tools.append(web_scraping_tool)

##################################################################################################

import subprocess

def run_terminal(cmd : str) -> str:
  """
  Function that takes shell command asd input and returns the output.
  Example:-
  run_terminal("ls -l") returns 'total 0 -rw-r--r-- 1 root root 0 Mar 30 11:28 test.py'

  """
  cmd_arr=cmd.split(" ")
  result = subprocess.run(cmd_arr, stdout=subprocess.PIPE)
  result=result.stdout.decode()
  return result

run_terminal_tool= StructuredTool.from_function(run_terminal)
tools.append(run_terminal_tool)

#####################################################################################################

from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain import hub




prompt = hub.pull("hwchase17/structured-chat-agent")

agent = create_structured_chat_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True,return_intermediate_steps=True
)


############################################################################################
import os
import time

def delete_files_in_folder(folder_list):
    for file_name in folder_list:
        
        file_path = os.path.join('./', file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


folder_list=os.listdir('.')
if(folder_list != None):
    folder_list.remove('app.py')
    folder_list.remove('__pycache__')
    delete_files_in_folder(folder_list)


#######################################################################################################


import streamlit as st
from langchain.callbacks.streamlit import StreamlitCallbackHandler


st.header('Lightning Fast AI Agent with GROQ and Langchain 🚀', divider='rainbow')


if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke(
            {"input": prompt}, {"callbacks": [st_callback]}
        )
        st.write(response["output"])



import os

def list_files_in_directory(directory_path):
    try:
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        files.remove("app.py")
        return files
    except FileNotFoundError:
        return []

def file_download_link(directory_path, filename):
    with open(os.path.join(directory_path, filename), "rb") as file:
        st.sidebar.download_button(
            label="Download File",
            data=file,
            file_name=filename,
            mime="application/octet-stream"  # Adjust the MIME type based on your file types if necessary
        )

directory_path = './'  

# Sidebar
st.sidebar.title("File Browser")

# List files in the specified directory and allow the user to select one
files = list_files_in_directory(directory_path)

if files:
    selected_file = st.sidebar.selectbox("Select a file", files)
    
    # # Display the selected file content or details
    # st.write(f"You selected: {selected_file}")
    
    # Provide a download button for the selected file
    file_download_link(directory_path, selected_file)
    
    # Example of displaying the content for text files
    # if selected_file.endswith('.txt'):  # Simple filter for text files
    #     with open(os.path.join(directory_path, selected_file), "r") as file:
    #         st.text(file.read())
else:
    st.sidebar.write("No files found in the directory.")


######################################################################################################
