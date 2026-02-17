"""
Centralized prompt templates for all LLM interactions.
"""

# Query Analyzer Prompt
QUERY_ANALYZER_PROMPT = """You are a research planning expert. Your task is to break down a broad research topic into 3-5 focused, searchable sub-questions.

User Query: {query}

Requirements:
- Generate 3-5 sub-questions that cover different aspects of the topic
- Each sub-question should be specific and searchable
- Questions should be complementary and non-overlapping
- Focus on questions that will yield factual, current information

Return your response as a JSON object with this structure:
{{
    "sub_questions": [
        "Question 1",
        "Question 2",
        "Question 3"
    ]
}}
"""

# Result Grader Prompt
RESULT_GRADER_PROMPT = """You are a research quality evaluator. Grade the relevance and quality of this search result for the given query.

Query: {query}

Search Result:
Title: {title}
Snippet: {snippet}
URL: {url}

Score this result from 1-5 based on:
1. Relevance to the query
2. Credibility of the source
3. Freshness and currency of information

Scoring rubric:
5 = Highly relevant, credible source, recent information
4 = Relevant, credible, reasonably current
3 = Moderately relevant, acceptable credibility
2 = Tangentially relevant or questionable credibility
1 = Not relevant or unreliable

Return your response as a JSON object:
{{
    "score": 3,
    "reasoning": "Brief explanation of the score"
}}
"""

# Query Rewriter Prompt
QUERY_REWRITER_PROMPT = """You are a search optimization expert. The previous search query didn't yield good results. Rewrite it to be more effective.

Original Query: {original_query}

Previous Attempt: {rejected_query}

Why it failed: All search results were irrelevant or low quality.

Instructions:
- Use different keywords or phrasing
- Try a different angle or perspective
- Make it more specific or more general as needed
- Consider synonyms and related terms

Return your response as a JSON object:
{{
    "rewritten_query": "Your improved query here"
}}
"""

# Research Synthesizer Prompt
RESEARCH_SYNTHESIZER_PROMPT = """You are a research analyst. Synthesize the following search results into structured research notes.

Sub-Questions and Results:
{graded_results}

Instructions:
- Organize notes by sub-topic
- Extract key facts, statistics, and quotes
- Maintain attribution to sources (include URLs)
- Structure with clear headings
- Be concise but comprehensive
- Only include information from accepted results (score ≥ 3)

Format your notes in markdown with clear sections.
"""

# Article Writer Prompt
ARTICLE_WRITER_PROMPT = """You are a professional content writer. Create a well-structured article based on the research notes provided.

Research Notes:
{research_notes}

Article Parameters:
- Tone: {tone}
- Target Word Count: {word_count}
- Export Format: {export_format}

{human_feedback_section}

Article Structure:
1. Compelling title
2. Introduction (hook and overview)
3. 3-5 main sections with descriptive headings
4. Conclusion (summary and key takeaways)
5. Sources section (list all URLs)

Requirements:
- Include inline citations [1], [2], etc.
- Use clear, engaging language
- Maintain factual accuracy
- Meet the target word count (±10%)
- Apply the specified tone consistently

Write the complete article now.
"""

# Quality Checker Prompt
QUALITY_CHECKER_PROMPT = """You are a content quality auditor. Evaluate this article draft on multiple dimensions.

Article Draft:
{article_draft}

Research Notes (for fact-checking):
{research_notes}

Sources Used:
{sources}

Evaluate on these 4 dimensions (each 0-25 points):

1. **Coverage** (0-25): Does it comprehensively address the research notes?
2. **Factual Consistency** (0-25): Are facts accurate and properly cited?
3. **Structure** (0-25): Is it well-organized with clear flow?
4. **Tone** (0-25): Is the tone appropriate and consistent?

Total Score: Sum of all dimensions (0-100)

Passing threshold: 70/100

Return your response as JSON:
{{
    "coverage_score": 20,
    "factual_score": 22,
    "structure_score": 23,
    "tone_score": 21,
    "total_score": 86,
    "feedback": "Specific, actionable feedback if score < 70, or 'Approved' if ≥ 70"
}}
"""

# HITL Display Template
HITL_DISPLAY_TEMPLATE = """
{'='*80}
ARTICLE DRAFT READY FOR REVIEW
{'='*80}

Quality Score: {quality_score}/100

{article_draft}

{'='*80}
SOURCES
{'='*80}
{sources_list}

{'='*80}
"""
