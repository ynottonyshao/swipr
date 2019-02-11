#! /usr/bin/env python3

"""
scan TAMU student ID cards and TX driver's licences
for attendance taking
"""

import time
import getpass
import signal
import re
from typing import Dict

ADMIN_ID = ['6016426592443531', 'PHILIP RITCHEY']
STUDENT_ID = '60'
TX_DL = 'TX'

SWIPE_LOG = 'swipe_log'
UIN_DICT = 'uin_dict'
ROSTER = 'roster'

UIN_PATTERN = r'^\d{3}00\d{4}$'
TAMU_ID_PATTERN = r'%(\d+)\?;((\d+)\?\+(\d+)\?)?'

def signal_handler(sig, frame) -> None:
    # ignore
    pass

def admin() -> None:
    """
    access admin functions
    """

    action = input('admin> ').lower()
    if action in ['exit', 'quit']:
        print('(admin) exiting...')
        exit(1)
    elif action in ['test']:
        print('(admin) entering test mode')
        while True:
            try:
                id_data = getpass.getpass('(admin) swipe ID (mag stripe AWAY from LED)...')
                if len(id_data) == 0:
                    print('<empty>')
                    break
                else:
                    print(id_data)
            except EOFError:
                print()
                continue
    print('(admin) nothing happened...')

def get_uin() -> int:
    uin = input('Please enter your UIN: ').strip()
    result = re.match(UIN_PATTERN, uin)
    while not result:
        print('Invalid UIN.')
        uin = input('Please enter your UIN: ').strip()
        result = re.match(UIN_PATTERN, uin)
    return result.group(0)

def init_uin_dict() -> Dict:
    uin_dict = dict()
    try:
        with open(UIN_DICT) as uin_dict_file:
            for line in uin_dict_file:
                key, value = line.strip().split(':')
                if key in uin_dict:
                    print('[WARNING] key ({:s}) already exists, replacing old value.'.format(key))
                uin_dict[key] = value
    except FileNotFoundError:
        pass
    return uin_dict

def init_roster() -> Dict:
    roster = dict()
    try:
        with open(ROSTER) as roster_file:
            for line in roster_file:
                last, first_middle, uin = line.strip().split('\t')
                if uin in roster:
                    print('[WARNING] UIN ({:s}) already exists, skipping'.format(uin))
                else:
                    roster[uin] = (last, first_middle)
    except FileNotFoundError:
        pass
    return roster

def main() -> None:
    """
    main loop for ID scanning
    """

    # read in UIN dictionary
    uin_dict = init_uin_dict()

    # read in roster
    roster = init_roster()

    with open(SWIPE_LOG, 'at') as swipe_log:
        while True:
            # scan ID
            print()
            try:
                id_data = getpass.getpass('swipe ID (mag stripe AWAY from LED)...')
                if len(id_data) == 0:
                    continue
            except EOFError:
                print()
                continue

            # is it a UIN directly?
            result = re.match(UIN_PATTERN, id_data)
            if result:
                uin = result.group(0)
                id_key = uin
            else:
                id_type = id_data[1:3]
                if id_type == TX_DL:
                    # Texas driver's license
                    id_key = ' '.join(id_data[16:].split('^')[0].split('$')[::-1])
                else:
                    # student/other ID
                    result = re.match(TAMU_ID_PATTERN, id_data)
                    if not result:
                        print('[ERROR] swipe error, please swipe again.')
                        continue
                    id_key = result.group(1)
                if id_key not in uin_dict:
                    print('This seems to be the first time this ID has been swiped.')
                    uin = get_uin()
                    uin_dict[id_key] = uin
                    with open(UIN_DICT,'at') as f:
                        f.write('{}:{}\n'.format(id_key, uin))
                else:
                    uin = uin_dict[id_key]
            if uin not in roster:
                print('The UIN associated with this ID is not in the roster.')
                print('Please verify your UIN.')
                uin = get_uin()
                uin_dict[id_key] = uin
                with open(UIN_DICT,'at') as f:
                    f.write('{:s}:{:s}\n'.format(id_key, uin))
                if uin not in roster:
                    first_middle = input('first [and middle] name: ')
                    last = input('last name: ')
                    with open('roster', 'at') as f:
                        f.write('{:s}\t{:s}\t{:s}\n'.format(last, first_middle, uin))
                    roster[uin] = (last, first_middle)
            last, first_middle = roster[uin]
            event = '{:.4f} {:s} {:s} {:s} {:s}'.format(time.time(), id_key, first_middle, last, uin)
            swipe_log.write(event + '\n')
            print('Howdy, {:s} {:s}!'.format(first_middle, last))
            if id_key in ADMIN_ID:
                admin()

if __name__ == '__main__':
    # ignore SIGINT, SIGTSTP
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)

    main()
