#OpenAi
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

#Llama
from langchain.embeddings import LlamaCppEmbeddings
from langchain.llms import LlamaCpp
from langchain.vectorstores import Chroma
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector

from plannerUtils import load_few_shot_examples
import os


def gen_openai_story(input_list : list[list[str]]):

    #Get Key
    os.environ["OPENAI_API_KEY"] = "" #ENTER YOUR API KEY HERE

    llm = OpenAI(model_name="text-davinci-003",temperature = 0.5, openai_api_key=os.getenv("OPENAI_API_KEY"))
    prompt = PromptTemplate(
        input_variables = ["genre", "subject", "details", "plan"],
        template = "You are a professional {genre} writer. I am a computer scientist. "   +
        "We are collaborating on an experimental writing technique. I will provide you "  +
        "with lists operations that result from a classical planner built on "            +
        "propositional logic, each by a *. For example, move-11-21 is an operation that " +
        "moves an agent from cell (1,1) to cell (2,1) in a grid. You will respond with "  +
        "a fictional story about {subject} where main character takes actions that "      +
        "math the plan operations. Ensure {details}. For example, \"move-11-21 * "        +
        "move-21-31 * move-31-41 * move-41-42\" should give a story where the main "      +
        "character is traveling. Here is your plan: {plan}" 
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

def gen_llama_story(input_list):
    
    llm = LlamaCpp( model_path="LLAMA_MODEL_PATH", verbose=True)

    #prompt to format user's perferences
    story_prompt = PromptTemplate(
        input_variables = ["genre", "subject", "details", "plan"],
        template = "You are a professional {genre} writer. I am a computer scientist. "   +
        "We are collaborating on an experimental writing technique. I will provide you "  +
        "with lists operations that result from a classical planner built on "            +
        "propositional logic, each by a *. For example, move-11-21 is an operation that " +
        "moves an agent from cell (1,1) to cell (2,1) in a grid. You will respond with "  +
        "a fictional story about {subject} where main character takes actions that "      +
        "math the plan operations. Ensure {details}. For example, \"move-11-21 * "        +
        "move-21-31 * move-31-41 * move-41-42\" should give a story where the main "      +
        "character is traveling. Here is your plan: {plan}"  
    )

    #prompt to format few shot examples
    example_prompt = PromptTemplate(input_variables=["prompt", "story"], template="{prompt}\n{story}")

    #from our examples, create an example_selector so we can select
    #semantically relevant examples
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        load_few_shot_examples('./domain_examples/few-shot-examples.json'),
        LlamaCppEmbeddings(model_path="LLAMA_MODEL_PATH"),
        Chroma,
        k=1
    )

    #We go through each input to individually select semantically relevant examples
    for var in input_list:

        story_prompt_text = story_prompt.format(var)
        
        #request the semantically similar examples
        selected_examples = example_selector.select_examples({"prompt": story_prompt_text})

        #create a prompt that positions selected examples above the
        #user prompt template
        few_shot_prompt = FewShotPromptTemplate(
            example_selector=example_selector, 
            example_prompt=example_prompt, 
            input_variables=["input"]
        )
        
        llm_chain = LLMChain(llm=llm, prompt=few_shot_prompt)

        #for each of the user's inputs, apply the input to the
        #few_shot prompt. 
        llm_chain.apply(story_prompt_text)
        llm_chain.run()
