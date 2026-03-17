import json
import re
import os
import logging
from typing import Dict,Any,List

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_communtiy.vectorstores import AzureSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage,HumanMessage

# import state schema

from backend.src.graph.state import VideoAuditState,ComplianceIssue

# import service

from backend.src.services.video_indexer import VideoIndexerService

## configure the logger

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

## NODE-1 Video indexer
## function resposnible for converting video to text

def index_video_node(state:VideoAuditState) -> Dict[str,Any]:

    '''
    Downloads youtube video from the url
    Uploads to Azure video indexer
    extracts the insights
    '''

    video_url = state.get('video_url')
    video_id_input = state.get('video_id','video_demo')

    logger.info(f"--- Processing NODE -- Video Indexer with youtube url {video_url}")
    local_filename = "temp-audit-video.mp4"

    try:
        vi_service = VideoIndexerService()

        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url,output_path=local_filename)
        else:
            raise Exception("Please provide a valid Youtube URL for auditing")
        
        azure_video_id = vi_service.upload_video(local_path,video_name = video_id_input)
        logger.info(f"--- NODE VIDEO Indexer Video upload successful in Azure -- {azure_video_id}")

        ## cleanup
        if os.path.exists(local_path):
            os.remove(local_path)

        raw_insights = vi_service.wait_for_processing(azure_video_id)

        clean_data = vi_service.extract_data(raw_insights)
        logger.info("--- NODE VIDEO Indexer -- Extraction complete and Data cleaned ")

        return clean_data
    
    except Exception as e:
        logger.error(f"Node indexer failed: {e}")
        return {
            "errors": [str(e)],
            "final_status": "FAIL",
            "transcript": "",
            "ocr_text": [] 
        }
    

## Node 2 Compliance Auditor

def audit_content_node(state: VideoAuditState) -> Dict[str,Any]:
    '''
    Performs RAG to audit the content 
    '''

    logger.info("--- Audit NODE started")
    transcript = state.get("transcript","")

    if not transcript:
        logger.warning("No transcript available.. Skipping audit")
        return {
            "final_status":"FAIL",
            "final_report": "Audit skipped as there is no transcript"
        }
    
    ## initilazie client model

    llm = AzureChatOpenAI(
        azure_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0
    )

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    )

    vector_store = AzureSearch(
        azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key = os.getenv("AZURE_SEARCH_API_KEY"),
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function = embeddings.embed_query
    )

    ocr_text = state.get("ocr_text", [])
    query_text = f"{transcript} {''.join(ocr_text)}"
    docs = vector_store.similarity_search(query_text,k=3)
    retrieved_rules = "\n\n".join([doc.page_content for doc in docs])

    system_prompt = f"""
    YOU ARE A SENIOR BRAND COMPLIANCE AUDITOR
    OFFICIAL REGULATORY RULES:
    {retrieved_rules}
    INSTRUCTIONS:
    1. ANALYZE THE TRANSCRIPT AND OCR TEXT GIVEN BELOW
    2. IDENTIFY ANY VIOLATIONS OF THE RULES
    3. RETURN STRICTLY JSON IN THE FOLLOWING FORMAT

    {{
    "compliance_results":[
    {{
    "category":"claim validation",
    "severity":"CRITICAL",
    "description":"Explanation of the violation..."
    ],
    "status":"FAIL",
    "final_report":"Summary of the findings..."
    }}
    }}

    IF NO VILATIONS ARE FOUND SET "STATUS" TO "PASS" AND "compliance_results" TO []

    """

    user_message = f"""
                VIDEO_METADATA: {state.get('video_metadata',{})} 
                TRANSCRIPT: {transcript}
                ON SCREEN TEXT (OCR): {ocr_text}
                """
    
    try:
        response= llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])

        content = response.content

        if "```" in content:
            content = re.search(r"```(?:json)?(.?)```", content,re.DOTALL).group(1)
        audit_data = json.loads(content.strip())

        return{
            "compliance_results" : audit_data.get("compliance_results",[]),
            "final_status" : audit_data.get("status","FAIL"),
            "final_report" : audit_data.get("final_report","No report generated")
        }
    
    except Exception as e:
        logger.error("Error in audit node", str(e))
        logger.error(f"Raw LLM response: {response.content if response in locals() else None}")

        return {
            "errors": [str(e)],
            "final_status":"FAIL"
        }






