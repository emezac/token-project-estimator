This code is based on https://github.com/AIAnytime/Unit-Economics-of-LLM
This code represents a Streamlit web application for calculating the costs associated with using Large Language Models (LLMs) like GPT-3.5 and GPT-4. Here's a breakdown of its main features and structure:

Purpose: The application helps users estimate the cost of using LLMs based on various parameters such as the number of employees, frequency of use, and the size of prompts and responses.
User Interface: It provides a step-by-step interface guiding users through the process of:
a) Choosing an input method (text entry or PDF upload)
b) Providing the input (either by typing or uploading a PDF)
c) Viewing the results and cost analysis
PDF Processing: The app includes robust PDF text extraction capabilities:

It uses two different libraries (PyPDF2 and pdfplumber) to maximize the chances of successful text extraction from various PDF types.
It provides detailed feedback on the extraction process and offers suggestions if extraction fails.


Cost Calculation: The app calculates costs for different LLM models (GPT-3.5-Turbo, GPT-4, GPT-4o) based on:

Number of employees
Frequency of prompts
Length of prompts and completions
Embedding costs


State Management: It uses Streamlit's session state to manage the flow between different steps and to persist data (like extracted text) between reruns.
Error Handling and User Feedback: The application provides clear error messages and suggestions when things go wrong, enhancing user experience.
Debugging Information: It includes a sidebar with debugging information to help troubleshoot issues during development or user support.
Flexibility: Users can start over at any point, clearing all entered data and returning to the beginning of the process.

Overall, this application serves as a practical tool for organizations or individuals to estimate their potential costs when using LLM services, while also demonstrating good practices in building user-friendly Streamlit applications with complex functionalities like PDF processing and multi-step workflows.
