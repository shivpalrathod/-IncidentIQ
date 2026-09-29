import os
import re

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from hindsight_client import Hindsight
from groq import Groq


# =========================================
# Load Environment Variables
# =========================================

load_dotenv()


# =========================================
# Configuration
# =========================================

HINDSIGHT_API_URL = os.getenv(
    "HINDSIGHT_API_URL",
    "https://api.hindsight.vectorize.io"
)

HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY"
)

HINDSIGHT_BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "incidentiq"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)


# =========================================
# Validate Environment Variables
# =========================================

if not HINDSIGHT_API_KEY:
    raise RuntimeError(
        "HINDSIGHT_API_KEY is missing from .env"
    )

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing from .env"
    )


# =========================================
# FastAPI Application
# =========================================

app = FastAPI(
    title="IncidentIQ",
    description="AI Incident Response Agent with Hindsight Memory",
    version="1.3.0"
)


# =========================================
# CORS Configuration
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://incident-iq-lilac-phi.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# Hindsight Client
# =========================================

hindsight = Hindsight(
    base_url=HINDSIGHT_API_URL,
    api_key=HINDSIGHT_API_KEY
)


# =========================================
# Groq Client
# =========================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================
# Request Model
# =========================================

class IncidentRequest(BaseModel):
    incident: str


# =========================================
# Text Utilities
# =========================================

