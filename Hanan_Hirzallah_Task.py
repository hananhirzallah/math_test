import random
import time
import streamlit as st

# Set the color styles using Streamlit's markdown feature with HTML and CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f4f8;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #007BFF;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #0056b3;
    }
    .stTextInput>div>div>input {
        border: 1px solid #007BFF;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
        color: #007BFF;
    }
    .stNumberInput>div>div>input {
        border: 1px solid #007BFF;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
        color: #007BFF;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown p {
        color: #007BFF;
    }
    .stMarkdown p {
        font-size: 16px;
    }
    .blue-text {
        color: #007BFF;
        margin-bottom: -100px;
    }
    .blue-label {
        color: #007BFF;
        font-size: 16px;
        margin-bottom: -100px;
    }
    </style>
""", unsafe_allow_html=True)

# Function to generate arithmetic questions with specific hints
def generate_arithmetic_question(difficulty):
    if difficulty == 1:  # easy
        a, b = random.randint(1, 10), random.randint(1, 10)
    elif difficulty == 2:  # medium
        a, b = random.randint(10, 100), random.randint(10, 100)
    else:  # hard
        a, b = random.randint(100, 1000), random.randint(100, 1000)
    
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

# Function to adjust difficulty based on correctness of the previous answer
def adjust_difficulty(current_difficulty, correct):
    if correct:
        return min(3, current_difficulty + 1)  # Increase difficulty if correct
    else:
        return max(1, current_difficulty - 1)  # Decrease difficulty if incorrect

# Function to reset the quiz state
def reset_quiz():
    keys_to_clear = [
        'num_questions', 'current_difficulty', 'score', 'question_number', 'answers',
        'current_question', 'start_time', 'feedback', 'user_answer', 'show_hint'
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
        st.session_state.show_hint = False

    # Request number of questions if not already set
    if st.session_state.num_questions is None:
        st.markdown('<p class="blue-text">Choose number of questions (10-20):</p>', unsafe_allow_html=True)
        num_questions = st.number_input('', min_value=10, max_value=20, step=1)
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
        st.session_state.show_hint = False  # Reset hint visibility for new question

    question = st.session_state.current_question
    st.write(f"Question {st.session_state.question_number + 1}: {question['question']} (Round your answer to one decimal place if necessary)")

    st.markdown('<p class="blue-label">Your answer:</p>', unsafe_allow_html=True)
    user_answer = st.text_input('', value=st.session_state.user_answer, key=f'user_answer_input_{st.session_state.question_number}')

    if st.button('Show Hint'):
        st.session_state.show_hint = True

    if st.session_state.show_hint:
        st.write(f"Hint: {question['hint']}")

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
            st.session_state.feedback = f"Wrong Answer! The correct answer was: {question['answer']}"

        st.session_state.answers.append({
            'question': question['question'],
            'answer': user_answer,
            'correct': correct,
            'difficulty': st.session_state.current_difficulty,
            'time_taken': time_taken
        })

        st.session_state.current_difficulty = adjust_difficulty(st.session_state.current_difficulty, correct)
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




