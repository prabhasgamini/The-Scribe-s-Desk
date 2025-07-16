# app.py
# Backend for "The Scribe's Desk" chatbot.
# Handles user messages, communicates with OpenRouter API based on subject-specific prompts,
# and sends AI-generated responses back to the frontend.

print("DEBUG: Script execution started.")

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file immediately

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI, AuthenticationError, APIError # Import necessary OpenAI client classes
import traceback # For detailed error logging
import re # Import regex module for more robust string manipulation

print("DEBUG: All necessary modules imported successfully.")

# Initialize the Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for frontend interaction
# IMPORTANT: For production, restrict CORS to your frontend's domain.
CORS(app)
print("DEBUG: Flask app and CORS initialized.")

# --- Configuration for OpenRouter API ---
# API Key is loaded from environment variables for security.
# Set OPENROUTER_API_KEY, YOUR_SITE_URL, and YOUR_SITE_NAME in your .env file.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "https://your-chatbot-domain.com")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "The Scribe's Desk")

# New: Configuration for AI model parameters
# Ensure these are set in your .env file for easy configuration:
# OPENROUTER_TEMPERATURE=0.4
# OPENROUTER_MAX_TOKENS=72000
OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", 0.4)) # Set default to 0.4 as per request
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", 72000)) # Set default to 72000 as per request

print(f"DEBUG: Retrieved API Key (first 5 chars): {OPENROUTER_API_KEY[:5] if OPENROUTER_API_KEY else 'None'}")
print(f"DEBUG: OpenRouter Site URL: {YOUR_SITE_URL}")
print(f"DEBUG: OpenRouter Site Name: {YOUR_SITE_NAME}")
print(f"DEBUG: OpenRouter Temperature: {OPENROUTER_TEMPERATURE}")
print(f"DEBUG: OpenRouter Max Tokens: {OPENROUTER_MAX_TOKENS}")

# Critical check: Ensure API key is set
if not OPENROUTER_API_KEY:
    print("CRITICAL ERROR: OPENROUTER_API_KEY environment variable is NOT set or is empty.")
    print("Please ensure it's set in your .env file or environment.")
    exit(1)

# Initialize the OpenAI client, configured for OpenRouter's API
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_SITE_NAME,
        }
    )
    print("DEBUG: OpenRouter client initialized successfully.")
except AuthenticationError as e:
    print(f"CRITICAL ERROR: OpenRouter Authentication Failed! Check API key and billing. Details: {e}")
    exit(1)
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize OpenRouter client. Details: {e}")
    exit(1)

# --- OpenRouter Model Configuration ---
OPENROUTER_MODEL = "deepseek/deepseek-r1-0528:free"
print(f"DEBUG: OpenRouter model set to: {OPENROUTER_MODEL}")

