import streamlit as st 
import tiktoken 
import PyPDF2
import io
import pdfplumber

GPT_35_TURBO_PROMPT_COST = 0.0015/1000 # USD 1.50 % 1M output tokens
GPT_35_TURBO_COMPLETIONS_COST = 0.002/1000 # USD 2.00  % 1M tokens
GPT4_PROMPT_COST = 0.03/1000 # USD 30.00 % 1M tokens
GPT4_COMPLETIONS_COST = 0.06/1000 # USD 60.00  % 1M tokens
GPT4o_PROMPT_COST = 0.005/1000 # USD 5.00 % 1M
GPT4o_COMPLETIONS_COST = 0.0025/1000 # USD 2.50 % 1M
EMBEDDINGS_COST = 0.0001/1000 # USD 0.10 % 1M tokens

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def extract_text_from_pdf(pdf_file):
    text = ""
    error_message = ""
    
    # Try PyPDF2 first
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        if text.strip():
            return text, "PyPDF2"
    except Exception as e:
        error_message += f"PyPDF2 error: {str(e)}\n"
    
    # If PyPDF2 fails or extracts no text, try pdfplumber
    if not text.strip():
        try:
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            if text.strip():
                return text, "pdfplumber"
        except Exception as e:
            error_message += f"pdfplumber error: {str(e)}\n"
    
    # If both methods fail
    if not text.strip():
        return "", error_message
    
    return text, "Combined methods"

def main():
    st.set_page_config(layout="wide")
    st.title("LLM Cost Calculations")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""

    # Debug information
    st.sidebar.write("Debug Info:")
    st.sidebar.write(f"Current Step: {st.session_state.step}")
    st.sidebar.write(f"Extracted Text Length: {len(st.session_state.extracted_text)}")

    # Step 1: Choose input method
    if st.session_state.step == 1:
        st.header("Step 1: Choose Input Method")
        input_method = st.radio("Select input method:", ("Enter Text", "Upload PDF"))
        if st.button("Next"):
            st.session_state.input_method = input_method
            st.session_state.step = 2
            st.experimental_rerun()

    # Step 2: Input text or upload PDF
    elif st.session_state.step == 2:
        st.header("Step 2: Provide Input")
        if st.session_state.input_method == "Enter Text":
            input_text = st.text_area("Enter your text here:", height=300)
            if st.button("Save and Proceed"):
                if input_text:
                    st.session_state.extracted_text = input_text
                    st.session_state.step = 3
                    st.experimental_rerun()
                else:
                    st.error("Please provide input text before proceeding.")
        else:
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            if uploaded_file is not None:
                st.success("PDF file uploaded successfully!")
                if st.button("Extract Text from PDF"):
                    with st.spinner("Extracting text from PDF..."):
                        extracted_text, method = extract_text_from_pdf(io.BytesIO(uploaded_file.getvalue()))
                    
                    if extracted_text:
                        st.session_state.extracted_text = extracted_text
                        st.info(f"Text extracted successfully using {method}!")
                        st.text_area("Extracted text preview:", value=extracted_text[:500], height=200, disabled=True)
                        st.session_state.step = 3
                        st.experimental_rerun()
                    else:
                        st.error("Failed to extract text from the PDF. Error details:")
                        st.text(method)  # method contains error messages in this case
                        st.warning("You can try the following:")
                        st.write("1. Check if the PDF is password-protected or encrypted.")
                        st.write("2. Ensure the PDF contains extractable text (not just images).")
                        st.write("3. Try converting the PDF to a different format and upload again.")
                        st.write("4. As a last resort, you can manually copy and paste the text from the PDF.")

    # Step 3: Process text and show results
    elif st.session_state.step == 3:
        st.header("Step 3: Results and Cost Analysis")
        
        if st.session_state.extracted_text:
            input_text = st.session_state.extracted_text
            token_counts = num_tokens_from_string(input_text, "cl100k_base")
            
            col1, col2, col3 = st.columns([1,1,1])

            with col1:
                st.subheader("Basic Information")
                st.info(f"Your Input: {input_text[:100]}..." if len(input_text) > 100 else input_text)
                st.success(f"Token Count: {token_counts}")
            
            with col2:
                st.subheader("Simulation Parameters")
                option = st.selectbox('Select an LLM:', ('GPT-3.5-Turbo', 'GPT-4','GPT-4o'))
                average_number_of_employees = st.slider("Average number of Employees", 0, 200, 1)
                average_prompt_frequency = st.slider("Average number of Prompt Frequency (Per Day)/Employee", 0, 300, 1)
                average_prompt_tokens = st.slider("Average Prompt Tokens Length", 0, max(300, token_counts), min(token_counts, 300))
                average_completions_tokens = st.slider("Average Completions Tokens Length", 0, 1000, min(token_counts, 1000))
                average_embedding_tokens = st.slider("Average Embedding Tokens Length", 0, max(1000, token_counts), token_counts)

            with col3:
                st.subheader("Cost Analysis")
                if option in ['GPT-3.5-Turbo', 'GPT-4', 'GPT-4o']:
                    if option == 'GPT-3.5-Turbo':
                        prompt_cost = GPT_35_TURBO_PROMPT_COST
                        completions_cost = GPT_35_TURBO_COMPLETIONS_COST
                    elif option == 'GPT-4':
                        prompt_cost = GPT4_PROMPT_COST
                        completions_cost = GPT4_COMPLETIONS_COST
                    else:  # GPT-4o
                        prompt_cost = GPT4o_PROMPT_COST
                        completions_cost = GPT4o_COMPLETIONS_COST
                    
                    llm_cost_per_day = average_number_of_employees * average_prompt_frequency * (
                        average_prompt_tokens * prompt_cost + 
                        average_completions_tokens * completions_cost
                    )
                    embedding_cost_per_day = average_number_of_employees * average_prompt_frequency * average_embedding_tokens * EMBEDDINGS_COST
                    total_cost_per_day = llm_cost_per_day + embedding_cost_per_day
                    total_cost_per_month = total_cost_per_day * 30
                    total_cost_per_year = total_cost_per_month * 12

                    st.success(f"LLM Cost Per Day: {round(llm_cost_per_day, 3)} $")
                    st.success(f"Embedding Cost Per Day: {round(embedding_cost_per_day, 3)} $")
                    st.success(f"Total Cost Per Day: {round(total_cost_per_day, 3)} $")
                    st.success(f"Total Cost Per Month: {round(total_cost_per_month, 3)} $")
                    st.success(f"Total Cost Per Year: {round(total_cost_per_year, 3)} $")

                    st.write("This calculation is based on assumptions. This app does not take any responsibility for the accuracy of the calculation. Please use this app at your own risk.")
                else:
                    st.error("Please select an LLM")
        else:
            st.error("No input text found. Please go back and provide input.")
        
    if st.button("Start Over"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

if __name__ == "__main__":
    main()