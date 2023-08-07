import gradio as gr
import json
import random

last_question_text = None
last_user_answer = None

# Path to the files
path_to_users = './data/users.json'
path_to_questions = './data/questions.json'

# Load Users
def load_users():
    with open(path_to_users, 'r') as file:
        return json.load(file)["users"]

# Save Users
def save_users(user_dropdown, points):
    with open(path_to_users, 'r') as file:
        users = json.load(file)
    for user in users["users"]:
        if user['username'] == user_dropdown:
            user['points'] = points
            break
    with open(path_to_users, 'w') as file:
        json.dump(users, file)

# Load Questions
def load_questions():
    with open(path_to_questions, 'r') as file:
        return json.load(file)["questions"]

questions = load_questions()

# Select User
def select_user(user_dropdown):
    selected_user_points = 0
    for user in users:
        if user['username'] == user_dropdown:
            selected_user_points = user['points']
            break
    return f"Points: {selected_user_points}"


# Show Random Question
def show_question(user_dropdown):
    global last_question_text, last_user_answer
    last_question_text = None
    last_user_answer = None

    question = random.choice(questions)
    question_text = format_question_text(question)
    last_question_text = question_text # Remember the last question text

    return question_text, json.dumps(question), "", "" # Clears user's answer and result text boxes

# Check Answer
def check_answer(user_answer, question_text, user_dropdown):
    global last_question_text, last_user_answer

    for user in users:
        if user['username'] == user_dropdown:
            if question_text == last_question_text and user_answer == last_user_answer:
                return (f"You've already answered this question! Your current points are {user['points']}.",
                        f"Points: {user['points']}")

            last_question_text = question_text
            last_user_answer = user_answer

            # Assuming question_text contains both question and correct answer
            correct_answer = extract_correct_answer(question_text)

            if user_answer.strip().lower() == correct_answer.lower():
                user['points'] += extract_points(question_text)
                save_users(user_dropdown, user['points'])
                return (f"Correct! You have now {user['points']} points.",
                        f"Points: {user['points']}")
            else:
                return (f"Wrong! The correct answer is: {correct_answer}. Your current points are {user['points']}.",
                        f"Points: {user['points']}")

def extract_correct_answer(question_text):
    question_data = json.loads(question_text)
    return question_data['correct_answer']

def extract_points(question_text):
    question_data = json.loads(question_text)
    return question_data['points']

def format_question_text(question):
    # Extract the relevant fields from the question
    question_type = question.get("type")
    question_prompt = question.get("question")
    options = question.get("options", []) # Options field is optional and could be empty for some types of questions

    # If question_prompt is None, you can handle it here (e.g., by returning a default value)
    if question_prompt is None:
        return "No question available"

    question_text = question_prompt
    if question_type == "multiple_choice" and options:
        question_text += "\n" + "\n".join([f"{i + 1}. {option}" for i, option in enumerate(options)])

    return question_text

users = load_users()

with gr.Blocks() as app:
    with gr.Row():
        gr.Markdown('# School Quiz')
    with gr.Row():
        with gr.Column(scale=1):
            user_dropdown = gr.Dropdown(choices=[user['username'] for user in users], label="Select User")
            user_points = gr.Markdown("Points: 0") # Initialized with 0 points
            user_dropdown.change(select_user, inputs=[user_dropdown], outputs=[user_points])
        with gr.Column(scale=2):
            gr.Markdown('## Questions')
            question_text = gr.Textbox(label="Question", lines=6) # Increase lines for displaying options
            question_hidden = gr.Textbox(visible=False)
            show_question_button = gr.Button("Show Question")
            show_question_button.click(show_question, inputs=[user_dropdown], outputs=[question_text, question_hidden])
            user_answer = gr.Textbox(label="Your Answer", lines=2)
            check_answer_button = gr.Button("Check Answer")
            answer_result = gr.Textbox(label="Result", lines=2)
            check_answer_button.click(check_answer, inputs=[user_answer, question_hidden, user_dropdown], outputs=[answer_result, user_points])

app.launch(server_name='0.0.0.0', server_port=7860, share=False)

