import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import asyncio
import time
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
import json
import os

st.title("🤖 Multi-Agent Analysis System")

# Setup logging directory
RESULTS_DIR = Path("analysis_results")
RESULTS_DIR.mkdir(exist_ok=True)

def create_log_file():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = RESULTS_DIR / f"analysis_{timestamp}.json"
    return log_file

def save_results(log_file: Path, stage: str, data: dict):
    try:
        if log_file.exists():
            with open(log_file, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}
        
        existing_data[stage] = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        with open(log_file, 'w') as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving results for stage {stage}: {str(e)}")

async def generate_agent_response(prompt_template: PromptTemplate, query: str, agent_id: int):
    try:
        model = ChatOpenAI(temperature=0.7)
        formatted_prompt = prompt_template.format(query=query)
        response = await model.ainvoke(formatted_prompt)
        return str(response), agent_id, None
    except Exception as e:
        return None, agent_id, f"Agent {agent_id} failed: {str(e)}"

async def run_agent_batch(prompt_template: PromptTemplate, query: str, log_file: Path, batch_name: str, num_agents: int = 10):
    start_time = time.time()
    
    tasks = [
        generate_agent_response(prompt_template, query, i) 
        for i in range(num_agents)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Filter out failed responses and collect errors
    successful_responses = []
    errors = []
    
    for response, agent_id, error in results:
        if error:
            errors.append(error)
        else:
            successful_responses.append((response, agent_id))
    
    end_time = time.time()
    
    # Save batch results
    save_results(log_file, f"{batch_name}_batch", {
        'successful_responses': len(successful_responses),
        'errors': errors,
        'execution_time': end_time - start_time,
        'responses': [(str(resp), aid) for resp, aid in successful_responses]
    })
    
    if not successful_responses:
        raise Exception(f"All agents in {batch_name} batch failed: {errors}")
    
    return successful_responses

async def evaluate_responses(responses: List[Tuple[str, int]], log_file: Path, stage: str) -> str:
    try:
        start_time = time.time()
        
        evaluator_prompt = """
        Review these responses and extract the best insights:
        {responses}
        
        Provide a synthesis of the best insights that can be used for further analysis.
        """
        
        formatted_responses = "\n\n".join([f"Response {i}:\n{resp}" for resp, i in responses])
        
        model = ChatOpenAI(temperature=0.3)
        evaluation = await model.ainvoke(evaluator_prompt.format(responses=formatted_responses))
        
        end_time = time.time()
        
        save_results(log_file, f"evaluation_{stage}", {
            'execution_time': end_time - start_time,
            'evaluation': str(evaluation)
        })
        
        return str(evaluation)
    except Exception as e:
        st.error(f"Evaluation failed at stage {stage}: {str(e)}")
        raise

async def process_final_response(insights: str, prompt_template: PromptTemplate, log_file: Path) -> str:
    try:
        start_time = time.time()
        
        final_prompt = """
        Using these key insights:
        {insights}
        
        Provide a comprehensive final answer to the original question.
        """
        
        model = ChatOpenAI(temperature=0.5)
        final_response = await model.ainvoke(final_prompt.format(insights=insights))
        
        end_time = time.time()
        
        save_results(log_file, "final_response", {
            'execution_time': end_time - start_time,
            'response': str(final_response)
        })
        
        return str(final_response)
    except Exception as e:
        st.error(f"Final response generation failed: {str(e)}")
        raise

async def load_prompt_template(file_path: str) -> PromptTemplate:
    prompt_path = Path("prompts") / file_path
    with open(prompt_path, "r") as f:
        template = f.read()
    return PromptTemplate.from_template(template)

async def run_analysis(query: str):
    log_file = create_log_file()
    
    try:
        # Log initial query
        save_results(log_file, "initial_query", {'query': query})
        
        # Load prompt template
        initial_prompt = load_prompt_template("cotv1.md")
        
        # First batch of agents
        st.write("Running first batch of agents...")
        first_batch_results = await run_agent_batch(initial_prompt, query, log_file, "first")
        
        # Evaluate first batch
        st.write("Evaluating first batch results...")
        first_evaluation = await evaluate_responses(first_batch_results, log_file, "first")
        
        # Second batch using insights
        st.write("Running second batch with refined insights...")
        second_batch_results = await run_agent_batch(initial_prompt, first_evaluation, log_file, "second")
        
        # Final evaluation and response
        st.write("Generating final response...")
        second_evaluation = await evaluate_responses(second_batch_results, log_file, "second")
        final_response = await process_final_response(second_evaluation, initial_prompt, log_file)
        
        return final_response, log_file
        
    except Exception as e:
        st.error(f"Analysis pipeline failed: {str(e)}")
        save_results(log_file, "error", {'error': str(e)})
        raise

# Streamlit interface
with st.form("analysis_form"):
    query = st.text_area("Enter your query:", height=100)
    submitted = st.form_submit_button("Analyze")
    
    if submitted:
        with st.spinner("Running multi-agent analysis..."):
            start_time = time.time()
            
            try:
                final_result, log_file = asyncio.run(run_analysis(query))
                end_time = time.time()
                
                st.subheader("Final Analysis")
                st.text(final_result)
                st.text(f"Total execution time: {end_time - start_time:.2f}s")
                st.text(f"Detailed results saved to: {log_file}")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")