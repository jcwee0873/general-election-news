import tiktoken
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser

from general_election.analyzer.prompts import POS_SENTENCE_EXTRACT_PROMPT, NEG_SENTENCE_EXTRACT_PROMPT


def load_analyze_chain():
    model = ChatOpenAI(model='gpt-3.5-turbo-0125', temperature=0)

    pos_chain = (
        POS_SENTENCE_EXTRACT_PROMPT
        | model
        | StrOutputParser()
    )

    neg_chain = (
        NEG_SENTENCE_EXTRACT_PROMPT
        | model
        | StrOutputParser()
    )

    chain = RunnableParallel(positive=pos_chain, negative=neg_chain)

    return chain



def count_message_tokens(
    messages: list[dict[str, str]] | str, model: str = 'gpt-3.5-turbo-0125'
) -> int:
    
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    encoding = tiktoken.encoding_for_model(model)
    if "gpt-3.5" in model:
        tokens_per_message = 4 
        tokens_per_name = -1 

    elif "gpt-4" in model:
        tokens_per_message = 3
        tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3 
    return num_tokens
