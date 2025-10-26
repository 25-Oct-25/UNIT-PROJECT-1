# 🎬 **YouTube Comment & Channel Analyzer — AI Report Generator**

## **Overview**

An interactive **Python CLI project** that analyzes **YouTube video comments and channel data** using **Google Gemini AI** and the **YouTube Data API**.
It detects viewer **sentiment**, identifies **common words**, generates **AI-powered summaries with actionable advice**, and can **analyze entire YouTube channels** fetching channel details, top videos, and generating professional PDF reports.

You can easily **export visual reports** that include channel thumbnails, statistics, sentiment charts, and AI-generated recommendations to improve future content.

---

## ✨ **Features**

* Interactive CLI with colorful text and ASCII art
* English support *(Arabic support coming soon)*
* Sentiment & keyword analysis
* AI-powered summaries and recommendations using Gemini
* Optional PDF report generation
* PDF reports for both **videos** and **channels**
* Secure API keys through environment variables

---

## ⚙️ **Usage**

Run the program:

```bash
python main.py
```

### **Main Menu Options**


1️⃣ Enter the YouTube Video ID
2️⃣ Show short summary of comments
3️⃣ Check overall feeling (sentiment)
4️⃣ See most repeated words or ideas
5️⃣ Get tips to improve next video
6️⃣ Get information about a specific channel *(NEW)*
7️⃣ Generate PDF Report
8️⃣ Exit
 
---

## **Setup**

Install dependencies:

```bash
pip install -r requirements.txt
```

Set up your API keys:

```bash
set YOUTUBE_API_KEY=your_youtube_api_key
set GEMINI_API_KEY=your_gemini_api_key
```

*(Use `export` instead of `set` on macOS/Linux.)*

---

## 📁 **Output Files**

*  `analysis_<video>.json` → AI summary & metrics
*  `analysis_report_<video>.pdf` → Full AI report with insights

---

## 🔗 **API References**

* **YouTube Data API** – [https://developers.google.com/youtube/v3](https://developers.google.com/youtube/v3)
* **Google Gemini API** – [https://ai.google.dev](https://ai.google.dev)

---

## **Author**

**Amwaj Al-Zahrani**








