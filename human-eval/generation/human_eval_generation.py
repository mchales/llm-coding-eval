from human_eval.data import write_jsonl, read_problems, read_attempts
import os
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAU_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature = 0.8, # 0.8 temperature was used in the human eval paper
                   api_key=OPENAU_API_KEY,
                   model_name="gpt-3.5-turbo")


# All the directories and file paths, if using windows change the / to \
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBSET_EVAL = os.path.join(ROOT, "data/human_eval_subset", "subset_problems.jsonl")

MISTAKE = os.path.join(ROOT, "data/mistake", "mistake_samples.jsonl")
USE_MISTAKE = os.path.join(ROOT, "data/use_mistake", "use_mistake_samples.jsonl")

ATTEMPT = os.path.join(ROOT, "data/attempt", "attempt_samples.jsonl")
USE_ATTEMPT = os.path.join(ROOT, "data/use_attempt", "use_attempt_samples.jsonl")

# Currently we are only doing the problems in the subset
problems = read_problems(SUBSET_EVAL)

# problems = read_problems()


# These are all the prompts being used
mistake_prompt = '''Complete this task with mistakes. Only return your addition to the existing code. Do not repeat the function header. \n {problem}'''

use_mistake_prompt = '''This function has mistakes \n {problem} \n {mistake} \n Redo this task and fix the mistakes of the solution above. \n {problem}
                        '''
use_attempt_prompt = '''This is an attempt to the function: \n {problem} \n {attempt} \n
                         If the solution is correct please output it. If the solution is incorrect redo the task.
                        '''

# How many tries the model does on each task
num_samples_per_task = 5

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
    
    prompt_template = '''{problem}'''
    
    prompt_setup = PromptTemplate(
        input_variables=["problem"],
        template=prompt_template
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
        dict(task_id=attempt["task_id"], completion=generate_attempt_with_mistake(problems[attempt["task_id"]]["prompt"], attempt["completion"]))
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