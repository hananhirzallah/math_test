# Hanan Hirzallah Math Test
import random
import time
import streamlit as st

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

# Main function to run the Streamlit app
def main():
    st.title("Math Test!")
    
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = 0
        st.session_state.current_difficulty = 1
        st.session_state.score = 0
        st.session_state.question_number = 0
        st.session_state.answers = []
        st.session_state.current_question = None
        st.session_state.start_time = None
        st.session_state.feedback = None
    
    if st.session_state.num_questions == 0:
        st.session_state.num_questions = st.number_input('Enter the number of questions (10-20):', min_value=10, max_value=20, step=1)
    
    if st.session_state.current_question is None:
        st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
        st.session_state.start_time = time.time()
    
    question = st.session_state.current_question
    st.write(f"Question {st.session_state.question_number + 1}: {question['question']} (Round your answer to one decimal place if necessary)")
    
    user_answer = st.number_input('Your answer:', format="%.1f", step=0.1)
    
    if st.button('Submit'):
        end_time = time.time()
        time_taken = end_time - st.session_state.start_time
        
        correct = round(user_answer, 1) == question['answer']
        if correct:
            st.session_state.score += 1
            st.session_state.feedback = "Correct!"
        else:
            st.session_state.feedback = f"Wrong Answer! Hint: {question['hint']} The correct answer was: {question['answer']}"
        
        st.session_state.answers.append({
            'question': question['question'],
            'answer': user_answer,
            'correct': correct,
            'difficulty': st.session_state.current_difficulty,
            'time_taken': time_taken
        })
        
        st.session_state.current_difficulty = adjust_difficulty(st.session_state.current_difficulty, correct)
        st.session_state.question_number += 1
        
        if st.session_state.question_number >= st.session_state.num_questions:
            performance = evaluate_performance(st.session_state.answers)
            st.write("Test completed!")
            st.write(f"Score: {st.session_state.score}/{st.session_state.num_questions}")
            st.write(f"Performance: {performance}")
        else:
            st.session_state.current_question = generate_arithmetic_question(st.session_state.current_difficulty)
            st.session_state.start_time = time.time()
    
    if st.session_state.feedback:
        st.write(st.session_state.feedback)
        st.session_state.feedback = None
    
    if st.session_state.question_number > 0 and st.session_state.question_number < st.session_state.num_questions:
        st.experimental_rerun()

if __name__ == "__main__":
    main()


