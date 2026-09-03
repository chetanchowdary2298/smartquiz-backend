import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import Subject, Question

def populate():
    print("Populating database with subjects and questions...")

    # 1. Create Subjects
    python_sub, _ = Subject.objects.get_or_create(name="Python", description="Python Programming Language Quiz")
    java_sub, _ = Subject.objects.get_or_create(name="Java", description="Java Core Concepts Quiz")
    cpp_sub, _ = Subject.objects.get_or_create(name="C++", description="C++ Object-Oriented Programming Quiz")

    # 2. Questions Data
    questions_data = [
        # Python Questions
        {"subject": python_sub, "text": "Which of the following is correct extension of the Python file?", "option_a": ".python", "option_b": ".pl", "option_c": ".py", "option_d": ".p", "correct_answer": "C"},
        {"subject": python_sub, "text": "How do you create a variable in Python?", "option_a": "var x = 5", "option_b": "int x = 5", "option_c": "x = 5", "option_d": "declare x = 5", "correct_answer": "C"},
        {"subject": python_sub, "text": "Which keyword is used for function declaration in Python?", "option_a": "fun", "option_b": "function", "option_c": "def", "option_d": "define", "correct_answer": "C"},
        {"subject": python_sub, "text": "What is the correct output of print(2 ** 3)?", "option_a": "6", "option_b": "8", "option_c": "9", "option_d": "5", "correct_answer": "B"},
        {"subject": python_sub, "text": "Which collection is ordered, changeable, and allows duplicate members?", "option_a": "SET", "option_b": "DICTIONARY", "option_c": "LIST", "option_d": "TUPLE", "correct_answer": "C"},

        # Java Questions
        {"subject": java_sub, "text": "Which component is used to compile, debug and execute the Java program?", "option_a": "JRE", "option_b": "JIT", "option_c": "JDK", "option_d": "JVM", "correct_answer": "C"},
        {"subject": java_sub, "text": "Which keyword is used to inherit a class in Java?", "option_a": "implements", "option_b": "extends", "option_c": "inherits", "option_d": "import", "correct_answer": "B"},
        {"subject": java_sub, "text": "What is the default value of a boolean variable in Java?", "option_a": "true", "option_b": "false", "option_c": "null", "option_d": "not defined", "correct_answer": "B"},
        {"subject": java_sub, "text": "Which method is the entry point for any Java program?", "option_a": "start()", "option_b": "init()", "option_c": "main()", "option_d": "run()", "correct_answer": "C"},
        {"subject": java_sub, "text": "Java is an example of which type of programming language?", "option_a": "Procedural", "option_b": "Object-Oriented", "option_c": "Functional", "option_d": "Logic", "correct_answer": "B"},

        # C++ Questions
        {"subject": cpp_sub, "text": "Who invented C++?", "option_a": "Dennis Ritchie", "option_b": "Bjarne Stroustrup", "option_c": "James Gosling", "option_d": "Guido van Rossum", "correct_answer": "B"},
        {"subject": cpp_sub, "text": "Which data type is used to create a variable that should store text in C++?", "option_a": "String", "option_b": "string", "option_c": "txt", "option_d": "char", "correct_answer": "B"},
        {"subject": cpp_sub, "text": "How do you insert a single line comment in C++ code?", "option_a": "# comment", "option_b": "/* comment", "option_c": "// comment", "option_d": "-- comment", "correct_answer": "C"},
        {"subject": cpp_sub, "text": "Which keyword is used to create a class in C++?", "option_a": "className", "option_b": "class", "option_c": "struct", "option_d": "object", "correct_answer": "B"},
        {"subject": cpp_sub, "text": "What is the insertion operator in C++ used with cout?", "option_a": "<<", "option_b": ">>", "option_c": "<", "option_d": ">", "correct_answer": "A"},
    ]

    # 3. Save to DB
    for q in questions_data:
        Question.objects.get_or_create(
            subject=q["subject"],
            text=q["text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"]
        )
    print("Successfully added all subjects and questions!")

if __name__ == "__main__":
    populate()