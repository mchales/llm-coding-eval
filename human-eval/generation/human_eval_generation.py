from human_eval.data import write_jsonl, read_problems, stream_jsonl
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


def read_attempts(evalset_file):
    return [task for task in stream_jsonl(evalset_file)]

load_dotenv()
OPENAU_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature = 0.8, # 0.8 temperature was used in the human eval paper
                   api_key=OPENAU_API_KEY,
                   model_name="gpt-3.5-turbo")


ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

PYTHON_SAGA = os.path.join(ROOT, "python_saga")
PYTHON_SAGA_EVAL = os.path.join(PYTHON_SAGA, "basic185.jsonl")
PYTHON_SAGA_EVAL_SUBSET = os.path.join(PYTHON_SAGA, "basic10.jsonl")

SUBSET_EVAL = os.path.join(ROOT, "human_eval_subset", "subset_problems.jsonl")

# Use ROOT for human eval, use PYTHON_SAGA for the python saga problems
MISTAKE = os.path.join(ROOT, "mistake", "mistake_samples.jsonl")
USE_MISTAKE = os.path.join(ROOT, "use_mistake", "use_mistake_samples.jsonl")

ATTEMPT = os.path.join(ROOT, "attempt", "attempt_samples.jsonl")
USE_ATTEMPT = os.path.join(ROOT, "use_attempt", "use_attempt_samples.jsonl")

# Currently we are only doing the problems in the subset
problems = read_problems()
# problems = read_problems(SUBSET_EVAL)
# problems = read_problems(PYTHON_SAGA_EVAL)
# problems = read_problems(PYTHON_SAGA_EVAL_SUBSET)


# attempt_prompt = '''Complete the code of this function.

# Example Input:
# add_weird(x: int, y: int):\n    \"\"\"Add x squared plus y squared\n    >>> add(2, 3)\n    13\n    >>> add(5, 7)\n    74\n    \"\"\"\n

# Example Output:
#     return x**2 + y**2

# Input:
# \n{problem}\n

# Output: \n
#                     '''

# # These are all the prompts being used
# mistake_prompt = '''Complete this task with mistakes. Only return your addition to the existing code. Do not repeat the function header. 
# Example Input:
# add_weird(x: int, y: int):\n    \"\"\"Add x squared plus y squared\n    >>> add(2, 3)\n    13\n    >>> add(5, 7)\n    74\n    \"\"\"\n

# Example Output:
#     return x**2 + y**3

# Input:
# \n{problem}\n

# Output: \n
#                     '''

# use_mistake_prompt = '''You are given a function with a mistake. Fix the mistake and output the correct function code.

# Example Input:
# add_weird(x: int, y: int):\n    \"\"\"Add x squared plus y squared\n    >>> add(2, 3)\n    13\n    >>> add(5, 7)\n    74\n    \"\"\"\n
#     return x**2 + y**3

# Example Output:
#     return x**2 + y**2

# Input:
# \n {problem} \n {mistake} \n
# Output: \n
#                         '''
# use_attempt_prompt = '''You are given an attempt at a function. If the attempt is wrong fix the mistake and output the correct function code.

# Example Input:
# add_weird(x: int, y: int):\n    \"\"\"Add x squared plus y squared\n    >>> add(2, 3)\n    13\n    >>> add(5, 7)\n    74\n    \"\"\"\n

#     return x**2 + y**3

# Example Output:
#     return x**2 + y**2
    
# Example Input:
# add_weird(x: int, y: int):\n    \"\"\"Add x squared plus y squared\n    >>> add(2, 3)\n    13\n    >>> add(5, 7)\n    74\n    \"\"\"\n

#     return x**2 + y**2

# Example Output:
#     return x**2 + y**2

# Input:
# \n {problem} \n {attempt} \n
# Output: \n
#                         '''


mistake_prompt = '''Complete this task with mistakes. Only return your addition to the existing code. Do not repeat the function header. \n {problem}'''

use_mistake_prompt = '''This function has mistakes \n {problem} \n {mistake} \n Redo this task and fix the mistakes of the solution above. \n {problem}
                        '''
use_attempt_prompt = '''This is an attempt to the function: \n {problem} \n {attempt} \n
                         If the solution is correct please output the existing function code. If the solution is incorrect fix and output the function code. \n {problem} 
                        '''

# How many tries the model does on each task
num_samples_per_task = 10

def generate_mistake_completion(problem):
        
        prompt_setup = PromptTemplate(
            input_variables=["problem"],
            template=mistake_prompt
        )
        
        chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=True)
        completion = chain.predict(problem=problem)
        
        
        return completion


def generate_mistake_solution():
    mistakes = [
    dict(task_id=task_id, completion=generate_mistake_completion(problems[task_id]["prompt"]))
    for task_id in problems
    for _ in range(num_samples_per_task)
    ]

    # Write the samples.jsonl file in the same directory as subset_problems.jsonl
    write_jsonl(MISTAKE, mistakes)


def generate_attempt_completion(problem):
    
    prompt='''{problem}'''
    
    prompt_setup = PromptTemplate(
        input_variables=["problem"],
        template=prompt
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=True)
    completion = chain.predict(problem=problem)
    
    
    return completion

def generate_attempt_solution():

    attempts = [
        dict(task_id=task_id, completion=generate_attempt_completion(problems[task_id]["prompt"]))
        for task_id in problems
        for _ in range(num_samples_per_task)
    ]

    # Write the samples.jsonl file in the same directory as subset_problems.jsonl
    write_jsonl(ATTEMPT, attempts)

def generate_attempt_with_mistake(problem, mistake):
    
    prompt_setup = PromptTemplate(
        input_variables=["problem", "mistake"],
        template=use_mistake_prompt
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=True)
    completion = chain.predict(problem=problem, mistake=mistake)

    return completion


def generate_attempt_mistake_solution():
    mistakes = read_attempts(MISTAKE)

    use_mistake_attempts = [
        dict(task_id=mistake["task_id"], completion=generate_attempt_with_mistake(problems[mistake["task_id"]]["prompt"], mistake["completion"]))
        for mistake in mistakes
    ]

    # Write the samples.jsonl file in the same directory as subset_problems.jsonl
    write_jsonl(USE_MISTAKE, use_mistake_attempts)

def generate_attempt_with_attempt(problem, attempt):
    
    prompt_setup = PromptTemplate(
        input_variables=["problem", "attempt"],
        template=use_attempt_prompt
    )
    
    chain = LLMChain(llm=llm, prompt=prompt_setup, verbose=True)
    completion = chain.predict(problem=problem, attempt=attempt)

    return completion


def generate_attempt_attempt_solution():
    attempts = read_attempts(ATTEMPT)

    use_attempt_attempts = [
        dict(task_id=attempt["task_id"], completion=generate_attempt_with_attempt(problems[attempt["task_id"]]["prompt"], attempt["completion"]))
        for attempt in attempts
    ]

    write_jsonl(USE_ATTEMPT, use_attempt_attempts)

if __name__ == "__main__":
    # Generate mistakes
    generate_mistake_solution()

    # Generate attempts
    generate_attempt_solution()

    # Generate attempts using mistakes
    generate_attempt_mistake_solution()

    # Generate attempts using attempts
    generate_attempt_attempt_solution()


    print("Done")