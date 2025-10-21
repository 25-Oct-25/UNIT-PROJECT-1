from transformers import pipeline
from PyPDF2 import PdfReader

class Summarizer:
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def summarize_text(self, text, max_length=150, min_length=40):
        """
        Generate a concise and focused summary of the text using a pretrained transformer model.
        Automatically handles long texts by splitting them into chunks.
        """
        chunk_size = 900
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"\n🔹 Summarizing chunk {i}/{len(chunks)}...")
            prompt = (
                "Summarize this text in 3-4 clear sentences that highlight key causes, effects, and solutions. "
                "Focus on clarity, accuracy, and natural flow:\n\n" + chunk
            )
            try:
                summary = self.summarizer(
                    prompt,
                    max_length=min(len(chunk)//2, 120),
                    min_length=30,
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])
            except Exception as e:
                print(f"Skipped chunk {i} due to error: {e}")

        final_summary = " ".join(summaries)
        return final_summary



'''def summarize_pdf():
    """
    Reads PDF content and uses summarize_text() to summarize it.
    """
    file_path = input("\nEnter the name of your PDF file (e.g., report.pdf): ")

    if not file_path.endswith(".pdf"):
        file_path += ".pdf"

    print("\nReading PDF file...")
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        print(f"Could not open file: {e}")
        return

    pdf_text = ""
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        if text:
            pdf_text += text + "\n"
        print(f"Extracted text from page {i}/{len(reader.pages)}")

    if not pdf_text.strip():
        print("Could not extract text. The PDF might be image-based.")
        return

    summary = summarize_text(pdf_text)

    with open("pdf_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    print("\nSummary saved in pdf_summary.txt")
'''
