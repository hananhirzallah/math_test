import random
import time
import streamlit as st

def set_styles():
    st.markdown("""
        <style>
        .main { background-color: #e0f7fa; }
        .stButton>button { color: #ffffff; background-color: #007BFF; border-radius: 5px; border: none; padding: 10px 20px; font-size: 16px; cursor: pointer; width: 140px; height: 40px; margin-top: 20px; }
        .stButton>button:hover { background-color: #0056b3; }
        .stTextInput>div>div>input, .stNumberInput>div>div>input, input[type="number"] { border: 1px solid #007BFF; border-radius: 5px; padding: 10px; font-size: 16px; color: #007BFF; background-color: #ffffff; }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stMarkdown p { color: #007BFF; }
        .blue-text, .hint { color: #007BFF; margin-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

def generate_arithmetic_question(difficulty):
    operations = {'+': 'add', '-': 'subtract', '*': 'multiply', '/': 'divide'}
    ranges = {1: (1, 10), 2: (10, 100), 3: (100, 500), 4: (500, 1000)}
    a, b = random.randint(*ranges[difficulty]), random.randint(*ranges[difficulty])
    operation = random.choice(list(operations.keys()))
    question = f"{a} {operation} {b}"
    answer = round(eval(question), 1) if operation == '/' else eval(question)
    
    if operation == '+':
        hint = (
            f"<p class='hint'>To solve {a} + {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other. Make sure the digits on the right are lined up.</p>"
            f"<p class='hint'>2. Start adding from the right side.</p>"
            f"<p class='hint'>3. If the sum is 10 or more, write down the right digit and put the left digit above the next column.</p>"
            f"<p class='hint'>4. Add the next column, including any number carried over.</p>"
        )
    elif operation == '-':
        hint = (
            f"<p class='hint'>To solve {a} - {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other. Make sure the digits on the right are lined up.</p>"
            f"<p class='hint'>2. Start subtracting from the right side.</p>"
            f"<p class='hint'>3. If the top number is smaller, borrow from the next column on the left.</p>"
            f"<p class='hint'>4. Subtract the next column, including any number borrowed.</p>"
        )
    elif operation == '*':
        hint = (
            f"<p class='hint'>To solve {a} * {b}:</p>"
            f"<p class='hint'>1. Write the numbers one under the other.</p>"
            f"<p class='hint'>2. Multiply the bottom number by each digit of the top number, starting from the right.</p>"
            f"<p class='hint'>3. Write each result below, shifting one place to the left each time.</p>"
            f"<p class='hint'>4. Add up all the results to get the final answer.</p>"
        )
    else:
        hint = (
            f"<p class='hint'>To solve {a} / {b}:</p>"
            f"<p class='hint'>1. See how many times {b} fits into {a}.</p>"
            f"<p class='hint'>2. Write down the answer above the division line.</p>"
            f"<p class='hint'>3. If there's any left over, that's the remainder.</p>"
            f"<p class='hint'>4. Continue dividing to get a decimal if needed, and round to one decimal place.</p>"
        )
    
    return {"question": question, "answer": answer, "difficulty": difficulty, "hint": hint}

def evaluate_performance(answers, total_time):
    correct_answers = sum(1 for ans in answers if ans['correct'])
    average_difficulty = sum(ans['difficulty'] for ans in answers) / len(answers)
    total_time = round(total_time, 1)
    minutes, seconds = divmod(total_time, 60)
    return {
        "correct_answers": correct_answers,
        "average_difficulty": average_difficulty,
        "total_time": f"{int(minutes)} minutes and {seconds:.1f} seconds"
    }

def adjust_difficulty(current_difficulty, correct):
    return min(4, current_difficulty + 1) if correct else max(1, current_difficulty - 1)

def reset_quiz():
    for key in ['num_questions', 'current_difficulty', 'score', 'question_number', 'answers', 'current_question', 'start_time', 'feedback', 'user_answer', 'show_hint', 'second_chance', 'total_start_time']:
        if key in st.session_state:
            del st.session_state[key]
    st.experimental_rerun()

def handle_feedback(user_answer, correct_answer, current_difficulty, second_chance):
    correct = round(user_answer, 1) == correct_answer
    feedback = "Correct!" if correct else "Wrong Answer! Try another question." if second_chance else f"Wrong Answer again! The correct answer was: {correct_answer}"
    next_difficulty = adjust_difficulty(current_difficulty, correct)
    return correct, feedback, next_difficulty

def main():
    set_styles()
    st.title("Math Test!")

    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False

    if not st.session_state.quiz_started:
        st.markdown("""
            <div class="blue-text">
                Hello! I'm Hanan Hirzallah and this is my math quiz!
                <br><br>
                Instructions:
                <br>- Firstly, The quiz will ask you to choose the number of questions you want, it has to be within the range (10-20).
                <br>- Once you select and confirm, the quiz begins.
                <br>- Each question has a hint, where the way to solve the question is displayed. Just press "Show Hint".
                <br>- The quiz is divided into 4 difficulty levels: Easy, Intermediate, Hard, and Advanced.
                <br>- If you solve the question correctly, you get upgraded to the next level!
                <br>- However, if you answer it incorrectly, you have a second attempt at a similar question.
                <br>- If you answer your second attempt correctly, you get upgraded to the next level
                <br>- If not, you get downgraded to the previous level.
                <br>- After the quiz is over, your score is displayed. As well as a summary of your performance including:
                <br>&nbsp;&nbsp;&nbsp;1. Number of correct answers.
                <br>&nbsp;&nbsp;&nbsp;2. Average level.
                <br>&nbsp;&nbsp;&nbsp;3. Time taken to finish the quiz.
                <br>- There's also an option to restart the quiz.
                <br><br>
                Have fun and good luck!!
            </div>
        """, unsafe_allow_html=True)
        
        if st.button('Start Quiz'):
            st.session_state.quiz_started = True
            st.session_state.total_start_time = time.time()
            reset_quiz()
        return

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
        st.session_state.total_start_time = time.time()

    if st.session_state.num_questions is None:
        st.markdown('<p class="blue-text">Choose number of questions (10-20):</p>', unsafe_allow_html=True)
        num_questions = st.number_input('', min_value=10, max_value=20, step=1, key='num_questions_input')
        if st.button('Confirm'):
            st.session_state.num_questions = num_questions
            st.session_state.total_start_time = time.time()
            st.experimental_rerun()
        return

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
        return

    if st.session_state.current_question is None:
        st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
        st.session_state.start_time = time.time()
        st.session_state.user_answer = ""
        st.session_state.show_hint = False

    question = st.session_state.current_question
    difficulty_map = {1: "Easy", 2: "Intermediate", 3: "Hard", 4: "Advanced"}
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
                return

            end_time = time.time()
            time_taken = end_time - st.session_state.start_time

            try:
                user_answer = float(user_answer)
            except ValueError:
                st.session_state.feedback = "Please enter a valid number."
                st.session_state.user_answer = ""
                st.experimental_rerun()
                return

            correct, feedback, next_difficulty = handle_feedback(user_answer, question['answer'], st.session_state.current_difficulty, st.session_state.second_chance)

            st.session_state.answers.append({
                'question': question['question'],
                'answer': user_answer,
                'correct': correct,
                'difficulty': st.session_state.current_difficulty,
                'time_taken': time_taken
            })

            if correct or st.session_state.second_chance:
                st.session_state.score += 1 if correct else 0
                st.session_state.current_difficulty = next_difficulty
                st.session_state.question_number += 1
                st.session_state.current_question = None
                st.session_state.user_answer = ""
                st.session_state.second_chance = False
            else:
                st.session_state.second_chance = True
                st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
                st.session_state.start_time = time.time()

            st.session_state.feedback = feedback
            st.experimental_rerun()

    if st.session_state.show_hint:
        st.markdown(question['hint'], unsafe_allow_html=True)

    if st.session_state.feedback:
        st.write(st.session_state.feedback)
        st.session_state.feedback = None

if __name__ == "__main__":
    main()








