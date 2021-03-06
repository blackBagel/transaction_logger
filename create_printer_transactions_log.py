# -*- coding: utf-8 -*-
import os
from datetime import timedelta, datetime
import random
import argparse

####################################################################
# Default variables values for controlling the logging behaviour
####################################################################

# Number of transactions to be written to the file
DEFAULT_NUM_TRANSACTIONS = 10

# The path for the log created by the script
DEFAULT_OUTPUT_FILE = os.path.join('./transaction.log')

# Timestamp of the beggining of the log
DEFAULT_DAYS_BACK = 1

# Maximal duration of a single transaction in seconds
DEFAULT_MAX_DURATION = 3600 * 2

# Maximal amount of seconds between log lines
DEFAULT_MAX_INTERVAL = 2500

# 0 to 1 chance there will be a problem with the connection to the DB at the beginning of the transaction
DEFAULT_DB_ERROR_CHANCE = 0.01

# 0 to 1 chance there will be an overheating error in the middle of the transaction
DEFAULT_OVERHEAT_ERROR_CHANCE = 0.00001

# 0 to 1 chance there will be a pid for the transaction
DEFAULT_PID_CHANCE = 0.33

# Minimal duration of a single transaction in seconds (default: 5 minutes)
DEFAULT_MIN_DURATION = 5 * 60

# A list of possible server values
# DEFAULT_SERVERS_LIST = [f'server{chr(server_ID)}' for server_ID in range(ord('A'), ord('A') + 7)]
DEFAULT_SERVERS_AMOUNT = 10

# A list of possible process type values
# DEFAULT_PROCESS_LIST = [chr(process_ID) for process_ID in range(ord('A'), ord('L') + 1)]
DEFAULT_PROCESSES_AMOUNT = 9

# A list of possible user values
DEFAULT_USERS_LIST = ['Leonardo', 'Michaelangelo', 'Rafael', 'Donatello', 'Splinter', 'April', 'Casey']
  
# The maximal possible number of seconds to decrease from the start time so that all events won't start at the same time
DEFAULT_START_RANDOMNESS_FACTOR = 3600

# General Exception Class for errors
class PrintTransactionError(Exception):
  def __init__(self, timestamp):
    self.timestamp = timestamp
    # This message is just a placeholder in case you forgot to add your own message...
    self.message = 'An error occured in the printer'

class DBError(PrintTransactionError):
  def __init__(self, timestamp):
    super().__init__(timestamp)
    self.message = 'connection to database failed, status=2'

class OverheatError(PrintTransactionError):
  def __init__(self, timestamp, print_head_ID):
    super().__init__(timestamp)
    self.print_head_ID = print_head_ID
    self.message = f'print head {self.print_head_ID} failure heated over 50 degrees'

# Represents a single printer head belonging to a single process on a server
# Made the server and pid as properties of the head because it was easier and sufficient for this simple script
class PrinterHead:
  chance_head_move_up = 3

  def __init__(self, ID, server, pid=None):
    self.ID = ID
    self.server = server
    self.pid = pid
    self.x = 0
    self.y = 0
    self.z = 0

  def print_location(self, curr_timestamp, output_file):
    print_log_line(curr_timestamp,
                   server=self.server,
                   severity='INFO',
                   message = f'printer head{self.ID} z-axis: {self.z}',
                   pid=self.pid,
                   output_file=output_file)
    print_log_line(curr_timestamp,
                   server=self.server,
                   severity='INFO',
                   message = f'printer head{self.ID} y-axis: {self.y}',
                   pid=self.pid,
                   output_file=output_file)
    print_log_line(curr_timestamp,
                   server=self.server,
                   severity='INFO',
                   message = f'printer head{self.ID} x-axis: {self.x}',
                   pid=self.pid,
                   output_file=output_file)
    

  def move(self):
    '''
    Always changes the X and Y axis
    There's also a 1 in 3 chance for going up the z axis
    '''
    # Move the x and y axis randomly
    x_direction = random.randint(0, 10) * random.choice([-1, 1])
    y_direction = random.randint(0, 10) * random.choice([-1, 1])

    # There's only a small chance the head will move up
    if random.randint(1, self.chance_head_move_up) == 1:
      z_direction = 1
    else:
      z_direction = 0

    self.x += x_direction  
    self.y += y_direction
    self.z += z_direction

def does_event_happen(event_chance):
  '''
  Raffles randomly whether the event will happen according to its chance
  and returns the result as a boolen
  '''
  
  return random.random() <= event_chance

def print_log_line(timestamp, server, severity, message, output_file, pid=None):
  '''
  prints a single log line into the output_file
  This is the only place where actuall writing to the file occurs
  '''

  timestamp_text = timestamp.strftime("%d/%m/%Y %T")

  if pid:
    pid_text = f' pid={pid}'
  else:
    pid_text = ''

  print(f'{timestamp_text} {severity} {server}{pid_text} {message}', file=output_file)

