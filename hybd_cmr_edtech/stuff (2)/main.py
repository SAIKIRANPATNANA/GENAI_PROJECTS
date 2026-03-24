import concurrent.futures
from help1 import getResponse as getResponse1
from help2 import getResponse as getResponse2

def main():
    # Execute the functions in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the functions and gather futures
        future1 = executor.submit(getResponse1)
        future2 = executor.submit(getResponse2)

        # Retrieve the results
        response1 = future1.result()
        response2 = future2.result()

    # Concatenate the responses with a newline character
    combined_output = response1 + "\n\n" + response2

    # Print or handle the concatenated output
    print(combined_output)

if __name__ == "__main__":
    main()
