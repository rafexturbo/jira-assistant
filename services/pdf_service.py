from fpdf import FPDF
from typing import Dict, Any
import json
import io
import pdfplumber
import openai

def json_to_pdf(json_data: Dict[str, Any]) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=10)
    
    def clean_text(text: str) -> str:
        # Replace smart quotes and other special characters
        replacements = {
            '"': '"',  # smart quote to regular quote
            '"': '"',  # smart quote to regular quote
            ''': "'",  # smart apostrophe to regular apostrophe
            ''': "'",  # smart apostrophe to regular apostrophe
            '–': '-',  # en dash to hyphen
            '—': '-',  # em dash to hyphen
            '…': '...' # ellipsis to dots
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def clean_json(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_json(item) for item in obj]
        elif isinstance(obj, str):
            return clean_text(obj)
        return obj
    
    # Clean the JSON data
    cleaned_json = clean_json(json_data)
    pretty_json = json.dumps(cleaned_json, indent=2, ensure_ascii=True)
    
    # Write to PDF
    for line in pretty_json.splitlines():
        pdf.multi_cell(0, 5, line)
    
    try:
        return pdf.output(dest='S').encode('latin1')
    except UnicodeEncodeError as e:
        raise Exception("Error: Some special characters could not be converted. Please check your input text.")

def format_tasks_from_transcript(pdf_bytes: bytes, api_key: str) -> str:
    """
    Extracts and formats action items from a meeting transcript PDF.
    Groups by project and developer, as specified.
    """
    # 1. Extract text from PDF
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # 2. Clean text: remove headers/footers, normalize whitespace
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Simple heuristic: skip lines that look like page numbers or headers/footers
        if line.strip().isdigit() or "Page" in line or "Confidential" in line:
            continue
        cleaned_lines.append(line.strip())
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = "\n".join([l for l in cleaned_text.splitlines() if l.strip()])  # Remove empty lines

    # 3. Use ChatGPT to extract and format action items
    prompt = f"""
You are an expert meeting assistant. Review the following meeting transcript and extract all action items, grouping them by project and then by developer. For each project, list the developer and their action items as bullet points. Use this format:

Project Name 1
Developer A
- Task 1
- Task 2

Developer B
- Task 1

Project Name 2
Developer C
- Task 1

Here is the transcript:
---
{cleaned_text}
---
Return only the formatted action items.
"""

    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.2,
    )
    formatted_output = response.choices[0].message.content.strip()
    return formatted_output 