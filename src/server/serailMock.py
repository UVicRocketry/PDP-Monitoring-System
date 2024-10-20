import time

def serial_feedback_mock(
    valve: str, 
    action: str
) -> dict:
    '''
    Name:
        serial_feedback(command: string, valve: string, action: string) -> dict
    Args:
        valve: the valve that the command is for
        action: the action to take on the valve
    Desc:
        Creates a dictionary to send over the websocket
    '''
    action = action if action == "OPEN" or action == "CLOSE" else "TRANSIT"
    return {
        'identifier': 'FEEDBACK',
        'valve': valve,
        'action': action
    }