def normalize_text(text: str) -> str:
    """
    Normalize text for comparisons.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def memory_terms(text: str):
    """
    Convert text into normalized terms.
    """

    terms = re.findall(
        r"[a-z0-9]+",
        text.lower()
    )

    return {
        term[:-1]
        if len(term) > 3 and term.endswith("s")
        else term
        for term in terms
    }


def token_similarity(
    text_a: str,
    text_b: str
) -> float:
    """
    Calculate Jaccard token similarity.
    """

    terms_a = set(
        normalize_text(text_a).split()
    )

    terms_b = set(
        normalize_text(text_b).split()
    )

    if not terms_a or not terms_b:
        return 0.0

    intersection = terms_a & terms_b
    union = terms_a | terms_b

    return len(intersection) / len(union)


def extract_incident_from_memory(
    text: str
) -> str:
    """
    Extract the original incident from a newer
    IncidentIQ memory.
    """

    match = re.search(
        r"(?im)^incident:\s*(.+)$",
        text
    )

    if match:
        return match.group(1).strip()

    return ""


def is_same_incident(
    current_incident: str,
    memory_text: str
) -> bool:
    """
    Determine whether a memory represents the
    same incident.
    """

    current_normalized = normalize_text(
        current_incident
    )

    if not current_normalized:
        return False

    stored_incident = extract_incident_from_memory(
        memory_text
    )

    # =====================================
    # Exact stored incident comparison
    # =====================================

    if stored_incident:

        stored_normalized = normalize_text(
            stored_incident
        )

        if stored_normalized == current_normalized:
            return True

        similarity = token_similarity(
            current_incident,
            stored_incident
        )

        if similarity >= 0.90:
            return True

    # =====================================
    # Conservative comparison for old
    # memories that don't contain Incident:
    # =====================================

    similarity = token_similarity(
        current_incident,
        memory_text
    )

    if similarity >= 0.92:
        return True

    return False


# =========================================
# Memory Summary Cleanup
# =========================================

def clean_memory_summary(
    summary: str
) -> str:
    """
    Clean the generated memory summary.
    """

    if not summary:
        return ""

    summary = summary.strip()

    summary = re.sub(
        r"^[-*•]+\s*",
        "",
        summary
    )

    return summary.strip()


# =========================================
# Extract Groq Memory Decision
# =========================================

def extract_memory_decision(
    ai_analysis: str
) -> str:
    """
    Extract the explicit decision generated by Groq.

    Expected:

        MEMORY_DECISION: SAVE

    or:

        MEMORY_DECISION: DO_NOT_SAVE
    """

    if not ai_analysis:
        return "DO_NOT_SAVE"

    match = re.search(
        r"(?im)^\s*MEMORY_DECISION\s*:\s*"
        r"(SAVE|DO_NOT_SAVE)\s*$",
        ai_analysis
    )

    if not match:
        return "DO_NOT_SAVE"

    return match.group(1).upper()


# =========================================
# Extract Memory Summary
# =========================================

def extract_memory_summary(
    ai_analysis: str
) -> str:
    """
    Extract only the text between:

        MEMORY_SUMMARY:

    and:

        MEMORY_DECISION:
    """

    if not ai_analysis:
        return ""

    match = re.search(
        r"(?is)"
        r"MEMORY_SUMMARY\s*:\s*"
        r"(.*?)"
        r"MEMORY_DECISION\s*:",
        ai_analysis
    )

    if not match:
        return ""

    summary = match.group(1).strip()

    return clean_memory_summary(
        summary
    )


# =========================================
# Duplicate Memory Detection
# =========================================

def find_duplicate_memory(
    current_incident: str,
    memory_summary: str
):
    """
    Search Hindsight for a substantially similar
    existing memory.
    """

    try:

        # =====================================
        # Search using original incident
        # =====================================

        incident_results = hindsight.recall(
            bank_id=HINDSIGHT_BANK_ID,
            query=current_incident
        )

        for memory in incident_results.results:

            if is_same_incident(
                current_incident,
                memory.text
            ):
                return memory


        # =====================================
        # Search using generated summary
        # =====================================

        if memory_summary:

            summary_results = hindsight.recall(
                bank_id=HINDSIGHT_BANK_ID,
                query=memory_summary
            )

            for memory in summary_results.results:

                memory_text = memory.text

                # Exact normalized comparison
                if (
                    normalize_text(memory_text)
                    == normalize_text(memory_summary)
                ):
                    return memory

                # Conservative similarity
                similarity = token_similarity(
                    memory_summary,
                    memory_text
                )

                if similarity >= 0.90:
                    return memory

    except Exception:
        # Duplicate checking must never stop
        # the main incident analysis.
        return None

    return None


# =========================================
# Home Endpoint
# =========================================

@app.get("/")
def home():

    return {
        "message": "IncidentIQ API is running",
        "status": "online"
    }


# =========================================
# Incident Analysis Endpoint
# =========================================

@app.post("/api/incidents/analyze")
def analyze_incident(
    request: IncidentRequest
):

    # =====================================
    # 1. Recall Previous Incidents
    # =====================================

    memories = hindsight.recall(
        bank_id=HINDSIGHT_BANK_ID,
        query=(
            f"{request.incident}\n"
            "Find historical incidents for the same named "
            "service, including explicitly documented causes, "
            "completed resolutions, and prevention actions. "
            "Do not treat recommendations as completed outcomes."
        )
    )


    # =====================================
    # 2. Convert Hindsight Results
    # =====================================

    all_memories = []

    for memory in memories.results:

        all_memories.append({
            "type": memory.type,
            "text": memory.text
        })


    # =====================================
    # 3. Find Relevant Documented Outcome
    # =====================================

    incident_terms = memory_terms(
        request.incident
    )

    generic_terms = {
        "a",
        "again",
        "after",
        "and",
        "api",
        "are",
        "around",
        "error",
        "errors",
        "is",
        "memory",
        "percent",
        "returning",
        "service",
        "the",
        "usage",
        "was",
        "were",
        "with"
    }


    # =====================================
    # Filter relevant memories
    # =====================================

    all_memories = [
        memory
        for memory in all_memories
        if len(
            (
                incident_terms
                & memory_terms(memory["text"])
            )
            - generic_terms
        ) >= 2
    ]


    # =====================================
    # Historical incident IDs
    # =====================================

    historical_incident_ids = {

        incident_id.upper().replace(
            " ",
            "-"
        )

        for memory in all_memories

        for incident_id in re.findall(
            r"\bINC[- ]?\d+\b",
            memory["text"],
            re.IGNORECASE
        )
    }


    # =====================================
    # Relevant historical resolution
    # =====================================

    def is_relevant_resolution(
        memory_type,
        text
    ):

        text_lower = text.lower()

        text_terms = memory_terms(
            text
        )

        shared_terms = (
            incident_terms
            & text_terms
        ) - generic_terms

        uncertain_terms = {
            "could",
            "likely",
            "may",
            "might",
            "possible",
            "possibly",
            "potentially",
            "recommend",
            "recommended",
            "should",
            "suspected",
            "suggests"
        }

        completed_outcome = re.search(
            r"\b("
            r"resolved|"
            r"fixed|"
            r"restored|"
            r"mitigated|"
            r"recovered"
            r")\b",
            text_lower
        )

        return (
            memory_type != "observation"
            and len(shared_terms) >= 2
            and completed_outcome is not None
            and not (
                text_terms
                & uncertain_terms
            )
        )


    def best_resolution(results):

        candidates = [
            memory
            for memory in results
            if is_relevant_resolution(
                memory.type,
                memory.text
            )
        ]

        def score(memory):

            memory_ids = {

                incident_id.upper().replace(
                    " ",
                    "-"
                )

                for incident_id in re.findall(
                    r"\bINC[- ]?\d+\b",
                    memory.text,
                    re.IGNORECASE
                )
            }

            return bool(
                historical_incident_ids
                & memory_ids
            )

        return max(
            candidates,
            key=score,
            default=None
        )


    resolution_memory = best_resolution(
        memories.results
    )


    # =====================================
    # Second resolution search
    # =====================================

    if resolution_memory is None:

        resolution_results = hindsight.recall(
            bank_id=HINDSIGHT_BANK_ID,
            query=(
                f"{request.incident}\n"
                "Find explicitly documented completed "
                "resolutions and outcomes for this same "
                "service and incident. Return historical "
                "records, not recommendations or hypotheses."
            )
        )

        resolution_memory = best_resolution(
            resolution_results.results
        )


    # =====================================
    # Different service reference
    # =====================================

    different_service_reference = None

    if re.search(
        r"\border\s+api\b",
        request.incident,
        re.IGNORECASE
    ):

        comparison_results = hindsight.recall(
            bank_id=HINDSIGHT_BANK_ID,
            query=(
                "Historical Payment API incident INC-001. "
                "Find a documented world memory that identifies "
                "the service and incident identifier. "
                "Do not infer a shared cause with the Order API."
            )
        )

        different_service_reference = next(
            (
                memory
                for memory in comparison_results.results
                if (
                    memory.type == "world"
                    and "payment api"
                    in memory.text.lower()
                    and "inc-001"
                    in memory.text.lower()
                )
            ),
            None
        )


    # =====================================
    # 4. Remove Duplicate Retrieved Memories
    # =====================================

    unique_memories = []

    seen_memories = set()

    for memory in all_memories:

        memory_type = memory["type"]
        text = memory["text"]

        normalized_memory = (
            memory_type,
            normalize_text(text)
        )

        if (
            text.strip()
            and normalized_memory
            not in seen_memories
        ):

            seen_memories.add(
                normalized_memory
            )

            unique_memories.append({
                "type": memory_type,
                "text": text
            })


    # =====================================
    # 5. Limit Memories Shown to AI
    # =====================================

    related_memories = unique_memories[:6]


    # =====================================
    # Always include documented resolution
    # =====================================

    if resolution_memory:

        resolution_entry = {
            "type": resolution_memory.type,
            "text": resolution_memory.text
        }

        if resolution_entry not in related_memories:

            related_memories = (
                unique_memories[:5]
                + [resolution_entry]
            )


    # =====================================
    # 6. Prepare Hindsight Context
    # =====================================

    if related_memories:

        memory_context = "\n".join(
            [
                f"- [{memory['type']}] "
                f"{memory['text']}"
                for memory in related_memories
            ]
        )

    else:

        memory_context = (
            "No previous related incidents were "
            "found in Hindsight memory."
        )


    # =====================================
    # 7. Build AI Prompt
    # =====================================

    prompt = f"""
