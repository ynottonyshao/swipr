"""
scan TAMU student ID cards and TX driver's licences
for attendance taking
"""

import time
import getpass
import signal

ADMIN_ID = ['6016426592443531', 'PHILIP RITCHEY']
STUDENT_ID = '60'
TX_DL = 'TX'

SWIPE_LOG = 'swipe_log'
UIN_DICT = 'uin_dict'

def signal_handler(sig, frame) -> None:
    # ignore
    pass

def admin() -> None:
    """
    access admin functions
    """

    action = input('admin> ')
    if action.lower() in ['exit', 'quit']:
        print('exiting...')
        exit(1)
    print('nothing happened...')

def get_uin() -> int:
    import re
    uin = input('Please enter your UIN: ')
    result = re.match(r'\d{3}00\d{4}', uin)
    while not result:
        print('Invalid UIN.')
        uin = input('Please enter your UIN: ')
        result = re.match(r'\d{3}00\d{4}', uin)
    return result.group(0)

def main() -> None:
    """
    main loop for ID scanning
    """

    # read in UIN dictionary
    uin_dict = dict()
    try:
        with open(UIN_DICT) as uin_dict_file:
            for line in uin_dict_file:
                key, value = line.split(':')
                if key in uin_dict:
                    print('[WARNING] key ({:s}) already exists, ignoring new value.'.format(key))
                else:
                    uin_dict[key] = value
    except FileNotFoundError:
        pass

    with open(SWIPE_LOG, 'at') as swipe_log:
        while True:
            # scan ID
            try:
                id_data = getpass.getpass('swipe ID...')
            except EOFError:
                print()
                continue
            id_type = id_data[1:3]
            if id_type == TX_DL:
                # Texas driver's license
                id_key = ' '.join(id_data[16:].split('^')[0].split('$')[::-1])
            else:
                # student/other ID
                id_key = id_data[1:17]
            event = '{:.4f}\t{:s}'.format(time.time(), id_key)
            #print(event)
            swipe_log.write(event + '\n')
            if id_key not in uin_dict:
                print('This is the first time this ID has been swiped.')
                uin = get_uin()
                uin_dict[id_key] = uin
                with open(UIN_DICT,'at') as f:
                    f.write('{}:{}\n'.format(id_key, uin))
            print('Howdy, {:s}'.format(uin_dict[id_key]))
            if id_key in ADMIN_ID:
                admin()



if __name__ == '__main__':
    # ignore SIGINT, SIGTSTP
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)

    main()
