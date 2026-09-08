import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import Subject, Question
from quiz_pool import DATA_POOL


def auto_seed_dbms():
    print("🚀 Initializing DBMS 150-Question Seeder Engine...")

    subject, _ = Subject.objects.get_or_create(
        name="DBMS"
    )

    total_questions_added = 0

    # Get DBMS questions from the consolidated data pool
    dbms_questions = DATA_POOL.get("DBMS", {})

    for topic_name, base_questions in dbms_questions.items():

        print(f"\nSeeding Topic: [{topic_name}]")

        # Exactly 30 questions per topic
        for base_q in base_questions[:30]:

            q_text = base_q["text"]

            opts = base_q["options"]

            opt_a = opts[0]
            opt_b = opts[1]
            opt_c = opts[2]
            opt_d = opts[3]

            # Find the correct answer's option letter
            correct_letter = "A"

            if base_q["correct"] == opts[1]:
                correct_letter = "B"
            elif base_q["correct"] == opts[2]:
                correct_letter = "C"
            elif base_q["correct"] == opts[3]:
                correct_letter = "D"

            question, q_created = Question.objects.get_or_create(
                subject=subject,
                topic=topic_name,
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

        print(
            f"  ✅ Topic '{topic_name}' "
            f"database synchronization complete."
        )

    print(
        f"\n🎉 Success! Added "
        f"{total_questions_added} synced DBMS questions "
        f"into the database."
    )


if __name__ == "__main__":
    auto_seed_dbms()