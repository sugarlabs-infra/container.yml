# container.yml

container.yml is a little script aiming to make docker container
configurations live in files not as commands.  It builds from a project's
Dockerfile (`container.yml build`) and can run the container with settings
defined in the container.yml file (`container.yml start [-d]`).

Inspired by [Docker Compose](https://github.com/docker/compose).

# Configuration

* The `env`, `volumes` and `ports` options contain a list of options.  They
  are all appended with `-e`/`-v`/`-p` and individually added to the options
  list.
* The `env-file` reads environment key/value pairs form a yaml file
* The `cpu` option sets the percentage of cpu a container gets
* When running in daemon mode, the container automattically restarts on exit
* All other options are passed directly to docker
* The `cpu` and `memory` options are also used during container build if the
  `-l` option is used.  However, the build process can be very slow if it
  is restricted.

# Examples

    volumes:
     - /var/lib/docker:/var/lib/docker
    privileged: true

    memory: 128m
    cpu: 10


---

    volumes:
     - /srv/socialhelp/sso-data:/data
    ports:
     - 5005:5000
    env-file: /srv/socialhelp/discourse-api-env.txt

    memory: 128m
    cpu: 10