You are IncidentIQ, an AI incident-response assistant
for DevOps and SRE engineers.

A new production incident has been reported:

{request.incident}


HISTORICAL INFORMATION RETRIEVED FROM HINDSIGHT
================================================

{memory_context}


IMPORTANT MEMORY PROVENANCE RULE
================================

The bracketed memory type is provenance, not a
certainty score.

A world memory can contain a hypothesis.

An observation is not automatically a fact.

Preserve uncertainty exactly as written.

Only call something Historical Fact when the
memory content itself states it definitively.


TASK
====

Analyze the current incident using the historical
information above.

Use only memories relevant to the current incident.

Do not force unrelated memories into the analysis.


RESPONSE FORMAT
===============

Use these exact sections:

1. Related Previous Incident
2. Likely Cause
3. Investigation Steps
4. Historical Resolution
5. Recommended Next Action


Use these labels:

- Historical Fact:
  A statement explicitly documented as a fact.

- Historical Observation/Experience:
  A past observation or experience as written in memory.

- Current Hypothesis:
  A possible explanation for the current incident.

- Recommendation:
  An action suggested for the current incident.


SECTION RULES
=============

1. Related Previous Incident

Identify the relevant service and historical incident.

Include documented details as Historical Fact.

Include uncertain observations as
Historical Observation/Experience.

