def determine_routing_intent(query: str) -> str:
    """
    Analyses the user query and returns a routing decision string.

    Returns:
        "rag_mode"     — query relates to company documents / HR / policy content
        "general_mode" — query is a general knowledge / conversational request
    """

    rag_keywords = [
        # HR & Policy
        "policy",
        "policies",
        "leave",
        "handbook",
        "onboarding",
        "document",
        "documents",
        "company",
        "vacation",
        "benefits",
        "hr",
        "employee",
        "employees",
        "pto",
        "holiday",
        "holidays",
        "reimbursement",
        "payroll",
        "pay",
        "salary",
        "compensation",
        "expense",
        "expenses",
        # Work arrangements
        "remote",
        "work from home",
        "wfh",
        "hybrid",
        "office",
        "attendance",
        # Compliance & Legal
        "code of conduct",
        "compliance",
        "legal",
        "contract",
        "agreement",
        "nda",
        "termination",
        "resignation",
        "notice period",
        # Benefits & Perks
        "insurance",
        "health",
        "dental",
        "vision",
        "401k",
        "retirement",
        "bonus",
        "appraisal",
        "performance review",
        # General document signals
        "according to",
        "as per",
        "stated in",
        "mentioned in",
        "refer to",
        "in the document",
        "in the policy",
        "guideline",
        "guidelines",
        "procedure",
        "procedures",
        "rule",
        "rules",
        "regulation",
        "regulations",
    ]

    query_lower = query.lower()

    if any(keyword in query_lower for keyword in rag_keywords):
        return "rag_mode"

    return "general_mode"