import random
import time
import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression

# Try to import transformers and initialize the pipeline
try:
    from transformers import pipeline
    nlp = pipeline("text-generation", model="distilgpt2")
    transformers_available = True
except Exception as e:
    st.error(f"Error initializing transformers pipeline: {e}")
    transformers_available = False

# Function to generate arithmetic questions with specific hints
def generate_arithmetic_question(difficulty):
    if difficulty == 1:  # easy
        a, b = random.randint(1, 10), random.randint(1, 10)
    elif difficulty == 2:  # medium
        a, b = random.randint(10, 100), random.randint(10, 100)
    else:  # hard
        a, b = random.randint(100, 1000), random.randint(1000, 1000)
    
    operation = random.choice(['+', '-', '*', '/'])
    if operation == '+':
        question = f"{a} + {b}"
        answer = a + b
        hint = f"Think about adding {a} and {b} together."
    elif operation == '-':
        question = f"{a} - {b}"
        answer = a - b
        hint = f"Think about subtracting {b} from {a}."
    elif operation == '*':
        question = f"{a} * {b}"
        answer = a * b
        hint = f"Think about multiplying {a} and {b}."
    else:
        question = f"{a} / {b}"
        answer = round(a / b, 1) if b != 0 else None  # Avoid division by zero and round to 1 decimal place
        hint = f"Think about dividing {a} by {b}. Remember to round to one decimal place if necessary."
    
    return {"question": question, "answer": answer, "difficulty": difficulty, "hint": hint}

# Function to generate feedback using NLP
def generate_feedback(question, user_answer, correct_answer):
    if transformers_available:
        feedback_prompt = f"The question was: {question}. You answered: {user_answer}. The correct answer is: {correct_answer}. Explain why."
        feedback = nlp(feedback_prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
        return feedback
    else:
        return f"The question was: {question}. You answered: {user_answer}. The correct answer is: {correct_answer}. Please install transformers library for detailed feedback."

# Function to evaluate performance
def evaluate_performance(answers):
    correct_answers = sum(1 for ans in answers if ans['correct'])
    average_difficulty = sum(ans['difficulty'] for ans in answers) / len(answers)
    total_time = sum(ans['time_taken'] for ans in answers)
    total_time = round(total_time, 1)  # Round total time to one decimal place

    # Convert total time to minutes and seconds
    minutes = int(total_time // 60)
    seconds = total_time % 60

    return {
        "correct_answers": correct_answers,
        "average_difficulty": average_difficulty,
        "total_time": f"{minutes} minutes and {seconds:.1f} seconds"
    }

# Function to adjust difficulty based on correctness of the previous answers using Linear Regression
def adjust_difficulty(answers):
    if len(answers) < 5:
        return 1  # Start with easy if not enough data

    # Prepare the data
    X = np.array([i for i in range(len(answers))]).reshape(-1, 1)
    y = np.array([ans['difficulty'] for ans in answers])
    correct = np.array([1 if ans['correct'] else 0 for ans in answers])

    # Train a simple linear regression model
    model = LinearRegression()
    model.fit(X, correct)

    # Predict the difficulty for the next question
    next_difficulty = model.predict(np.array([[len(answers)]]))[0]
    next_difficulty = min(max(1, round(next_difficulty)), 3)  # Ensure difficulty is between 1 and 3

    return next_difficulty

# Function to reset the quiz state
def reset_quiz():
    keys_to_clear = [
        'num_questions', 'current_difficulty', 'score', 'question_number', 'answers',
        'current_question', 'start_time', 'feedback', 'user_answer'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.experimental_rerun()

# Main function to run the Streamlit app
def main():
    st.title("Math Test!")

    # Initialize session state variables if not already done
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = None
        st.session_state.current_difficulty = 1
        st.session_state.score = 0
        st.session_state.question_number = 0
        st.session_state.answers = []
        st.session_state.current_question = None
        st.session_state.start_time = None
        st.session_state.feedback = None
        st.session_state.user_answer = ""

    # Request number of questions if not already set
    if st.session_state.num_questions is None:
        num_questions = st.number_input('Enter the number of questions (10-20):', min_value=10, max_value=20, step=1)
        if st.button('Confirm'):
            st.session_state.num_questions = num_questions
            st.experimental_rerun()
        return  # Return here to wait for the user to confirm the number of questions

    # Check if the quiz is complete
    if st.session_state.question_number >= st.session_state.num_questions:
        performance = evaluate_performance(st.session_state.answers)
        st.write("Test completed!")
        st.write(f"Score: {st.session_state.score}/{st.session_state.num_questions}")
        st.write("## Performance Summary")
        st.write(f"Correct Answers: {performance['correct_answers']}")
        st.write(f"Average Difficulty: {round(performance['average_difficulty'], 2)}")
        st.write(f"Total Time: {performance['total_time']}")
        if st.button('Start New Quiz', key='start_new_quiz_button'):
            reset_quiz()
        return  # Stop execution after the last question

    if st.session_state.current_question is None:
        st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
        st.session_state.start_time = time.time()
        st.session_state.user_answer = ""  # Reset user answer for new question

    question = st.session_state.current_question
    st.write(f"Question {st.session_state.question_number + 1} (Difficulty: {question['difficulty']}): {question['question']} (Round your answer to one decimal place if necessary)")

    user_answer = st.text_input('Your answer:', value=st.session_state.user_answer, key=f'user_answer_input_{st.session_state.question_number}')

    if st.button('Submit', key='submit_button'):
        if st.session_state.question_number >= st.session_state.num_questions:
            return  # Stop if quiz is complete

        end_time = time.time()
        time_taken = end_time - st.session_state.start_time

        try:
            user_answer = float(user_answer)
        except ValueError:
            st.session_state.feedback = "Please enter a valid number."
            st.experimental_rerun()
            return

        correct = round(user_answer, 1) == question['answer']
        if correct:
            st.session_state.score += 1
            st.session_state.feedback = "Correct!"
        else:
            hint = question['hint']
            feedback = generate_feedback(question['question'], user_answer, question['answer'])
            st.session_state.feedback = f"{feedback} Hint: {hint}"

        st.session_state.answers.append({
            'question': question['question'],
            'answer': user_answer,
            'correct': correct,
            'difficulty': st.session_state.current_difficulty,
            'time_taken': time_taken
        })

        st.session_state.current_difficulty = adjust_difficulty(st.session_state.answers)
        st.session_state.question_number += 1

        # Reset for the next question
        st.session_state.current_question = None
        st.session_state.start_time = time.time()
        st.session_state.user_answer = ""  # Reset user answer for next question
        st.experimental_rerun()

    if st.session_state.feedback:
        st.write(st.session_state.feedback)
        st.session_state.feedback = None

if __name__ == "__main__":
    main()


