#!/usr/bin/env python3
"""Setup test data for ChoreBoss FastAPI backend."""

import asyncio
import bcrypt
from choreboss.models.chore import Chore
from choreboss.models.people import People
from choreboss.models import Base
from choreboss.config import get_config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker


async def setup_test_data():
    """Create database and load test data."""
    config = get_config()
    
    print(f"Database URL: {config.database_url}")
    
    # Create engine
    engine = create_async_engine(config.database_url, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session factory
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Add test data
    async with AsyncSessionLocal() as session:
        # Create people
        person1 = People(
            first_name='Alice',
            last_name='Smith',
            birthday='2000-01-15',
            pin=bcrypt.hashpw(b'1234', bcrypt.gensalt()).decode(),
            is_admin=True,
            sequence_num=1
        )
        person2 = People(
            first_name='Bob',
            last_name='Jones',
            birthday='2001-05-20',
            pin=bcrypt.hashpw(b'5678', bcrypt.gensalt()).decode(),
            is_admin=False,
            sequence_num=2
        )
        
        # Create chores
        chore1 = Chore(
            name='Wash dishes',
            description='Wash all dishes and put them away',
            person_id=1
        )
        chore2 = Chore(
            name='Vacuum living room',
            description='Vacuum the living room carpet',
            person_id=2
        )
        chore3 = Chore(
            name='Clean bathroom',
            description='Clean the bathroom sink, toilet, and shower',
            person_id=None  # Unassigned
        )
        
        session.add_all([person1, person2, chore1, chore2, chore3])
        await session.commit()
        
        print("✅ Test data loaded successfully!")
        print()
        print("People:")
        print("  ID 1: Alice Smith (is_admin=True)")
        print("        PIN: 1234")
        print("  ID 2: Bob Jones (is_admin=False)")
        print("        PIN: 5678")
        print()
        print("Chores:")
        print("  1. Wash dishes (assigned to Alice)")
        print("  2. Vacuum living room (assigned to Bob)")
        print("  3. Clean bathroom (unassigned)")
        print()
        print("To test:")
        print("  1. Start FastAPI: python api_run.py")
        print("  2. Run tests: python test_integration.py")
        print("  3. Or Flask frontend: python flask_bridge.py")
        print("     Then visit: http://localhost:8055")


if __name__ == '__main__':
    asyncio.run(setup_test_data())
