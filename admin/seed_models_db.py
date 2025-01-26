import asyncio
from shared.prisma.models_db_prisma_client import Prisma
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

async def seed_database():
    db = Prisma()
    await db.connect()

    # Create organizations
    organizations = []
    for _ in range(5):
        org = await db.organization.create({
            "type": random.choice(["Company", "University", "Research Institute"]),
            "name": fake.company(),
            "url": fake.url(),
            "identifier": str(fake.uuid4()),
            "same_as": fake.url(),
        })
        organizations.append(org)

    # Create persons
    persons = []
    for _ in range(10):
        person = await db.person.create({
            "type": "Individual",
            "given_name": fake.first_name(),
            "family_name": fake.last_name(),
            "email": fake.email(),
            "affiliation": {"connect": {"id": random.choice(organizations).id}},
        })
        persons.append(person)

    # Create programming languages
    programming_languages = []
    for lang in ["Python", "JavaScript", "Java", "C++", "Ruby"]:
        pl = await db.programminglanguage.create({
            "name": lang,
        })
        programming_languages.append(pl)

    # Create categories and tags
    categories = [await db.category.create({"name": fake.word()}) for _ in range(5)]
    tags = [await db.tag.create({"name": fake.word()}) for _ in range(10)]

    # Create model metadata and models
    for _ in range(20):
        metadata = await db.modelmetadata.create({
            "publisher": {"connect": {"id": random.choice(organizations).id}},
            "name": fake.catch_phrase(),
            "abstract": fake.text(max_nb_chars=200),
            "description": fake.text(max_nb_chars=500),
            "version": f"{random.randint(0, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "url": fake.url(),
            "identifier": str(fake.uuid4()),
            "date_created": fake.date_time_this_decade(),
            "date_modified": fake.date_time_this_decade(),
            "keywords": [fake.word() for _ in range(5)],
            "citation": [fake.sentence() for _ in range(2)],
            "license": random.choice(["MIT", "Apache 2.0", "GPL", "BSD"]),
            "release_notes": fake.text(max_nb_chars=100),
            "programming_languages": {
                "connect": [{"id": lang.id} for lang in random.sample(programming_languages, k=random.randint(1, 3))]
            },
            "authors": {
                "connect": [{"id": person.id} for person in random.sample(persons, k=random.randint(1, 3))]
            },
            "categories": {
                "connect": [{"id": cat.id} for cat in random.sample(categories, k=random.randint(1, 3))]
            },
            "tags": {
                "connect": [{"id": tag.id} for tag in random.sample(tags, k=random.randint(1, 5))]
            },
        })

        model = await db.model.create({
            "external_id": str(fake.uuid4()),
            "metadata": {"connect": {"id": metadata.id}},
        })

        # Create model docs
        model_doc = await db.modeldoc.create({
            "model": {"connect": {"id": model.id}},
            "markdown_object_name": f"{fake.word()}.md",
            "original_source_object_name": f"{fake.word()}.txt",
            "docs_summary": fake.text(max_nb_chars=200),
        })

        # Create doc sections
        for _ in range(random.randint(3, 7)):
            doc_section = await db.docsection.create({
                "model_doc": {"connect": {"id": model_doc.id}},
                "title": fake.sentence(),
                "content": fake.text(max_nb_chars=500),
                "summary": fake.text(max_nb_chars=100),
            })

            # Create DocSectionQA
            for _ in range(random.randint(2, 5)):
                await db.docsectionqa.create({
                    "doc_section": {"connect": {"id": doc_section.id}},
                    "question": fake.sentence(),
                    "answer": fake.text(max_nb_chars=200),
                })

            # Create chunks
            for _ in range(random.randint(2, 5)):
                chunk = await db.chunk.create({
                    "doc_section": {"connect": {"id": doc_section.id}},
                    "type": random.choice(["text", "code", "table"]),
                    "content": fake.text(max_nb_chars=200),
                    "content_with_context": fake.text(max_nb_chars=300),
                    "summary": fake.text(max_nb_chars=100),
                })

                # Create ChunkQA
                for _ in range(random.randint(1, 3)):
                    await db.chunkqa.create({
                        "chunk": {"connect": {"id": chunk.id}},
                        "question": fake.sentence(),
                        "answer": fake.text(max_nb_chars=150),
                    })

        # Create model code
        await db.modelcode.create({
            "model": {"connect": {"id": model.id}},
        })

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_database())
