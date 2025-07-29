from bear_utils.extras._tools import copy_to_clipboard_async


async def copy(output: str) -> int:
    """
    Asynchronously copy the output to the clipboard.

    Args:
        output (str): The output to copy to the clipboard.

    Returns:
        int: The return code of the command.
    """
    return await copy_to_clipboard_async(output)


if __name__ == "__main__":
    import asyncio

    async def main():
        result = await copy("Hello, World!")
        print(f"Copy result: {result}")

    asyncio.run(main())