def print_start_lines(start_time, server, process_type, user, output_file, pid):
  '''
  Prints lines that announce the beginning of a transaction

  This is where the DBError will be raised if it occurs
  '''
  
  latest_timestamp = start_time
  print_log_line(latest_timestamp, server, severity='INFO', message=f'Start process type {process_type}', pid=pid, output_file=output_file)

  latest_timestamp = latest_timestamp + timedelta(milliseconds = random.randint(0, 1500))

  if does_event_happen(GLOBAL_VARS['db_error_chance']):
    raise DBError(latest_timestamp)
  
  print_log_line(latest_timestamp, server, severity='INFO', message=f'connected to database', pid=pid, output_file=output_file)

  latest_timestamp = latest_timestamp + timedelta(milliseconds = random.randint(0, 1500))
  print_log_line(latest_timestamp, server, severity='INFO', message=f'user {user} initiated action build', pid=pid, output_file=output_file)

  return latest_timestamp

def print_end_lines(time, server, process_type, pid, output_file, error = None):
  '''
  Prints lines that announce the end of a transaction
  Prints errors and their messages if they occured

  Only one error can happen in each transaction
  '''
  
  curr_timestamp = time
  if not error:
    print_log_line(curr_timestamp, server, severity='INFO', message=f'End process type {process_type} Successfully', pid=pid, output_file=output_file)
  else:
    print_log_line(curr_timestamp, server, severity='ERROR', message=error, pid=pid, output_file=output_file)
    print_log_line(curr_timestamp, server, severity='ERROR', message=f'End process type {process_type} Failed', pid=pid, output_file=output_file)
  
  return curr_timestamp

def print_printer_heads_movement(start_time, server, printer_heads, output_file, pid):
  '''
  Handles the logic of the head location printing

  The only function that will raise an Overheat Error if it occurs
  '''
  
  duration_in_seconds = random.randint(GLOBAL_VARS['min_duration'], GLOBAL_VARS['max_duration'])
  end_time = start_time + timedelta(seconds = duration_in_seconds)
  latest_timestamp = start_time

  # Print movement in transaction
  while latest_timestamp < end_time:
    for printer_head in printer_heads:
      printer_head.print_location(latest_timestamp, output_file=output_file)

      if does_event_happen(GLOBAL_VARS['overheat_error_chance']):
        raise OverheatError(latest_timestamp, printer_head.ID)

      printer_head.move()
    
    latest_timestamp += timedelta(milliseconds = random.randint(0, GLOBAL_VARS['max_interval']))
  
  return latest_timestamp

def do_single_transaction(server, process_type, user, start_time, printer_heads, output_file, pid=None):
  '''
  Calls the start, printer_heads_movement and end printing functions

  Errors are exceptions so they're handled either way in the end printing func 
  '''
  try:
    latest_timestamp = print_start_lines(start_time = start_time,
                                         server = server,
                                         user = user,
                                         process_type = process_type,
                                         pid = pid,
                                         output_file=output_file)
  
    latest_timestamp = print_printer_heads_movement(start_time=latest_timestamp,
                                                    server = server,
                                                    printer_heads = printer_heads,
                                                    pid = pid,
                                                    output_file=output_file)
  except PrintTransactionError as e:
    error = e.message

    # latest_timestamp always has to exist so print_end_lines will continue from there
    latest_timestamp = e.timestamp
  else:
    error = None
  finally:
    latest_timestamp = print_end_lines(time = latest_timestamp,
                                    server = server,
                                    process_type = process_type,
                                    pid = pid,
                                    error = error,
                                    output_file=output_file)
    return latest_timestamp                                

def print_log(output_file):
  '''
  Runs the printing transactions with random properties

  The transaction properties are sent across functions 
  since they're unique per transaction
  '''
  latest_timestamp_of_server = dict()
  for i in range(GLOBAL_VARS['num_transactions']):
    server = random.choice(GLOBAL_VARS['servers_list'])
    process_type = random.choice(GLOBAL_VARS['process_type_list'])
    user = random.choice(GLOBAL_VARS['users_list'])

    if server in latest_timestamp_of_server:
      start_time = latest_timestamp_of_server[server]
    else:
      start_time = GLOBAL_VARS['start_date']

    start_rand_delta = timedelta(seconds=random.randint(1, GLOBAL_VARS['start_randomness_factor']))
    start_time += start_rand_delta

    pid = None
    if does_event_happen(GLOBAL_VARS['pid_chance']):
      pid = random.randint(1001, 9999)

    printer_heads = [
                     PrinterHead(ID = 'A', server=server, pid = pid),
                     PrinterHead(ID = 'B', server=server, pid = pid),
                     PrinterHead(ID = 'C', server=server, pid = pid)
                     ]

    latest_timestamp_of_server[server] = do_single_transaction(server=server,
                                                               process_type=process_type,
                                                               user=user,
                                                               start_time = start_time,
                                                               printer_heads=printer_heads,
                                                               pid=pid,
                                                               output_file=output_file)

