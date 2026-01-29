from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate(
    [
        ("system","You are a helpful assistant"),
        ("user","{question}"),
    ]
)
print(prompt.messages)
