HELP_TEXT = """How to use pySMASH:
    \n 1. Set Desired Sleep times and iteration counts.
    \n 2. Click Capture clicks to record a list of coords.
    \n - RIGHT CLICK to stop capturing clicks for that list.
    \n - Your list will populate under the Start Clicking button.
    \n 3. Repeat for as many lists as needed.
    \n 4. Click "Start Clicking" to begin the automated clicking process.
    \n NOTE: Move mouse to a corner "quickly" to cancel process.
    \n 
    \n OPTIONS:
    \n Sleep Time between clicks:
    \n - Time between individual clicks in a list.
    \n Sleep Time between lists:
    \n - Time between lists of clicks.
    \n Iteration Count:
    \n - Number of random lists to run.
    \n - OR number of times to follow every list in sequence.
    \n Use Random Order:
    \n - If checked, will execute one list at random per iteration
    \n - If unchecked, will execute each list in order (all lists = 1 iteration)
    \n Configuration Management
    \n Save config - Save all configuration options to a .json file.
    \n Load config - Load all configuration options from a .json file.
    """

default_sleep_time = "1"
default_sleep_between_lists_time = "3"
default_iteration_count = "10"
