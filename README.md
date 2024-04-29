# llm-coding-eval

Exploring error driven prompting techniques on HumanEval and PythonSaga Datasets

## How to Generate Code

Code can be generated for the problems in the dataset being used by navigating to `human-eval/generation` and running the `human_eval_generation.py` file with the desired paths to the problems/LLM outputs. This will require an OpenAI API key in a .env folder.

## How to Evaluate Code

Reference the instructions in the README in the human-eval folder and use the desired paths to the LLM code outputs. The evaluation outputs will be saved in the Docker container that it is run in.

## How to Check Code Generations

In the `data` folder, the outputs for the 4 prompting methods (attempt, mistake, use_attempt, and use_attempt) can be found. These are for the HumanEval dataset. The outputs for the PythonSaga datasets can be found in the `python_saga` folder