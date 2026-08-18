# app.py
# Backend and Static File Server for "The Scribe's Desk" chatbot.

import os
import re
import traceback
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI, AuthenticationError, APIError

# Load environment variables
load_dotenv()

# Define absolute paths so Flask locates the frontend directory relative to backend/app.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)  # Enables cross-origin requests for frontend clients

# --- Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "https://your-chatbot-domain.com")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "The Scribe's Desk")
OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", 0.4))
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", 72000))
PORT = int(os.getenv("PORT", 5000))

if not OPENROUTER_API_KEY:
    print("CRITICAL ERROR: OPENROUTER_API_KEY environment variable is NOT set.")
    exit(1)

# Initialize OpenAI client configured for OpenRouter
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": YOUR_SITE_URL,
            "X-Title": YOUR_SITE_NAME,
        }
    )
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize OpenRouter client: {e}")
    exit(1)

OPENROUTER_MODEL = "deepseek/deepseek-r1-0528:free"

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
            Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using (e.g., Key Concept). Do not use markdown headings (like #, ##, ###) or triple asterisks(***). Ensure a line space after each point or paragraph for improved readability."""}
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
            Format your responses for maximum readability: use clear paragraphs with good line spacing. For lists, use bullet points (e.g., '- item'). For main points or section titles within your response, bold them using single asterisks (e.g., Key Concept). Do not use markdown headings (like #, ##, ###) or triple asterisks (***). Ensure a line space after each point or paragraph for improved readability."""}
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

# --- Frontend Static File Routes ---
@app.route('/', methods=['GET'])
def serve_index():
    """Serves the main frontend index.html page at the root URL."""
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    """Serves static assets (script.js, style.css, images, etc.) from frontend directory."""
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, 'index.html')

# --- Backend Health Endpoint ---
@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    """Returns JSON status for monitoring and uptime checks."""
    return jsonify({"status": "healthy", "service": "The Scribe's Desk Backend"}), 200

# --- API Endpoint for Chat ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    user_message = data.get('message')
    subject = data.get('subject')

    if not user_message or not subject:
        return jsonify({"error": "Message and subject are required"}), 400

    found_subject_key = None
    normalized_subject = subject.replace(" ", "").upper()
    for key in PROMPT_DESIGNS_OPENROUTER.keys():
        if normalized_subject == key.replace(" ", "").upper():
            found_subject_key = key
            break

    if not found_subject_key:
        return jsonify({"error": "Invalid subject selected. Please choose a valid subject."}), 400

    messages_for_api = list(PROMPT_DESIGNS_OPENROUTER[found_subject_key]["messages"])
    messages_for_api.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages_for_api,
            temperature=OPENROUTER_TEMPERATURE,
            max_tokens=OPENROUTER_MAX_TOKENS
        )

        bot_response = completion.choices[0].message.content or ""

        # Strip reasoning thoughts (<think>...</think>) generated by DeepSeek-R1
        bot_response = re.sub(r'<think>.*?</think>', '', bot_response, flags=re.DOTALL).strip()

        # Formatting normalizations
        bot_response = re.sub(r'^\s*\d+\.\s*', '- ', bot_response, flags=re.MULTILINE)
        bot_response = re.sub(r'^\s*[\*\+]\s*', '- ', bot_response, flags=re.MULTILINE)
        bot_response = re.sub(r'#{1,3}\s*(.*?)\s*', r'\1', bot_response)
        bot_response = re.sub(r'\n{3,}', '\n\n', bot_response)
        bot_response = re.sub(r'(?<!\n)\n-', '\n\n-', bot_response)

        return jsonify({"botResponse": bot_response})

    except AuthenticationError as e:
        return jsonify({"error": f"Authentication Error: {str(e)}"}), 500
    except APIError as e:
        return jsonify({"error": f"OpenRouter API Error: {str(e)}"}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