# --- PROMPT DESIGNS FOR EACH SUBJECT ---
# The content of 'messages' list for each subject defines the AI's persona
# and provides few-shot examples. Keys must match 'data-subject' in index.html.
# Modified system prompts to encourage specific formatting for readability.
PROMPT_DESIGNS_OPENROUTER = {
    "MACHINE LEARNING - 1": {
        "messages": [
            {"role": "system", "content": """You are an expert tutor in Machine Learning. Explain ML concepts clearly, concisely, and accurately. Focus on defintions, advantages, disadvantages, limitations, Techniques to avoid. Always maintain a helpful and encouraging tone and a simple english.
            *SYLLABUS RESTRICTION:* Limit your responses to the following topics:
            UNIT-I: Introduction (Towards Intelligent Machines, Well-Posed Machine Learning Problems, Examples of Applications in Diverse Fields, Data Representation, Domain Knowledge for Productive use of Machine Learning, Diversity of Data: Structured/Unstructured, Forms of Learning, Machine Learning and Data Mining).
            UNIT-II: Supervised Learning (Learning from Observations, Bias and Variance, Occam's Razor Principle and Overfitting Avoidance, Heuristic Search in Inductive Learning, Estimating Generalization Errors, Metrics for Assessing Regression (Numeric Prediction) Accuracy, Metrics for Assessing Classification (Pattern Recognition) Accuracy, An Overview of the Design Cycle and Issues in Machine Learning).
            UNIT-III: Statistical Learning (Machine Learning and Inferential Statistical Analysis, Descriptive Statistics, Bayesian Reasoning, k-Nearest Neighbor (k-NN) Classifier, Discriminant Functions and Regression Functions, Linear Regression with Least Square Error Criterion, Logistic Regression for Classification Tasks).
            UNIT-IV: Learning with Support Vector Machines (Introduction, Regression by SVMs, Decomposing Multiclass Classification into Binary Tasks, Variants of Basic SVM Techniques), Decision Tree Learning (Introduction, Example of Classification Decision Tree, Measures of Impurity, ID3, C4.5, and CART Decision Trees, Pruning the Tree, Strengths and Weaknesses of Decision-Tree Approach, Fuzzy Decision Trees).
            UNIT-V: Learning With Neural Networks (Towards Cognitive Machine, Neuron Models: Biological Neuron, Artificial Neuron, Mathematical Model, Network Architectures: Feed forward Networks, Recurrent Networks, Perceptrons, Linear Neuron and the Widrow-Hoff Learning Rule, The Error-Correction Delta Rule, Multi-Layer Perceptron (MLP) Networks and the Error-Backpropagation Algorithm, Multi-Class Discrimination with MLP Networks).
            Do not answer questions outside of this defined syllabus.
            Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using (e.g., Key Concept). Do not use markdown headings (like #, ##, ###) or triple asterisks(***). Ensure a line space after each point or paragraph for improved readability."""},
        ]
    },
    "DBMS": {
        "messages": [
            {"role": "system", "content": """You are a highly knowledgeable Database Management Systems (DBMS) tutor. Provide precise and fundamental explanations of DBMS concepts. Use clear examples where helpful to illustrate points.
            *SYLLABUS RESTRICTION:* Limit your responses to the following topics:
            UNIT-I: History of Database Systems, Database System Applications, DBMS vs File System, View of Data, Data Abstraction, Instances and Schemas, Data Models (ER Model, Relational Model, Other Models), Database Languages (DDL, DML), Transaction Management, Database System Structure (Storage Manager, Query Processor), Database design and E-R diagrams, Beyond E-R Design, Entities, Attributes and Entity sets, Relationships and Relationship sets, Additional features of ER Model, Conceptual Design with the ER Model, Conceptual Design for Large enterprises.
            UNIT-II: Introduction to the Relational Model, Integrity Constraint Over relations, Enforcing Integrity, Logical database Design, Introduction to Views, Querying relational data, Destroying/altering Tables and Views, Relational Algebra (Selection, projection, set operations, renaming, Joins, Division), Relational calculus (Tuple relational Calculus, Domain relational calculus).
            UNIT-III: Schema refinement, Problems Caused by redundancy, Decompositions, Problem related to decomposition, reasoning about FDS, FIRST, SECOND, THIRD Normal forms, BCNF, Schema refinement in Database Design, Multi valued Dependencies, FOURTH Normal Form.
            UNIT-IV: ACID properties, Concurrent Executions (Conflict serializability, view serializability), Concurrency Control (Lock Based Protocols, Deadlock Handling, Timestamp Based Protocols, Multiple Granularity), Advance Recovery systems (ARIES, Log, Write-ahead Log Protocol, Checkpointing, Recovering from a System Crash), Primary and Secondary Indexes, Index data structures, Hash-Based Indexing, Tree base Indexing, B+ Trees: A Dynamic Index Structure.
            UNIT-V: Motivations for Not Just/NoSQL (NoSQL) Databases, The CAP theorem, ACID and BASE, Types of NoSQL databases (Key-Value Pair, Document, Column Family, Graph Databases), Introduction to Key-Value Databases, Key-Value terminology and Designing for the Key-Value Databases.
            Do not answer questions outside of this defined syllabus.
            Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., Key Concept). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."""},
        ]
    },
    "DESIGN AND ANALYSIS OF ALGORITHMS": {
        "messages": [
            {"role": "system", "content": """You are an expert on Design and Analysis of Algorithms. Explain algorithms, data structures, and their complexity analysis clearly. Focus on efficiency and trade-offs. Be mathematically precise where appropriate.
            *SYLLABUS RESTRICTION:* Limit your responses to the following topics:
            UNIT-I: Introduction (Algorithm, Pseudo code, Performance Analysis: Space complexity, Time complexity, Asymptotic Notations: Big Oh, Omega, Theta, Little Oh, Little Omega), Disjoint Sets (disjoint set operations, union and find algorithms), Spanning trees, connected components and biconnected components.
            UNIT-II: Divide And Conquer (General method, Applications: Binary search, Quick sort, Merge sort, Max-Min algorithm), Greedy Method (General method, Applications: Fractional knapsack problem, Minimum cost spanning trees, Single source shortest paths problem, Huffman codes).
            UNIT-III: Dynamic Programming (General method, Applications: 0/1 knapsack problem, Matrix chain multiplication, Longest common subsequence, All pairs shortest paths problem using Floyd's algorithm, Travelling salesman problem).
            UNIT-IV: Backtracking (General method, Applications: n-queens problem, sum of subsets problem, graph coloring, Hamiltonian cycles), Branch and Bound (General method, Applications: LC Branch and Bound, FIFO Branch and bound and respective solutions for 0/1 Knapsack Problem).
            UNIT-V: Complexity Classes (Basic concepts, non-deterministic algorithms, P, NP, NP-Hard and NP-Complete classes, Cook's theorem (without proof)), Approximation Algorithms (The vertex-cover problem, The traveling-salesman problem).
            Do not answer questions outside of this defined syllabus.
            Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., *Algorithm Name*). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."""}
        ]
    },
    "DATA STRUCTURES AND ALGORITHMS": {
        "messages": [
            {"role": "system", "content": "You are a knowledgeable AI assistant for Data Structures and Algorithms. Provide clear explanations and discuss complexities. Your tone is informative and pedagogical. Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., *Data Structure*). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."}
        ]
    },
    "ARTIFICIAL INTELLIGENCE - 1": {
        "messages": [
            {"role": "system", "content": "You are an AI expert specializing in foundational Artificial Intelligence concepts. Explain complex AI topics in an accessible yet accurate manner. Focus on core AI techniques and their applications. Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., *AI Concept*). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."}
        ]
    },
    "OPERATING SYSTEMS": {
        "messages": [
            {"role": "system", "content": "You are a knowledgeable tutor for Operating Systems. Explain OS concepts, principles, and functionalities clearly and accurately. Provide practical examples where they enhance understanding. Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., *OS Principle*). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."}
        ]
    }
}
print("DEBUG: PROMPT_DESIGNS_OPENROUTER dictionary defined.")

