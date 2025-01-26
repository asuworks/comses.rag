import asyncio
import random
from datetime import datetime
from faker import Faker
import asyncpg

# Initialize Faker
fake = Faker()


async def create_database_if_not_exists():
	try:
		# Connect to default postgres database first
		sys_conn = await asyncpg.connect(
			user='postgres',
			password='postgres',
			database='postgres',
			host='localhost',
			port=54320
		)

		# Check if database exists
		exists = await sys_conn.fetchval(
			"SELECT 1 FROM pg_database WHERE datname = 'comses_metadata_fake_db'"
		)

		if not exists:
			await sys_conn.execute("CREATE DATABASE comses_metadata_fake_db")
			print("Database 'comses_metadata_fake_db' created successfully")
		else:
			print("Database 'comses_metadata_fake_db' already exists")

		await sys_conn.close()

	except Exception as e:
		print(f"An error occurred: {e}")


def generate_random_model():
	first_published = fake.date_time_between(start_date='-5y', end_date='now')
	last_published = fake.date_time_between(start_date=first_published,
	                                        end_date='now')
	last_modified = fake.date_time_between(start_date=last_published,
	                                       end_date='now')

	return (
		fake.catch_phrase(),  # title
		fake.text(max_nb_chars=500),  # description
		[fake.name() for _ in range(random.randint(1, 5))],  # contributors
		[fake.url() for _ in range(random.randint(0, 3))],  # references
		fake.url(),  # permanent_url
		fake.sentence() if random.random() > 0.3 else None,
		# associated_publication
		[fake.word() for _ in range(random.randint(1, 5))],  # tags
		random.choice(['NetLogo', 'Mesa', 'Repast', 'AnyLogic', 'MASON']),
		# framework
		random.choice(['Python', 'Java', 'NetLogo', 'R', 'C++']),
		# programming_language
		random.random() < 0.05,  # is_marked_spam
		last_modified,
		random.random() < 0.3,  # peer_reviewed
		random.random() < 0.1,  # featured
		random.random() < 0.15,  # is_replication
		random.random() < 0.9,  # live
		first_published,
		last_published,
		random.randint(0, 10000)  # downloads
	)


async def seed_database(num_records=100):
	conn = await asyncpg.connect(
		user='postgres',
		password='postgres',
		database='comses_metadata_fake_db',
		host='localhost',
		port=54320
	)

	await conn.execute('''
    CREATE TABLE IF NOT EXISTS models (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        contributors TEXT[],
        reference_links TEXT[],
        permanent_url TEXT,
        associated_publication TEXT,
        tags TEXT[],
        framework TEXT,
        programming_language TEXT,
        is_marked_spam BOOLEAN,
        last_modified TIMESTAMP,
        peer_reviewed BOOLEAN,
        featured BOOLEAN,
        is_replication BOOLEAN,
        live BOOLEAN,
        first_published_at TIMESTAMP,
        last_published_on TIMESTAMP,
        downloads INTEGER
    )
    ''')

	records = [generate_random_model() for _ in range(num_records)]

	await conn.executemany('''
        INSERT INTO models (
            title, description, contributors, reference_links, permanent_url,
            associated_publication, tags, framework, programming_language,
            is_marked_spam, last_modified, peer_reviewed, featured,
            is_replication, live, first_published_at, last_published_on, downloads
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18
        )
    ''', records)

	await conn.close()


async def main():
	await create_database_if_not_exists()
	await seed_database(100)


if __name__ == "__main__":
	asyncio.run(main())