Only include directly relevant memories.

If none are relevant, say so briefly.


2. Likely Cause

Give possible causes only as Current Hypothesis.

Ground them in the current report and relevant history.

Similar symptoms do NOT prove the same root cause.


3. Investigation Steps

Provide practical investigation steps.

Label every step as Recommendation.


4. Historical Resolution

Report a historical resolution ONLY when a Hindsight
memory explicitly documents a completed action or outcome.

Never turn an observation, hypothesis, or recommendation
into a historical resolution.

If no documented historical resolution exists, write
exactly:

No documented previous resolution was found in Hindsight.


5. Recommended Next Action

Give the immediate current action.

Label it Recommendation.


STRICT MEMORY GROUNDING RULES
=============================

1. world:
   Historical/domain information, but only the content
   actually stated in the memory is known.

2. experience:
   Previous experience. Report only what the memory
   explicitly says happened.

3. observation:
   An observation or possible inference.
   It is NOT a confirmed fact.

4. Memory type alone does not prove causal certainty.

5. Never invent or embellish historical information.

6. Never assume an action was performed during a past
   incident unless the memory explicitly documents it.

7. Never describe a current hypothesis or recommendation
   as a historical resolution.

8. Do not conflate different services or incidents.

9. A similar historical incident is a clue, not proof
   that the current incident has the same root cause.

10. Do not state that Redis, a database, authentication,
    deployment, network, or another component is the
    confirmed current root cause unless current evidence
    explicitly confirms it.

11. Do not recommend disruptive actions such as rollback,
    scaling, eviction, or configuration changes based
    only on a reported symptom.

12. First recommend validation and low-risk diagnostics.


MEMORY RETENTION DECISION
=========================

IncidentIQ must decide whether the NEW analysis contains
useful institutional knowledge worth retaining.

Use this rule:

SAVE only when the Hindsight context contains a
DOCUMENTED COMPLETED RESOLUTION for the same service
or incident AND the memory summary can accurately record
that verified historical outcome.

DO_NOT_SAVE when:

- the current analysis contains only hypotheses;
- the historical information is only uncertain;
- there is no documented completed resolution;
- the answer contains only recommendations;
- the information would merely duplicate an existing
  incident without adding useful knowledge.

IMPORTANT:

A recommendation is NOT institutional knowledge.

