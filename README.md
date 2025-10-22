# UNIT-PROJECT-1

Smart Video Assistant system

Overview:

In today’s fast-paced world, people no longer have enough time to watch long videos or follow full visual content, which makes it difficult to extract important information efficiently.
To address this need, the Smart Video Assistant project was designed as an intelligent tool that helps users analyze videos and extract the most important information from them.

The system converts video content into readable text, making it especially useful for individuals with hearing impairments.
It then generates a concise summary and a set of questions and answers that help users quickly understand and review the content later.

Features:
As a user, you should be able to:

Create a new account (Sign Up).
Log in (Login).
Process a new video:
Generate a Transcript of the video content.
Create an intelligent Summary of the video.
Generate Questions and Answers (Q&A) from the extracted text.
Save the results as PDF files within the system.
Automatically receive the files via email.
View the History of all previously processed videos:
Reopen any saved file for review or resend it via email.
Log out securely.

Usage:
To use the Smart Video Assistant system, follow these steps:

Run the system
The start screen displays two options:
Login – to log into an existing account.
Sign Up – to create a new account.

Choose your operation after logging in:
Process a new video – to analyze a new video.
View History – to view previously processed videos.

When selecting “Process a new video”:
Enter the path of the video from your device.
The system supports only MP4 (for video) and WAV (for audio) formats.

After processing, you will see the following options:
Convert to Text – to extract the transcript.
Summarize – to generate a smart summary.
Generate Q&A – to create interactive questions and answers.

After choosing an operation:
You can save the result as a PDF file.
You can also send it directly to your registered email.

View History:
Allows you to review all previously processed files, reopen them, or resend them to your email.

Technical Steps:

Extract Audio from Video
(using FFmpeg)
⬇️
Convert Audio to Text (Transcription)
(using Whisper – OpenAI)
⬇️
Summarize the Text (Summarization)
(using BART Large CNN – Facebook AI)
⬇️
Generate Questions and Answers (Q&A Generation)
(using Gemini 2.5 – Google DeepMind)
⬇️
Create a PDF Report
(using FPDF)
⬇️
Send the Results to the User via Email
(using smtplib)
⬇️
Save User Files and History
(using JSON Files)

