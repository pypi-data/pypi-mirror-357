import asyncio
from svo_client.chunker_client import (
    ChunkerClient, 
    SVOServerError, 
    SVOJSONRPCError, 
    SVOHTTPError, 
    SVOConnectionError, 
    SVOTimeoutError
)

async def main():
    text = (
        "Although the project was initially considered too ambitious by many experts, "
        "the team managed to overcome numerous obstacles, demonstrating not only technical proficiency but also remarkable perseverance. "
        "Хотя проект изначально считался слишком амбициозным многими экспертами, команда сумела преодолеть многочисленные препятствия, "
        "продемонстрировав не только техническое мастерство, но и удивительное упорство. "
        "Хоча проєкт спочатку вважався надто амбітним багатьма експертами, команда змогла подолати численні перешкоди, "
        "продемонструвавши не лише технічну майстерність, а й дивовижну наполегливість."
    )
    async with ChunkerClient() as client:
        # Получение чанков
        try:
            chunks = await client.chunk_text(text)
        except SVOTimeoutError as e:
            print(f"Timeout error: {e}")
            chunks = []
        except SVOConnectionError as e:
            print(f"Connection error: {e}")
            chunks = []
        except SVOHTTPError as e:
            print(f"HTTP error: {e}")
            chunks = []
        except SVOJSONRPCError as e:
            print(f"JSON-RPC error: {e}")
            chunks = []
        except SVOServerError as e:
            print(f"SVO server error: {e}")
            chunks = []
        except ValueError as e:
            print(f"Validation error: {e}")
            chunks = []
        print("Chunks:")
        for chunk in chunks:
            print(chunk)
        # Реконструкция текста
        reconstructed = client.reconstruct_text(chunks)
        print("\nReconstructed text:")
        print(reconstructed)
        # Health
        try:
            health = await client.health()
            print("\nHealth:", health)
        except SVOTimeoutError as e:
            print(f"Health check timeout error: {e}")
        except SVOConnectionError as e:
            print(f"Health check connection error: {e}")
        except SVOHTTPError as e:
            print(f"Health check HTTP error: {e}")
        except SVOJSONRPCError as e:
            print(f"Health check JSON-RPC error: {e}")
        # Help
        try:
            help_info = await client.get_help()
            print("\nHelp:", help_info)
        except SVOTimeoutError as e:
            print(f"Help timeout error: {e}")
        except SVOConnectionError as e:
            print(f"Help connection error: {e}")
        except SVOHTTPError as e:
            print(f"Help HTTP error: {e}")
        except SVOJSONRPCError as e:
            print(f"Help JSON-RPC error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 