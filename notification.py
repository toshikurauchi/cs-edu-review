import os
import platform


def notify(title, message):
    '''
    Source: https://www.pythongasm.com/desktop-notifications-with-python/
    '''
    plt = platform.system()

    if plt == 'Darwin':
        command = f'''
        osascript -e 'display notification "{message}" with title "{title}"'
        '''
    elif plt == 'Linux':
        command = f'''
        notify-send "{title}" "{message}"
        '''
    else:
        return

    os.system(command)
