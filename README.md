# Container Squash

This is a hacky attempt to write a proof of concept that will allow me to:

1. Build a container
2. Interactively shell into it
3. Save it incrementally while it's running (or more generally, allow support for a command while in the container)
4. Exit and save state.

We will do this with incremental runs of docker commit, and then build with squash.
Squash (at least on my old Ubuntu machine with an older version of Docker) requires experimental mode, so add:

```
{ 
    "experimental": true 
}
```
to `/etc/docker/daemon.json`, e.g.,:

```bash
sudo vim /etc/docker/daemon.json
```

And then restart

```bash
sudo service docker restart
```

Without experimental you'll see an error in the console.

## Example

I started with zero images to ensure I could watch what is going on.

```bash
$ docker system prune --all
```

Then I ran the script (you'll see a base image ubuntu being pulled, and yes the name of the interactive container
could easily be a command line argument but it's hard coded for this proof of concept.)

```bash
$ python save_state.py
```

**under development**
