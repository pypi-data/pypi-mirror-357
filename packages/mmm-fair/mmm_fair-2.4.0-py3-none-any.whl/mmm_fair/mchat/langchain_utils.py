from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from bs4 import BeautifulSoup
from mmm_fair.mchat.openai_utils import get_openAI_llm
from mmm_fair.mchat.groq_utils import get_groq_llm
from mmm_fair.mchat.together_utils import get_together_llm
def get_langchain_agent(llm,template="Your are an MMM-fair bot, just say Hi and welcome the user"):
    langchain_agent=None
    try:

        prompt=ChatPromptTemplate.from_messages(template)
        langchain_agent = LLMChain(llm=llm, prompt=prompt)

    except Exception as e:
        print(f"Failed to load langchain agent: {e}.")
        
    return langchain_agent


def summarize_html_report(html_context, langchain_agent: LLMChain, question="", summary="") -> str:
    try:   
        #print(html_context[:200])
        result = langchain_agent.invoke({"context": html_context, "summary": summary, "question": question})
        return result.get("text", "⚠️ No summary returned.")
    except Exception as e:
        return f"⚠️ Could not summarize the report: {e}"


def get_available_llm_providers():
    providers = {}
    try:
        from langchain_groq import ChatGroq 
        providers["groqai"]=get_groq_llm
        providers["groq"]=get_groq_llm
    except ImportError:
        pass
    try:
        from langchain_community.chat_models import ChatOpenAI 
        providers["openai"]=get_openAI_llm  
        providers["chatgpt"]=get_openAI_llm  
    except ImportError:
        pass
    
    try:
        from langchain_together import ChatTogether
        providers["togetherai"]= get_together_llm
        providers["together"]= get_together_llm
    except ImportError:
        pass
    return providers
