import threading
import time
import random
import sys

def print_hello_task():
    # Generate a random number
    rand_num = random.randint(1, 100)
    # Print first message
    print(f"Hello world {rand_num} 1st time")
    # Wait for 1 second
    time.sleep(5)
    # Print second message with the same random number
    print(f"Hello world {rand_num} 2nd time")

def main():
    print("Type 'Say hello' to start the task or 'exit' to quit:")
    while True:
        # Read user input
        user_input = input().strip()
        
        if user_input.lower() == "say hello":
            # Create and start a new thread for the task
            thread = threading.Thread(target=print_hello_task)
            thread.start()
        elif user_input.lower() == "exit":
            print("Exiting program.")
            break
        else:
            print("Invalid input. Please type 'Say hello' or 'exit'.")

if __name__ == "__main__":
    main()