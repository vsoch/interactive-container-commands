# Interactive Container Commands

This is an attempt to write a proof of concept that will allow me to:

1. Build a container
2. Interactively shell into it
3. Save it incrementally while it's running (or more generally, allow support for a command while in the container)
4. Exit and save state.

As a first example, I want to write `#save` and have that be enough to save the container state. 
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

Note that you can watch this proof of concept [here](https://www.youtube.com/watch?v=ZFwapu4I-pg).
I started with zero images to ensure I could watch what is going on.

```bash
$ docker system prune --all
```

Then I ran the script (you'll see a base image ubuntu being pulled, and yes the name of the interactive container
could easily be a command line argument but it's hard coded for this proof of concept.)

```bash
$ python save_state.py
```
```bash
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
08c01a0ec47e: Already exists 
Digest: sha256:669e010b58baf5beb2836b253c1fd5768333f0d1dbcb834f7c07a4dc93f474be
Status: Downloaded newer image for ubuntu:latest
```

Now here we are in the container!
```
root@4f4f45c2a719:/# ls
ls
bin   dev  home  lib32  libx32  mnt  proc  run   srv  tmp  var
boot  etc  lib   lib64  media   opt  root  sbin  sys  usr
```

Let's touch a random filename:

```bash
root@4f4f45c2a719:/# touch FILENAME
touch FILENAME
```

And now the moment of truth! Let's ask the container to save.

```bash
root@4f4f45c2a719:/# #save
sha256:7fb56de01d2812e1fed449771acc4ac6fc82654056826e81b5de2801ef32aeaf
[+] Building 1.4s (5/5) FINISHED                                                                                                     
 => [internal] load build definition from Dockerfile                                                                            0.0s
 => => transferring dockerfile: 68B                                                                                             0.0s
 => [internal] load .dockerignore                                                                                               0.0s
 => => transferring context: 2B                                                                                                 0.0s
 => [internal] load metadata for docker.io/library/ubuntu-bkkpobav-tmp:latest                                                   0.0s
 => [1/1] FROM docker.io/library/ubuntu-bkkpobav-tmp                                                                            0.0s
 => exporting to image                                                                                                          0.0s
 => => exporting layers                                                                                                         0.0s
 => => writing image sha256:fc2769bf442860dacc75d950bb9c80e44240d3311bbf42f96788dd4636f55bfb                                    0.0s
 => => naming to docker.io/library/ubuntu-saved                                                                                 0.0s
Saving container...
#save
root@4f4f45c2a719:/# 
```

Ahh, okay! So let's exit and see if we have the container...

```bash
$ docker images | grep ubuntu-saved
ubuntu-saved                       latest                         687973b77fbc   About a minute ago   72.8MB
```
Now the moment of truth!

```bash
$ docker run -it --rm ubuntu-saved
root@44fe4a68550f:/# ls
FILENAME  bin  boot  dev  etc  home  lib  lib32  lib64  libx32  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var
```

THERE IT IS! AHH!!

This is super cool! I think we should make a little library around this.
