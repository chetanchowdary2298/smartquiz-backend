import os
import django

# Setup Django configuration layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# ⚠️ Replace 'accounts' with your exact app name containing your quiz models
from accounts.models import Subject, Question, Option 
from quiz_pool import DATA_POOL

def seed_quiz_system():
    print("🚀 Starting SmartQuiz Master Data Seeding System...")
    
    for subject_name, questions_list in DATA_POOL.items():
        print(f"\nProcessing Subject: {subject_name}...")
        
        # 1. Ensure the subject exists in MySQL matching the frontend card layout
        subject, created = Subject.objects.get_or_create(name=subject_name)
        if created:
            print(f"  ✅ Created new Subject record in DB: {subject_name}")
        else:
            print(f"  ℹ️ Subject '{subject_name}' already exists in DB. Appending questions.")

        questions_inserted = 0
        
        # 2. Loop through all questions provided for this subject
        for q_data in questions_list:
            # Prevent duplicates if script runs multiple times
            question, q_created = Question.objects.get_or_create(
                subject=subject,
                text=q_data["text"],
                defaults={"difficulty": q_data.get("difficulty", "Medium")}
            )
            
            if q_created:
                questions_inserted += 1
                # 3. Create all 4 multiple-choice options linked to this question
                for option_text in q_data["options"]:
                    is_correct = (option_text == q_data["correct"])
                    Option.objects.create(
                        question=question,
                        text=option_text,
                        is_correct=is_correct
                    )
                    
        print(f"  🎉 Successfully synced {questions_inserted} new questions for {subject_name}!")

    print("\n🌟 All subjects and question pools are fully updated in MySQL!")

if __name__ == "__main__":
    seed_quiz_system()