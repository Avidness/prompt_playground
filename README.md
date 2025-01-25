# Prompt Playground
Experimenting with CoA (Chain of Agents), CoT, etc.

https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/

## Installation

1. **Clone**:
   ```bash
   git clone https://github.com/avidness/prompt_playground
   cd prompt_playground
   ```

2. **Install**:
   ```bash
   pip install -r requirements.txt
   ```

3. **API Keys**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Streamlit UI**:
   ```bash
   streamlit run streamlit/<script>.py
   ```

# Questions that LLM's get wrong
From https://arxiv.org/html/2405.19616v2

| Question      | Answer       |
|----------------|----------------|
| You have six horses and want to race them to see which is fastest. What is the best way to do this?   | Race them on a single race track with at least six lanes - the order in which they cross the finish line determines which is the fastest.   |
| Suppose you’re on a game show, and you’re given the choice of three doors: Behind one door is a gold bar; behind the others, rotten vegetables. You pick a door, say No. 1, and the host asks you “Do you want to pick door No. 2 instead?” Is it to your advantage to switch your choice? | It is not an advantage to switch. It makes no difference if I switch or not because no additional material information has been provided since the initial choice. |

## License

Open-source under the MIT license.