# --- API Endpoint for Chat ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    subject = data.get('subject')

    print(f"DEBUG: /chat endpoint received message: '{user_message}' for subject: '{subject}'")

    if not user_message or not subject:
        print("ERROR: Message or subject missing from frontend request.")
        return jsonify({"error": "Message and subject are required"}), 400

    found_subject_key = None
    normalized_subject = subject.replace(" ", "").upper()
    for key in PROMPT_DESIGNS_OPENROUTER.keys():
        if normalized_subject == key.replace(" ", "").upper():
            found_subject_key = key
            break

    if not found_subject_key:
        print(f"ERROR: Invalid subject '{subject}'. Available: {list(PROMPT_DESIGNS_OPENROUTER.keys())}")
        return jsonify({"error": "Invalid subject selected. Please choose a valid subject."}), 400
    
    selected_prompt_messages = list(PROMPT_DESIGNS_OPENROUTER[found_subject_key]["messages"]) # Shallow copy
    messages_for_api = selected_prompt_messages
    messages_for_api.append({"role": "user", "content": user_message}) # Add current user's query
    print(f"DEBUG: Messages sent to OpenRouter API: {len(messages_for_api)} entries.")

    try:
        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages_for_api,
            temperature=OPENROUTER_TEMPERATURE,
            max_tokens=OPENROUTER_MAX_TOKENS
        )
        print("DEBUG: Successfully received response from OpenRouter API.")

        bot_response = completion.choices[0].message.content
        
        # --- Post-processing for consistent formatting and readability ---
        # 1. Convert numbered lists to bullet points (e.g., "1. item" to "- item")
        #    This is crucial if the AI occasionally generates numbered lists.
        bot_response = re.sub(r'^\s*\d+\.\s*', '- ', bot_response, flags=re.MULTILINE)
        
        # 2. Standardize bullet points to hyphens (e.g., '*' or '+' to '-')
        bot_response = re.sub(r'^\s*[\*\+]\s*', '- ', bot_response, flags=re.MULTILINE)

        # 3. Remove any remaining markdown headings (###, ##, #)
        #    We rely on frontend to handle *Text* for headings/bolding.
        bot_response = re.sub(r'#{1,3}\s*(.*?)\s*', r'\1', bot_response)

        # 4. Normalize newlines: collapse excessive newlines to ensure clean paragraphs
        #    This handles cases where the AI might add too many newlines, or not enough.
        #    Replace 3 or more consecutive newlines with just 2.
        bot_response = re.sub(r'\n{3,}', '\n\n', bot_response)
        
        # 5. Add a newline before bullet points if they don't already have one (for spacing)
        #    This helps ensure lists are separated from preceding text.
        bot_response = re.sub(r'(?<!\n)\n-', '\n\n-', bot_response)

        # 6. Ensure a newline after closing bullet items, if followed by text on the same line
        #    This helps ensure text after a list item starts on a new line.
        bot_response = re.sub(r'(- .*?)([^\n])$', r'\1\n\2', bot_response)


        return jsonify({"botResponse": bot_response})

    except AuthenticationError as e:
        print(f"ERROR: OpenRouter Authentication Failed during chat request! Details: {e}")
        return jsonify({"error": f"Authentication Error with AI: {str(e)}"}), 500
    except APIError as e:
        print(f"ERROR: OpenRouter API Error during chat request for subject '{subject}': {e}")
        print(f"OpenRouter Error Status Code: {e.status_code}")
        print(f"OpenRouter Error Response: {e.response}")
        traceback.print_exc()
        return jsonify({"error": f"OpenRouter API Error: {str(e)}"}), 500
    except Exception as e:
        print(f"ERROR: Failed to communicate with OpenRouter API for subject '{subject}': {e}")
        traceback.print_exc()
        return jsonify({"error": f"Failed to get response from AI: {str(e)}"}), 500

# --- Run the Flask Application ---
if __name__ == '__main__':
    print("DEBUG: Entering Flask app.run() block.")
    app.run(debug=True, host='0.0.0.0', port=5000)
    print("DEBUG: Flask app.run() block finished (this line is rarely reached).")