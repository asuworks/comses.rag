import subprocess
import sys

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if process.returncode != 0:
        print(f"Error executing command: {command}")
        print(error.decode('utf-8'))
        sys.exit(1)
    return output.decode('utf-8')

def reset_database():
    print("Resetting the database...")

    # Drop the database schema
    print("Dropping the database schema...")
    run_command("prisma db push --force-reset --accept-data-loss --schema=../src/shared/prisma/models-db-schema.prisma")

    # Apply migrations
    # print("Applying migrations...")
    # run_command("prisma migrate deploy --schema=../src/shared/prisma/models-db-schema.prisma")

    # Generate Prisma client
    print("Generating Prisma client...")
    run_command("prisma generate --schema=../src/shared/prisma/models-db-schema.prisma")

    print("Database reset completed successfully.")

if __name__ == "__main__":
    reset_database()