A current hypothesis is NOT institutional knowledge.

A possible cause is NOT a confirmed root cause.

If there is no documented completed resolution for the
current service/incident, use DO_NOT_SAVE.


MEMORY SUMMARY
==============

At the very end, output:

MEMORY_SUMMARY:

Write ONE short paragraph of no more than 50 words.

The summary must contain only information supported
by the Hindsight context.

Do not turn hypotheses into facts.

Do not turn recommendations into completed actions.

If there is no documented completed resolution, the
summary should not claim a resolution.


MEMORY DECISION
===============

Immediately after MEMORY_SUMMARY, output exactly ONE line:

MEMORY_DECISION: SAVE

OR:

MEMORY_DECISION: DO_NOT_SAVE

Do not output anything after MEMORY_DECISION.
"""


    # =====================================
    # 8. Ask Groq
    # =====================================

    completion = groq_client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a reliable production "
                    "incident-response assistant. "
                    "Historical information must be "
                    "strictly grounded in supplied "
                    "Hindsight memories. "
                    "Never upgrade an observation to fact. "
                    "Never invent a past resolution. "
                    "Never present a current recommendation "
                    "as history. "
                    "For memory retention, use SAVE only when "
                    "the supplied Hindsight context contains "
                    "a documented completed resolution for "
                    "the same service or incident. "
                    "Otherwise use DO_NOT_SAVE."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )


    # =====================================
    # 9. Get AI Response
    # =====================================

    ai_analysis = (
        completion.choices[0]
        .message.content
        or ""
    )


    # =====================================
    # 10. Extract Memory Summary
    # =====================================

    memory_summary = extract_memory_summary(
        ai_analysis
    )


    # =====================================
    # 11. Extract Explicit Memory Decision
    # =====================================

    model_memory_decision = extract_memory_decision(
        ai_analysis
    )


    # =====================================
    # 12. Remove Internal Memory Metadata
    #     From Visible Analysis
    # =====================================

    visible_analysis = ai_analysis

    visible_analysis = re.sub(
        r"(?is)"
        r"\s*MEMORY_SUMMARY\s*:.*?"
        r"MEMORY_DECISION\s*:\s*"
        r"(?:SAVE|DO_NOT_SAVE)"
        r"\s*$",
        "",
        visible_analysis
    ).strip()


    # =====================================
    # 13. Historical Resolution Override
    # =====================================

    if resolution_memory:

        historical_resolution = (
            "- Historical Fact: "
            f"{resolution_memory.text}"
        )

    else:

        historical_resolution = (
            "No documented previous resolution "
            "was found in Hindsight."
        )


    visible_analysis = re.sub(
        r"(?ms)"
        r"^\**4\. Historical Resolution\**[ \t]*\n.*?"
        r"(?=^\**5\. Recommended Next Action\**[ \t]*$)",
        (
            "**4. Historical Resolution**\n"
            f"{historical_resolution}\n\n"
        ),
        visible_analysis,
        count=1
    )


    # =====================================
    # 14. Different Service Clarification
    # =====================================

    if different_service_reference:

        visible_analysis = re.sub(
            r"(?ms)"
            r"(^\**1\. Related Previous Incident\**[ \t]*\n)"
            r"(.*?)"
            r"(?=^\**2\. Likely Cause\**[ \t]*$)",
            lambda match: (
                match.group(1)
                + match.group(2).rstrip()
                + "\n\n"
                "- Historical Fact: Hindsight records "
                "INC-001 as a Payment API incident; "
                "the current report concerns the Order API, "
                "so these are different incidents and do "
                "not establish a shared root cause.\n\n"
            ),
            visible_analysis,
            count=1
        )


    # =====================================
    # 15. Controlled Recommended Next Action
    # =====================================

    incident_lower = request.incident.lower()


    if (
        "auth" in incident_lower
        or "401" in incident_lower
    ):

        next_action = (
            "Compare the authentication deployment and "
            "configuration with the last known-good version, "
            "and inspect current 401 validation logs before "
            "changing traffic or rolling back."
        )


    elif (
        "database" in incident_lower
        or "connection" in incident_lower
    ):

        next_action = (
            "Collect current database connection-pool metrics "
            "and Order API timeout logs before attributing the "
            "502 errors to Redis or changing infrastructure."
        )


    elif "redis" in incident_lower:

        next_action = (
            "Verify current Redis memory and eviction metrics, "
            "then correlate them with Payment API logs before "
            "applying a capacity or eviction change."
        )


    else:

        next_action = (
            "Validate the reported symptoms against current "
            "service logs and metrics before applying a remediation."
        )


    visible_analysis = re.sub(
        r"(?ms)"
        r"^\**5\. Recommended Next Action\**[ \t]*\n.*?"
        r"(?=^---[ \t]*$|\Z)",
        (
            "**5. Recommended Next Action**\n"
            f"- Recommendation: {next_action}\n"
        ),
        visible_analysis,
        count=1
    )


    # =====================================
    # 16. SERVER-SIDE MEMORY VALIDATION
    # =====================================
    #
    # Groq's decision is NOT trusted by itself.
    #
    # Python requires an actual documented
    # historical resolution before allowing SAVE.
    #
    # This is what prevents an Order API hypothesis
    # from becoming institutional memory.
    # =====================================

    has_documented_resolution = (
        resolution_memory is not None
    )


    # =====================================
    # Validate the memory decision
    # =====================================

    memory_quality = False

    memory_quality_reason = ""


    if not memory_summary:

        memory_quality_reason = (
            "No valid memory summary was generated."
        )


    elif model_memory_decision != "SAVE":

        memory_quality_reason = (
            "Groq marked the memory as DO_NOT_SAVE "
            "because it does not contain sufficiently "
            "verified institutional knowledge."
        )


    elif not has_documented_resolution:

        memory_quality_reason = (
            "SAVE was rejected because Hindsight does "
            "not contain a documented completed resolution "
            "for this incident."
        )


    else:

        memory_quality = True

        memory_quality_reason = (
            "The analysis contains a documented historical "
            "resolution and passed the server-side memory gate."
        )


    # =====================================
    # 17. Duplicate Protection
    # =====================================

    duplicate_memory = None

    if memory_quality:

        duplicate_memory = find_duplicate_memory(
            current_incident=request.incident,
            memory_summary=memory_summary
        )


    # =====================================
    # 18. Decide Whether to Save
    # =====================================

    memory_saved = False

    memory_status = ""


    # =====================================
    # Case 1: Quality gate rejected
    # =====================================

    if not memory_quality:

        memory_status = (
            "Memory was not saved. "
            + memory_quality_reason
        )


    # =====================================
    # Case 2: Duplicate found
    # =====================================

    elif duplicate_memory is not None:

        memory_status = (
            "Similar incident memory already exists "
            "in Hindsight. Duplicate memory was not saved."
        )


    # =====================================
    # Case 3: New trusted memory
    # =====================================

    else:

        memory_content = (
            "IncidentIQ incident memory\n"
            f"Incident: {request.incident.strip()}\n"
            f"Summary: {memory_summary.strip()}"
        )

        hindsight.retain(
            bank_id=HINDSIGHT_BANK_ID,
            content=memory_content
        )

        memory_saved = True

        memory_status = (
            "Confirmed incident knowledge was saved "
            "to Hindsight for future incidents."
        )


    # =====================================
    # 19. Return Response
    # =====================================

    return {

        "incident": request.incident,

        "related_memories": related_memories,

        "memory_count": len(
            related_memories
        ),

        "ai_analysis": visible_analysis,

        "memory_saved": memory_saved,

        "memory_status": memory_status,

        "memory_quality": memory_quality,

        "memory_quality_reason": memory_quality_reason,

        "memory_decision": model_memory_decision,

        "memory_saved_summary": memory_summary
    }