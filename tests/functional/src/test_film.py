import pytest

import conftest

# @pytest.mark.asyncio
# async def test_film(init_es_db):
#     conftest.create_es_indexes()
def devision(a, b):
    return a/b

@pytest.mark.asyncio
async def test_film():
    assert(devision(10, 2) == 5)