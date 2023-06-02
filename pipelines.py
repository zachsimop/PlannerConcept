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
from planner import *
from plannerUtils import *
import os


def gen_openai_story(input_list: list[list[str]], include_state: bool, type):

    if include_state:
        operator_explanation = (
                    "I will provide you with a list operations and states from a classical planner built on " +
                    "propositional logic where the operation and its resulting state are seperated by a '*', and each step in the plan is" +
                    " seperated by a newline character (\"\\n\")")
    else:
        operator_explanation = (
                    "I will provide you with lists operations that result from a classical planner built on " +
                    " propositional logic, each by a newline character (\"\\n\").")


    if type == PlannerType.del_rob:
        P = Planner(PlannerType.del_rob)
        a = State({'r11': True})
        b = State({'r42': True})
        P.make_plan_astar([a, b])
        operator_example =  P.format_plan(del_rob_state_format, include_state)
        operator_output = "give a story where the main character is traveling."


    else:
        P = Planner(PlannerType.block)
        a = [['A', 'C', 'B'], [], []]
        b = [[], [], ['A', 'C', 'B']]
        P.make_plan_astar([a, b])
        operator_example = P.format_plan(block_state_format, include_state)
        operator_output = "give a story where characters a, b, and c are traveling between locations denoted by each pile."

    prompt_template = ("You are a professional {genre} writer. I am a computer scientist. " +
        f'We are collaborating on an experimental writing technique. {operator_explanation}' +
        " You will respond with a fictional story about {subject} where main character takes actions that " +
        f'math the plan operations. For example, \"{operator_example}\" should {operator_output}' +
        " Ensure {details}. Here is your plan: {plan}")

    print(prompt_template)

    llm = OpenAI(model_name="text-davinci-003",temperature = 0.5, openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables = ["genre", "subject", "details", "plan"],
        template = prompt_template
    )

    stories = []
    story_str = ""
    llm_chain = LLMChain(llm = llm, prompt = prompt)
    
    for var in input_list:
        s = llm_chain.run(var)
        stories.append(s)
        story_str += (s + "\n\n")
    print(story_str)
    return stories

def gen_llama_story(input_list, genre, subject, include_state=False):
    llm = LlamaCpp(model_path="./LLaMa/llama.cpp/models/7B/ggml-model-q4_0.bin",
                   verbose=True,
                   max_tokens = 100,
                   n_ctx = 2048,
                   stop=['\n'])

    #prompt to format few shot examples
    if include_state:
        prompt_template = 'Write a {genre} short story about {subject}:\n\n{op1} * {state1}\n{story1}\n\n{op2} * {state2}\n{story2}\n\n{op3} * {state3}\n{story3}\n\n{op4} * {state4}\n{story4}\n\n\n'
        input_variables=["genre",
                         "subject",
                         "op1", "op2", "op3", "op4",
                         "state1", "state2", "state3", "state4",
                         "story1", "story2", "story3", "story4"]
    else:
        prompt_template = 'Write a {genre} short story about {subject}:\n\n{op1}\n{story1}\n\n{op2}\n{story2}\n\n{op3}\n{story3}\n\n{op4}\n{story4}\n\n\n'
        input_variables=["genre",
                        "subject",
                        "op1", "op2", "op3", "op4",
                        "story1", "story2", "story3", "story4"]

    example_prompt = PromptTemplate(input_variables=input_variables,
                                    template=prompt_template)

    #from our examples, create an example_selector so we can select
    #semantically relevant examples
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        load_few_shot_examples('./domain_examples/few-shot-examples.json'),
        LlamaCppEmbeddings(model_path="./LLaMa/llama.cpp/models/7B/ggml-model-q4_0.bin"),
        Chroma,
        k=1
    )

    few_shot_prompt = FewShotPromptTemplate(
            example_selector=example_selector, 
            example_prompt=example_prompt,
            suffix='Write a {genre} short story about {subject}:\n\n{story}',
            input_variables=["genre", "subject", "story"]
        )

    # We go through each input to individually select semantically relevant examples
    running_output = []
    for op in input_list:
        #for each of the user's inputs, apply the input to the
        #few_shot prompt. 
        llm_chain = LLMChain(llm=llm, prompt=few_shot_prompt)
        output = llm_chain({'genre' : genre,
                            'subject' : subject,
                            'story' : ''.join([f"{x[0]}:\n{x[1]['text']}\n\n" for x in running_output]) + op + '\n'})

        #add output to in-context learning set
        running_output.append((op, output))
    
    return running_output

if __name__ == '__main__':
    story = gen_llama_story(['move-12-11 * Present Location: (1,1) ; not holding an object ; Object locations: (1,1); Wall locations: (2,4),(1,4)',
                             'pickup-11 * Present Location: (1,1) ; holding an object ; Object locations: ; Wall locations: (2,4),(1,4)',
                             'move-11-12 * Present Location: (1,2) ; holding an object ; Object locations: ; Wall locations: (2,4),(1,4)',
                             'dropoff-12 * Present Location: (1,2) ; not holding an object ; Object locations: (1,2); Wall locations: (2,4),(1,4)'],
                             'fantasy', 'a jewel-encrusted dragon', include_state=True)

    print(''.join([f"{p[0]}:\n{p[1]['text']}\n\n" for p in story]))
