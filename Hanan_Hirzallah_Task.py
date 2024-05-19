import random
import time
import streamlit as st

# Set the color styles using Streamlit's markdown feature with HTML and CSS
st.markdown("""
    <style>
    .main {
        background-color: #e0f7fa;
    }
    .stButton>button {
        color: #ffffff;
        background-color: #007BFF;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        cursor: pointer;
        width: 140px;  /* Adjusted width */
        height: 40px;  /* Adjusted height */
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
        background-color: #ffffff;  /* White background color */
    }
    .stNumberInput>div>div>input {
        border: 1px solid #007BFF;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
        color: #007BFF;
        background-color: #ffffff;  /* White background color */
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
    .hint {
        color: #007BFF;
    }
    input[type="number"] {
        background-color: #ffffff;  /* White background color */
        color: #007BFF;  /* Blue text color */
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
        hint = (
            f"<p class='hint'>To solve {a} + {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other. Make sure the digits on the right are lined up.</p>"
            f"<p class='hint'>2. Start adding from the right side.</p>"
            f"<p class='hint'>3. If the sum is 10 or more, write down the right digit and put the left digit above the next column.</p>"
            f"<p class='hint'>4. Add the next column, including any number carried over.</p>"
        )
    elif operation == '-':
        question = f"{a} - {b}"
        answer = a - b
        hint = (
            f"<p class='hint'>To solve {a} - {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other. Make sure the digits on the right are lined up.</p>"
            f"<p class='hint'>2. Start subtracting from the right side.</p>"
            f"<p class='hint'>3. If the top number is smaller, borrow from the next column on the left.</p>"
            f"<p class='hint'>4. Subtract the next column, including any number borrowed.</p>"
        )
    elif operation == '*':
        question = f"{a} * {b}"
        answer = a * b
        hint = (
            f"<p class='hint'>To solve {a} * {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other.</p>"
            f"<p class='hint'>2. Multiply the bottom number by each digit of the top number, starting from the right.</p>"
            f"<p class='hint'>3. Write each result below, shifting one place to the left each time.</p>"
            f"<p class='hint'>4. Add up all the results to get the final answer.</p>"
        )
    else:
        question = f"{a} / {b}"
        answer = round(a / b, 1) if b != 0 else None  # Avoid division by zero and round to 1 decimal place
        hint = (
            f"<p class='hint'>To solve {a} / {b}:</p>"
            f"<p class='hint'>1. See how many times {b} fits into {a}.</p>"
            f"<p class='hint'>2. Write down the answer above the division line.</p>"
            f"<p class='hint'>3. If there's any left over, that's the remainder.</p>"
            f"<p class='hint'>4. Continue dividing to get a decimal if needed, and round to one decimal place.</p>"
        )
    
    return {"question": question, "answer": answer, "difficulty": difficulty, "hint": hint}

# Function to evaluate performance
def evaluate_performance(answers, total_time):
    correct_answers = sum(1 for ans in answers if ans['correct'])
    average_difficulty = sum(ans['difficulty'] for ans in answers) / len(answers)
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
        'current_question', 'start_time', 'feedback', 'user_answer', 'show_hint', 'second_chance', 'total_start_time'
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
        st.session_state.second_chance = False
        st.session_state.total_start_time = time.time()  # Initialize total start time

    # Request number of questions if not already set
    if st.session_state.num_questions is None:
        st.markdown('<p class="blue-text">Choose number of questions (10-20):</p>', unsafe_allow_html=True)
        num_questions = st.number_input('', min_value=10, max_value=20, step=1, key='num_questions_input')
        if st.button('Confirm'):
            st.session_state.num_questions = num_questions
            st.session_state.total_start_time = time.time()  # Initialize total start time when quiz starts
            st.experimental_rerun()
        return  # Return here to wait for the user to confirm the number of questions

    # Check if the quiz is complete
    if st.session_state.question_number >= st.session_state.num_questions:
        total_time = time.time() - st.session_state.total_start_time
        performance = evaluate_performance(st.session_state.answers, total_time)
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

    difficulty_map = {1: "Easy", 2: "Medium", 3: "Hard"}
    difficulty_label = difficulty_map[question['difficulty']]

    st.write(f"Question {st.session_state.question_number + 1} (Difficulty: {difficulty_label}): {question['question']} (Round your answer to one decimal place if necessary)")

    st.markdown('<p class="blue-label">Your answer:</p>', unsafe_allow_html=True)
    user_answer = st.text_input('', value=st.session_state.user_answer, key=f'user_answer_input_{st.session_state.question_number}')

    col1, col2 = st.columns(2)
    with col1:
        if st.button('Show Hint'):
            st.session_state.show_hint = True

    with col2:
        if st.button('Submit', key='submit_button'):
            if st.session_state.question_number >= st.session_state.num_questions:
                return  # Stop if quiz is complete

            end_time = time.time()
            time_taken = end_time - st.session_state.start_time

            try:
                user_answer = float(user_answer)
            except ValueError:
                st.session_state.feedback = "Please enter a valid number."
                st.session_state.user_answer = ""  # Reset user answer
                st.experimental_rerun()
                return

            correct = round(user_answer, 1) == question['answer']
            if correct:
                st.session_state.score += 1
                st.session_state.feedback = "Correct!"
                st.session_state.current_difficulty = adjust_difficulty(st.session_state.current_difficulty, correct)
                st.session_state.second_chance = False  # Reset second chance flag
                st.session_state.question_number += 1
                st.session_state.answers.append({
                    'question': question['question'],
                    'answer': user_answer,
                    'correct': True,
                    'difficulty': st.session_state.current_difficulty,
                    'time_taken': time_taken
                })
            else:
                if st.session_state.second_chance:
                    st.session_state.feedback = f"Wrong Answer again! The correct answer was: {question['answer']}"
                    st.session_state.answers.append({
                        'question': question['question'],
                        'answer': user_answer,
                        'correct': False,
                        'difficulty': st.session_state.current_difficulty,
                        'time_taken': time_taken
                    })
                    st.session_state.current_difficulty = adjust_difficulty(st.session_state.current_difficulty, correct)
                    st.session_state.question_number += 1
                    st.session_state.second_chance = False  # Reset second chance flag
                else:
                    st.session_state.feedback = "Wrong Answer! Try another question of the same difficulty."
                    st.session_state.answers.append({
                        'question': question['question'],
                        'answer': user_answer,
                        'correct': False,
                        'difficulty': st.session_state.current_difficulty,
                        'time_taken': time_taken
                    })
                    st.session_state.question_number += 1  # Increment the question number for the second attempt
                    st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
                    st.session_state.start_time = time.time()
                    st.session_state.user_answer = ""  # Reset user answer for the new question
                    st.session_state.second_chance = True
                    st.experimental_rerun()
                    return

            # Reset for the next question
            st.session_state.current_question = None
            st.session_state.user_answer = ""  # Reset user answer for next question
            st.experimental_rerun()

    if st.session_state.show_hint:
        st.markdown(question['hint'], unsafe_allow_html=True)

    if st.session_state.feedback:
        st.write(st.session_state.feedback)
        st.session_state.feedback = None

if __name__ == "__main__":
    main()




