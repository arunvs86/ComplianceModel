import operator
from typing import List,Dict,Any,Annotated,Optional,TypedDict

# defining schema for single compliance result
# Error report structure

class ComplianceIssue(TypedDict):
    category: str
    description: str
    severity: str
    timestamp: Optional[str]


# define the global graph state
# this defines the state that gets passed around in the agentic workflow

class VideoAuditState(TypedDict):
    '''
    Defines the data schema for the langgraph exec content
    Its like a main container which holds all the info about the audit
    right from the initial url to the final report

    '''
    local_file_path: Optional[str]
    video_metadata : Dict[str,Any]
    transcript : Optional[str]
    ocr_text : List[str]

    # analysis output
    # stores the list of all issues found by the AI
    compliance_results: Annotated[List[ComplianceIssue],operator.add]

    final_status: str
    final_report: str

    # stores the system level crashes
    
    errors: Annotated[List[str],operator.add]


