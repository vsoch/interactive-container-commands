import threading


def run_container(name="ubuntu", entrypoint="bash"):
    """ This function starts an interactive session with a container of interest.
    Run with threading, we can know when the container is exited for a final save.
    """
    import random
    import string
    import pty
    import subprocess
    import select
    import sys
    import os

    def generate_name():
        return "".join([random.choices(string.ascii_lowercase)[0] for x in range(8)])

    # This is ensuring every based image has just one saved name. This could
    # be managed more elegantly.
    random_name = name + "-" + generate_name()
    pty, tty = pty.openpty()
    p = subprocess.Popen(
        ["docker", "run", "-it", "--rm", "--name", random_name, name, entrypoint],
        stdin=tty,
        stdout=tty,
        stderr=tty,
    )

    # Keep updating the terminal until the user is done!
    # This is where we can read in commands and respond to user requests
    while p.poll() is None:
        r, _, _ = select.select([sys.stdin, pty], [], [])
        if sys.stdin in r:
            input_from_terminal = os.read(sys.stdin.fileno(), 10240)

            # Saving the state!
            if "#save" in input_from_terminal.decode("utf-8"):
                save_container(name, random_name)
                os.write(sys.stdout.fileno(), b"Saving container...\n")
            os.write(pty, input_from_terminal)
        elif pty in r:
            output_from_docker = os.read(pty, 10240)
            os.write(sys.stdout.fileno(), output_from_docker)

    print("Container exited.")
    return random_name


def save_container(name, container_name, suffix="-saved"):
    """
    Save a temporary container name back to the main container name
    """
    import subprocess
    import shutil
    import tempfile
    import os

    # Probably this should be random!
    p = subprocess.Popen(["docker", "commit", container_name, container_name + "-tmp"])
    p.wait()

    # Create a temporary context
    tempdir = tempfile.mkdtemp()
    dockerfile = os.path.join(tempdir, "Dockerfile")
    with open(dockerfile, "w") as fd:
        fd.write("FROM %s-tmp\n" % container_name)
    os.chdir(tempdir)
    p = subprocess.Popen(["docker", "build", "--squash", "-t", name + suffix, "."])
    p.wait()
    shutil.rmtree(tempdir)


def main():
    """ Start a thread to run the container, and we can run other tasks too.
    """
    # threading.Thread(target=run_container, name='run-container').start()
    # Perform other tasks while the thread is running.
    name = run_container()

    # Stop and remove the temporary container.
    p = subprocess.Popen(["docker", "stop", name])
    p.wait()
    p = subprocess.Popen(["docker", "rm", name])
    p.wait()


if __name__ == "__main__":
    main()
