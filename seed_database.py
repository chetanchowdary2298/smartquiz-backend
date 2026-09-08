import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from accounts.models import Subject, Question
from quiz_pool import DATA_POOL


def seed_quiz_system():
    print("🚀 Starting SmartQuiz Master Data Seeding System...")

    total_questions_added = 0

    for subject_name, topics in DATA_POOL.items():

        print(f"\n📚 Processing Subject: {subject_name}...")

        # Create subject if it does not already exist
        subject, created = Subject.objects.get_or_create(
            name=subject_name
        )

        if created:
            print(
                f"  ✅ Created new Subject record: {subject_name}"
            )
        else:
            print(
                f"  ℹ️ Subject '{subject_name}' already exists."
            )

        subject_questions_added = 0

        # DATA_POOL structure:
        # Subject → Topic → Questions
        for topic_name, questions_list in topics.items():

            print(f"\n  📖 Processing Topic: {topic_name}")

            # Exactly 30 questions per topic
            for q_data in questions_list[:30]:

                opts = q_data["options"]

                # Make sure every question has 4 options
                if len(opts) < 4:
                    print(
                        f"  ⚠️ Skipping question with fewer than "
                        f"4 options: {q_data['text']}"
                    )
                    continue

                opt_a = opts[0]
                opt_b = opts[1]
                opt_c = opts[2]
                opt_d = opts[3]

                # Determine correct answer letter
                correct_letter = "A"

                if q_data["correct"] == opt_b:
                    correct_letter = "B"

                elif q_data["correct"] == opt_c:
                    correct_letter = "C"

                elif q_data["correct"] == opt_d:
                    correct_letter = "D"

                # Create question only if it does not already exist
                question, q_created = Question.objects.get_or_create(
                    subject=subject,
                    topic=topic_name,
                    text=q_data["text"],
                    defaults={
                        "option_a": opt_a,
                        "option_b": opt_b,
                        "option_c": opt_c,
                        "option_d": opt_d,
                        "correct_answer": correct_letter
                    }
                )

                if q_created:
                    subject_questions_added += 1
                    total_questions_added += 1

            print(
                f"  ✅ Topic '{topic_name}' synchronized "
                f"with up to 30 questions."
            )

        print(
            f"\n  🎉 Added {subject_questions_added} new "
            f"questions for {subject_name}."
        )

    print(
        "\n🌟 SmartQuiz database synchronization complete!"
    )

    print(
        f"📊 Total new questions added: "
        f"{total_questions_added}"
    )


if __name__ == "__main__":
    seed_quiz_system()