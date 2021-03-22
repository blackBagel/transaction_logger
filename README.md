# transaction_logger
A simple python script that'll create a log full of printer transactions with occasional failures

All the variables can be changed using the script arguments  
**Except** the users list which is hardcoded (and not very important anyway ;)
```
usage: create_printer_transactions_log.py [-h] [-n NUM_TRANSACTIONS] [-o OUTPUT_FILE] [-s DAYS_BACK] [-d MAX_DURATION] [-i MAX_INTERVAL] [-b DB_ERROR_CHANCE]
                                          [-k OVERHEAT_ERROR_CHANCE] [-p PID_CHANCE] [-t MIN_DURATION] [-r SERVERS_AMOUNT] [-c PROCESSES_AMOUNT]

__Appends__ printer transactions to a log file

optional arguments:
  -h, --help            show this help message and exit
  -n NUM_TRANSACTIONS, --num-transactions NUM_TRANSACTIONS
                        the number of transactions to be printed (default: 10)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The path for the log created by the script (default: ./transaction.log)
  -s DAYS_BACK, --days-back DAYS_BACK
                        How many days back should the log start its' timestamp (default: 1)
  -d MAX_DURATION, --max-duration MAX_DURATION
                        Maximal duration of a single transaction in seconds (default: 7200)
  -i MAX_INTERVAL, --max-interval MAX_INTERVAL
                        Maximal amount of milliseconds between log lines (default: 2500)
  -b DB_ERROR_CHANCE, --db-error-chance DB_ERROR_CHANCE
                        0 to 1 chance there will be a problem with the connection to the DB at the beginning of the transaction (default: 0.01)
  -k OVERHEAT_ERROR_CHANCE, --overheat-error-chance OVERHEAT_ERROR_CHANCE
                        0 to 1 chance there will be an overheating error in the middle of the transaction (default: 1e-05)
  -p PID_CHANCE, --pid-chance PID_CHANCE
                        0 to 1 chance there will be a pid for the transaction (default: 0.33)
  -t MIN_DURATION, --min-duration MIN_DURATION
                        Minimal duration of a single transaction in seconds (default: 300)
  -r SERVERS_AMOUNT, --servers-amount SERVERS_AMOUNT
                        Number of possible different servers to use (default: 10)
  -c PROCESSES_AMOUNT, --processes-amount PROCESSES_AMOUNT
                        Number of possible different processes to use (default: 9)
```
