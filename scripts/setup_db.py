import asyncio

import asyncpg


async def main():
    conn = await asyncpg.connect(
        user="postgres",
        password="root",
        host="localhost",
        port=5432,
        database="postgres",
    )

    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1",
        "arshi_ecommerce",
    )

    if not exists:
        await conn.execute("CREATE DATABASE arshi_ecommerce")
        print("Created database arshi_ecommerce")
    else:
        print("Database arshi_ecommerce already exists")

    await conn.close()

    conn2 = await asyncpg.connect(
        user="postgres",
        password="root",
        host="localhost",
        port=5432,
        database="arshi_ecommerce",
    )
    print("Connected to arshi_ecommerce: OK")
    await conn2.close()


if __name__ == "__main__":
    asyncio.run(main())
