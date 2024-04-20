mistake_prompt = '''Below is an instruction that describes a coding task. Write a reponse that purposefully adds mistakes into the code.\n {problem}'''

use_mistake_prompt = '''Below is an instruction that describes a coding task. \n {problem} \n This is a solution that has mistakes: \n {mistake_attempt} \n
                        Please redo this task and fix the mistakes of the solution above.
                        '''
use_solution_prompt = '''Below is an instruction that describes a coding task. \n {problem} \n This is an attempted solution: \n {attempt} \n
                         If the solution is correct please output it. If the solution is incorrect please redo the task.
                        '''