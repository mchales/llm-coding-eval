from human_eval.data import write_jsonl, read_problems
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from .prompts import mistake_prompt, use_mistake_prompt, use_solution_prompt

load_dotenv()
OPENAU_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature = 0.8,
                   api_key=OPENAU_API_KEY,
                   model_name="gpt-3.5-turbo")


# Subset of problems for faster/cheaper testing
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSET_EVAL = os.path.join(ROOT, "data\human_eval_subset", "subset_problems.jsonl")

problems = read_problems(SUBSET_EVAL)

# problems = read_problems()

def generate_mistake_completion(problem):
        
        prompt_setup = PromptTemplate(
            input_variables=["problem"],
            template=mistake_prompt
        )
        
        chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=False)
        completion = chain.predict(mistake_prompt=problem)
        
        return completion


def generate_one_completion(problem):
    
    prompt_template = '''{problem}'''
    
    prompt_setup = PromptTemplate(
        input_variables=["problem"],
        template=prompt_template
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=False)
    completion = chain.predict(problem=problem)
    
    
    return completion

num_samples_per_task = 5

mistakes = [
    dict(task_id=task_id, completion=generate_mistake_completion(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples_per_task)
]


samples = [
    dict(task_id=task_id, completion=generate_one_completion(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples_per_task)
]
# write_jsonl("samples.jsonl", samples)

samples_file_path = os.path.join(os.path.dirname(SUBSET_EVAL), "subset_samples.jsonl")

# Write the samples.jsonl file in the same directory as subset_problems.jsonl
write_jsonl(samples_file_path, samples)