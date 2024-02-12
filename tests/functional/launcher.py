import os

if __name__ == "__main__":
    # Wait for elastic and redis creation
    exec(open('utils/es_waiter.py').read())
    exec(open('utils/redis_waiter.py').read())

    os.system("pytest")
