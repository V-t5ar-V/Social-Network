import asyncio

async def race(times, seconds, racer):
    for i in range(times):
        await asyncio.sleep(seconds)
        print("\033[0m", i, f"racer : {racer}")
    print(f"\033[31m{racer} finished")
    return True

async def main():
    await asyncio.gather(race(10, 0.5, "John"), race(5, 1, "Layla"))

asyncio.run(main())
