import re

def extract_key_info(text):
    """Extract key information from PDF text"""
    try:
        # If text is too long, extract only important parts
        if len(text) > 1500:  # Reduced from 2000 to 1500
            # Extract title and headings
            lines = text.split('\n')
            important_lines = []

            # Keep first 3 lines (usually contains title, author)
            important_lines.extend(lines[:min(3, len(lines))])
            
            # Look for headings and important sentences
            for line in lines[3:]:
                line = line.strip()
                # Keep lines that look like headings
                if re.match(r'^[A-Z0-9][\w\s]{0,50}$', line) or \
                   re.match(r'^[IVX]+\.\s', line) or \
                   re.match(r'^\d+\.\s', line):
                    important_lines.append(line)
                
                # Keep sentences with important keywords
                elif any(keyword in line.lower() for keyword in ['important', 'key', 'significant', 'conclusion', 'result']):
                    important_lines.append(line)
            
            # Join the important lines
            return '\n'.join(important_lines)
        
        return text
    except Exception as e:
        print(f"Error in extract_key_info: {str(e)}")
        # Return original text if there's an error
        return text

def extract_summary_text(text, max_length=1000):
    """Extract a shorter version of text for summarization"""
    if len(text) <= max_length:
        return text

    # Split into paragraphs
    paragraphs = text.split('\n\n')

    # Take first paragraph
    result = paragraphs[0]

    # Add more paragraphs until we reach max_length
    for p in paragraphs[1:]:
        if len(result) + len(p) + 2 <= max_length:  # +2 for the newlines
            result += '\n\n' + p
        else:
            break

    return result

def extract_relevant_context(question, context, max_length=4000):
    """Extraer las partes más relevantes del contexto basado en la pregunta."""
    # Extraer palabras clave de la pregunta
    question_keywords = set(re.findall(r'\b\w{3,}\b', question.lower()))

    # Dividir el contexto en párrafos
    paragraphs = context.split('\n\n')
    relevant_paragraphs = []

    # Mantener párrafos que contengan palabras clave de la pregunta
    for paragraph in paragraphs:
        paragraph_text = paragraph.lower()
        if any(keyword in paragraph_text for keyword in question_keywords):
            relevant_paragraphs.append(paragraph)

    # Si encontramos párrafos relevantes, usarlos como contexto
    if relevant_paragraphs:
        reduced_context = '\n\n'.join(relevant_paragraphs)
        print("Contexto reducido enviado a Gemini:")
        print(reduced_context)
        if len(reduced_context) > max_length:
            reduced_context = reduced_context[:max_length] + "..."
    else:
        # Si no hay párrafos relevantes, usar una versión truncada del contexto original
        reduced_context = context[:max_length] + "..." if len(context) > max_length else context

    return reduced_context