import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import asyncio
import time
from pathlib import Path

st.title("🧠🖥️")

async def load_prompt_template(file_path: str) -> PromptTemplate:
    prompt_path = Path("prompts") / file_path
    with open(prompt_path, "r") as f:
        template = f.read()
    return PromptTemplate.from_template(template)

async def generate_response(prompt_template: PromptTemplate, query: str):
    start_time = time.time()
    model = ChatOpenAI(temperature=0.7)
    formatted_prompt = prompt_template.format(query=query)
    response = await model.ainvoke(formatted_prompt)
    end_time = time.time()
    execution_time = end_time - start_time
    return str(response), execution_time

async def process_prompts(query: str):
    # Load both prompt templates
    cot_v1 = await load_prompt_template("cotv1.md")
    cot_v2 = await load_prompt_template("cotv2.md")
    
    # Run both prompts concurrently
    results = await asyncio.gather(
        generate_response(cot_v1, query),
        generate_response(cot_v2, query)
    )
    
    return results

with st.form("my_form"):
    text = st.text_area(
        "Enter query:",
        "",
    )
    submitted = st.form_submit_button("Submit")
    if submitted:
        # Run async code in sync context
        results = asyncio.run(process_prompts(text))
        
        # Display results
        st.subheader("Chain of Thought v1")
        response_v1, time_v1 = results[0]
        st.info(response_v1)
        st.text(f"Execution time: {time_v1:.2f}s ({time_v1*1000:.0f}ms)")
        
        st.subheader("Chain of Thought v2")
        response_v2, time_v2 = results[1]
        st.info(response_v2)
        st.text(f"Execution time: {time_v2:.2f}s ({time_v2*1000:.0f}ms)")