#OpenAi
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

#Llama
from langchain import FewShotPromptTemplate
from langchain.embeddings import LlamaCppEmbeddings
from langchain.llms import LlamaCpp
from langchain.vectorstores import Chroma
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector

from plannerUtils import load_few_shot_examples, PlannerType
from planner import *
import os


def gen_openai_story(input_list: list[list[str]], include_state: bool, type):

    operator_explanation = ""
    operator_example = ""
    operator_output = ""
    prompt_template = ""
    rob_state_examples = ["Present Location: (2,1) ; not holding an object ; Object locations: (1,2),(4,2) ; Wall locations: (1,3),(1,4)",
                      "Present Location: (3,1) ; not holding an object ; Object locations: (1,2),(4,2) ; Wall locations: (1,3),(1,4)",
                      "Present Location: (4,1) ; not holding an object ; Object locations: (1,2),(4,2) ; Wall locations: (1,3),(1,4)",
                      "Present Location: (4,2) ; not holding an object ; Object locations: (1,2),(4,2) ; Wall locations: (1,3),(1,4)"]

    block_state_examples = ["Pile 1: c,b Pile 2: a Pile 3: Empty ",
        'Pile 1: b Pile 2: c,a Pile 3: Empty ',
        'Pile 1: Empty Pile 2: c,a Pile 3: b ',
        'Pile 1: Empty Pile 2: a Pile 3: c,b ']
    if include_state:
        operator_explanation +=("I will provide you with a list operations and states that result from a classical planner built on "+
        "propositional logic where the operation and its resulting state are seperated by a '*', and each step in the plan is"+
        " seperated by a newline character (\"\\n\")")
    else:
        operator_explanation += ("I will provide you with lists operations that result from a classical planner built on "+
        " propositional logic, each by a newline character (\"\\n\").")

    if type == PlannerType.block:
        operator_example += (f'\"move-11-21 {"* "+rob_state_examples[0] if include_state else ""} \n'+
                              f'move-21-31 {"* "+rob_state_examples[1] if include_state else ""} \n'+
                              f'move-31-41 {"* "+rob_state_examples[2] if include_state else ""} \n'+
                              f'move-41-42 {"* "+rob_state_examples[3] if include_state else ""} \"')
    else:
        operator_example += (f'\"move-a-1-2 {"* " + block_state_examples[0] if include_state else ""} \n' +
                              f'move-c-1-2 {"* " + block_state_examples[1] if include_state else ""} \n' +
                              f'move-b-1-3 {"* " + block_state_examples[2] if include_state else ""} \n' +
                              f'move-c-2-3 {"* " + block_state_examples[3] if include_state else ""} \"')

    prompt_template = ("You are a professional {genre} writer. I am a computer scientist. " +
        f'We are collaborating on an experimental writing technique. {operator_explanation}' +
        " You will respond with a fictional story about {subject} where main character takes actions that " +
        f'math the plan operations. For example, {operator_example} should {operator_output}' +
        " Ensure {details}. Here is your plan: {plan}")

    print(prompt_template)
    '''
    llm = OpenAI(model_name="text-davinci-003",temperature = 0.5, openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables = ["genre", "subject", "details", "plan"],
        template = prompt_template
    )
    '''
    '''
    Object locations: (1,2),(4,2) 
    Pile 1: Empty, Pile 2: A, B Pile 3: C
    "You are a professional {genre} writer. I am a computer scientist. " +
    "We are collaborating on an experimental writing technique. I will provide you " +
    "with a list operations and states that result from a classical planner built on " +
    "propositional logic where the operation and its resulting state are seperated by a '*', and each operation in the plan is" \
    " seperated by a newline character (\"\\n\"). For example, ***move-11-21 * {state} is an operation that " +
    "moves an agent from cell (1,1) to cell (2,1) in a grid. You will respond with " +
    "a fictional story about {subject} where main character takes actions that " +
    "math the plan operations. For example, \"move-11-21 *  state ""\ " +
    "move-21-31 * move-31-41 * move-41-42\" should give a story where the main " +
    "character is traveling. Ensure {details}. Here is your plan: {plan}"
    '''
    '''
    stories = []
    story_str = ""
    llm_chain = LLMChain(llm = llm, prompt = prompt)
    
    for var in input_list:
        s = llm_chain.run(var)
        stories.append(s)
        story_str += (s + "\n\n")
    '''
    '''
    print(story_str)
    return stories
    '''
def gen_llama_story(input_list, genre='Fiction'):
    llm = LlamaCpp( model_path="./LLaMa/llama.cpp/models/7B/ggml-model-q4_0.bin", verbose=True)

    #prompt to format user's perferences
    story_prompt = PromptTemplate(
        input_variables = ["genre"],
        template = "{genre} short stories:"  
    )
    story_prompt_text = story_prompt.format(genre=genre)

    #prompt to format few shot examples
    example_prompt = PromptTemplate(input_variables=["prompt", "story"], template="{prompt}:\n{story}")

    #from our examples, create an example_selector so we can select
    #semantically relevant examples
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        load_few_shot_examples('./domain_examples/few-shot-examples.json'),
        LlamaCppEmbeddings(model_path="./LLaMa/llama.cpp/models/7B/ggml-model-q4_0.bin"),
        Chroma,
        k=3
    )

    # We go through each input to individually select semantically relevant examples
    running_output = []
    for op in input_list:
        #create a prompt that positions selected examples above the
        #user prompt template
        suff_pre = ''.join([f'{x[0]}:\n{x[1]}\n\n' for x in running_output])
        # map(lambda x: f'{x[0]}:\n{x[1]}\n\n', running_output)

        few_shot_prompt = FewShotPromptTemplate(
            example_selector=example_selector, 
            example_prompt=example_prompt,
            prefix=story_prompt_text,
            suffix=suff_pre+'{input}:\n',
            input_variables=["input"]
        )

        #for each of the user's inputs, apply the input to the
        #few_shot prompt. 
        llm_chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        output = llm_chain({'input':op})
        
        #strip overgeneration from output
        output_text = output['text']
        output_text = output_text.split('\n\n')[0]

        #add output to in-context learning set
        running_output.append((op, output_text))

    return running_output

if __name__ == '__main__':
    story = gen_llama_story(['move-12-11', 'move-11-21'], 'Romance')

    print(story)
