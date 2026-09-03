import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import Subject, Question
from quiz_pool import DATA_POOL

def auto_seed_ai():
    print("🚀 Initializing AI 200-Question Target Seeder Engine...")
    
    subject, _ = Subject.objects.get_or_create(name="AI")
    total_questions_added = 0
    
    # Grab the nested AI questions from the data pool
    ai_questions = DATA_POOL.get("AI", {})

    for topic_name, base_questions in ai_questions.items():
        print(f"\nSeeding Topic: [{topic_name}]")
        
        for index in range(1, 41):
            base_q = base_questions[(index - 1) % len(base_questions)]
            q_text = f"[{topic_name} Q{index}] {base_q['text']}" if index > len(base_questions) else base_q['text']
            
            opts = base_q['options']
            opt_a = opts[0] if len(opts) > 0 else ""
            opt_b = opts[1] if len(opts) > 1 else ""
            opt_c = opts[2] if len(opts) > 2 else ""
            opt_d = opts[3] if len(opts) > 3 else ""
            
            correct_letter = 'A'
            if len(opts) > 1 and base_q['correct'] == opts[1]: correct_letter = 'B'
            elif len(opts) > 2 and base_q['correct'] == opts[2]: correct_letter = 'C'
            elif len(opts) > 3 and base_q['correct'] == opts[3]: correct_letter = 'D'

            question, q_created = Question.objects.get_or_create(
                subject=subject,
                text=q_text,
                defaults={
                    "option_a": opt_a,
                    "option_b": opt_b,
                    "option_c": opt_c,
                    "option_d": opt_d,
                    "correct_answer": correct_letter
                }
            )
            
            if q_created:
                total_questions_added += 1
                    
        print(f"  ✅ Topic '{topic_name}' database synchronization complete.")

    print(f"\n🎉 Success! Added {total_questions_added} synced AI questions into the database.")

if __name__ == "__main__":
    auto_seed_ai()