def parse_script_arguments():
  # Create the parser
  parser = argparse.ArgumentParser(description='Appends printer transactions to a log file')

  # Adding the possible the arguments
  parser.add_argument('-n',
                      '--num-transactions',
                       action='store',
                       type=int,
                       default=DEFAULT_NUM_TRANSACTIONS,
                       help=f'the number of transactions to be printed (default: {DEFAULT_NUM_TRANSACTIONS})')
  parser.add_argument('-o',
                      '--output-file',
                      action='store',
                      type=str,
                      default=DEFAULT_OUTPUT_FILE,
                      help=f'The path for the log created by the script (default: {DEFAULT_OUTPUT_FILE})')
  parser.add_argument('-s',
                      '--days-back',
                      action='store',
                      type=int,
                      default=2,
                      help=f'How many days back should the log start its\' timestamp (default: {DEFAULT_DAYS_BACK})')
  parser.add_argument('-d',
                      '--max-duration',
                      action='store',
                      type=int,
                      default=DEFAULT_MAX_DURATION,
                      help=f'Maximal duration of a single transaction in seconds (default: {DEFAULT_MAX_DURATION})')
  parser.add_argument('-i',
                      '--max-interval',
                      action='store',
                      type=int,
                      default=DEFAULT_MAX_INTERVAL,
                      help=f'Maximal amount of milliseconds between log lines (default: {DEFAULT_MAX_INTERVAL})')
  parser.add_argument('-b',
                      '--db-error-chance',
                      action='store',
                      type=float,
                      default=DEFAULT_DB_ERROR_CHANCE,
                      help=f'0 to 1 chance there will be a problem with the connection to the DB at the beginning of the transaction (default: {DEFAULT_DB_ERROR_CHANCE})')
  parser.add_argument('-k',
                      '--overheat-error-chance',
                      action='store',
                      type=float,
                      default=DEFAULT_OVERHEAT_ERROR_CHANCE,
                      help=f'0 to 1 chance there will be an overheating error in the middle of the transaction (default: {DEFAULT_OVERHEAT_ERROR_CHANCE})')
  parser.add_argument('-p',
                      '--pid-chance',
                      action='store',
                      type=float,
                      default=DEFAULT_PID_CHANCE,
                      help=f'0 to 1 chance there will be a pid for the transaction (default: {DEFAULT_PID_CHANCE})')
  parser.add_argument('-t',
                      '--min-duration',
                      action='store',
                      type=int,
                      default=DEFAULT_MIN_DURATION,
                      help=f'Minimal duration of a single transaction in seconds (default: {DEFAULT_MIN_DURATION})')
  parser.add_argument('-r',
                      '--servers-amount',
                      action='store',
                      type=int,
                      default=DEFAULT_SERVERS_AMOUNT,
                      help=f'Number of possible different servers to use (default: {DEFAULT_SERVERS_AMOUNT})')
  parser.add_argument('-c',
                      '--processes-amount',
                      action='store',
                      type=int,
                      default=DEFAULT_PROCESSES_AMOUNT,
                      help=f'Number of possible different processes to use (default: {DEFAULT_PROCESSES_AMOUNT})')

  args = parser.parse_args()

  global GLOBAL_VARS
  GLOBAL_VARS = vars(args)

  # Process the inputs into python usable objects
  GLOBAL_VARS['start_date'] = datetime.today() - timedelta(days=GLOBAL_VARS['days_back'])
  GLOBAL_VARS['servers_list'] = [f'server{chr(server_ID)}' for server_ID in range(ord('A'), ord('A') + GLOBAL_VARS['servers_amount'])]
  GLOBAL_VARS['process_type_list'] = [chr(process_ID) for process_ID in range(ord('A'), ord('A') + GLOBAL_VARS['processes_amount'])]
  GLOBAL_VARS['users_list'] = DEFAULT_USERS_LIST
  GLOBAL_VARS['start_randomness_factor'] = DEFAULT_START_RANDOMNESS_FACTOR

if __name__ == '__main__':
  parse_script_arguments()

  with open(GLOBAL_VARS['output_file'], mode='a') as log_file:
    print_log(log_file)

  print(f'Successfully wrote into {GLOBAL_VARS["output_file"]}')