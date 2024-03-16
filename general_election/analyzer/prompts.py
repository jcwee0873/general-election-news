from langchain.prompts import ChatPromptTemplate

POS_SENTENCE_EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ('system', 'You are an AI aide who analyzes news articles for {target}(election candidates).'),
    ('user', """Extract the positive aspect sentences from article related to {target}'s reputation. Considering Sarcasm. If not contains any positive sentences return 'none'.
Article: {article}
Sentences: """)
])

NEG_SENTENCE_EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ('system', "You are an AI aide works for '{target}'(election candidates), specifically focusing on analyzing article coverage to aid in the election."),
    ('user', """Extract the negative aspect sentences from article related to {target}'s reputation. Considering Sarcasm. If not contains any negative sentence return 'none'.
Article: {article}
Sentences: """)
])