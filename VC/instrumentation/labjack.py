from labjackDriver import LabJackU6Driver
import asyncio

def main() -> None:
    instrumentation = None
    try:
        instrumentation = LabJackU6Driver()
        print("instrumentation Driver configured")
    except Exception as e:
        print(f"Failed to initialize LabJackU6Driver: {e}")
        exit(1)

    asyncio.run(instrumentation.stream())

if __name__ == "__main__":
    main()