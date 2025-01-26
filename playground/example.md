# Setup

First clone the repository if you haven't already:
```bash
$ git clone https://github.com/comses/comses.net.git
```

## Build the codebase: Linux CLI

These instructions assume you're familiar with the Linux / macOS command line. They *might* work on a Windows Subsystem for Linux setup + Docker engine but we don't have the resources to test that - if you get that working please let us know [by submitting an issue](https://github.com/comses/comses.net/issues/new) with the relevant details.

Alternatively, running Linux in a virtual machine or Windows Subsystem for Linux should ensure being able to follow this guide without issue.

**Base dependencies:**

1. An up-to-date version of [Docker](https://docs.docker.com/engine/install/#server) installed
2. [make](https://www.gnu.org/software/make/)
3. openssl
4. bash 5.x
5. wget

You might want to alias docker compose to something easier to type since it will be frequently used, for example:

`$ alias doc="docker compose"`

Add the alias command to your shell environment startup script (e.g., `.bashrc` or `.zshrc`) to ensure that it's always available in every CLI shell you open.

#### macOS specific install instructions

macOS comes with pretty ancient CLI tooling that won't cut it to build this application (bash 3.x etc... come on, mac!). In order to build and run comses.net from the command line we'll need to upgrade them. We've tested this using [macports](https://macports.org) and [homebrew](https://brew.sh/) and have developed a slight preference for homebrew but feel free to use either. You'll probably also need [XCode and the XCode Command Line Tools](https://developer.apple.com/downloads/).

1. Download and install [macports](https://www.macports.org/install.php) or download and install [homebrew](https://brew.sh) via 

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
(if you already these installed, make sure they're up-to-date e.g., `brew upgrade`)

2. Follow the macports [install XCode and the XCode Command Line Tools guide here](https://guide.macports.org/#installing.xcode)
3. *(Apple Silicon M* chips only)* set the `DOCKER_DEFAULT_PLATFORM` environment variable to `linux/amd64` e.g., 

```bash 
export DOCKER_DEFAULT_PLATFORM=linux/amd64
``` 

Again, to make sure this is always set in your environment place this export command in your shell startup script (e.g., `.bashrc` for bash, `.zshrc` for zsh etc). You can find out what shell you are running with the command `$ echo $0`

The rest of these instructions should be applicable to both Linux / macOS once you have the base dependencies installed.

### Set up a local development environment

To setup a local dev environment with anonymized user data and web content, follow these steps:

1. (**NOTE: LINUX ONLY**, still need to find equivalents for macOS) Add `vm.max_map_count=262144` to `/etc/sysctl.d/99-docker.conf` (create this file if it doesn't already exist via something like `% echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-docker.conf`) for elasticsearch and run `sysctl -p` to apply those changes
2. After cloning the comses/comses.net git repository run `$ make build` to build the Docker images and configure all necessary settings and configuration files. If you run into issues at this step you should make sure that a) you're running an up-to-date version of Docker and b) that the Docker daemon is running. Running a simple check like `docker version` and `docker compose version` on the command line should suffice. Contact us or [create an issue](https://github.com/comses/infra/issues/new) if you encounter problems and please include a detailed system report with your OS version, Docker version, and any error messages you encountered.
3. Edit `config.mk` in your root directory and set `BORG_REPO_URL=https://dev.commons.asu.edu/data/comses/minimal/repo.tar.xz`
4. Run `make restore` to download the sparse repo and load its data into your Docker containers. You may see an error `ERROR: database "comsesnet" already exists` but you should be able to safely ignore this. FIXME: clear this spurious warning from the build process
5. At this point all the containers should be up and running.
6. The following commands are all applicable _within_ the Django server container. Start an interactive bash shell within the container by running something like `$ docker compose exec server bash`
7. Run any Django migrations if needed via `./manage.py migrate`
8. Adjust Site settings and other wagtail / Django data for development use via `$ ./manage.py setup_staging`
9. Run Django's collect static and index database content into Elasticsearch via `$ inv prepare`

Congratulations! If you made it this far you *should* be able to access your local instance of comses.net at http://localhost:8000 - if not, it's probably our fault! Please reach out to the dev team on Slack to get assistance (and update these instructions).

> The minimal backup comes with two user accounts for testing purposes:
> - An admin user with all permissions: (username: `admin_user` password: `123456`)
> - A base user (created by the usual means) : (username: `test_user` password: `123456`)

When new changes come in from the upstream repository (comses/comses.net) run a `$ git pull` and `$ make deploy` from your host computer to retrieve and build the latest changes.

This is a hot-reloading server so any changes you make to the frontend or backend should automagically get deployed and made visible without doing anything. If you do run into problems though or need to rebuild your container images, the following commands are often helpful:

```bash
$ docker compose restart server # server|js|db|redis|elasticsearch or whatever service name in docker-compose.yml you want to restart
$ docker compose down # bring down all services to keep your system load clean
$ docker compose build --pull # rebuild container images (run docker compose up -d to recreate them afterwards)
$ docker compose exec server bash # enter the running server container (replace server with any service name defined in `docker-compose.yml`)
$ docker compose logs -f <service> # view (follow) log output for a specific service (server|js|db|redis|elasticsearch)
```

## Contributing back to the repository

Our standard workflow for developers is to have you fork the _upstream_ [comses.net repo](https://github.com/comses/comses.net) for your own development. Create your own fork [here](https://github.com/comses/comses.net/fork); if you need to include a branch from the upstream repository, uncheck the "Copy the main branch only" option.

1. Clone your fork onto your local machine via `% git clone https://github.com/your-username/comses.net`
2. Set up an upstream remote, e.g.,  `git remote add upstream https://github.com/comses/comses.net.git` (or `git@github.com` as the host if you are using ssh keys)
3. View your remote status: `git remote -v`
4. Update your origin to the location of your own fork if necessary: git remote set-url origin <your_fork_url> (eg, `git remote set-url origin https://github.com/monaw/comses.net.git`)
5. `git pull` to fetch OR git pull origin
6. If there is an existing branch with code you want to work with, you can switch to this branch with git checkout --track origin/<branch_name> (eg, git checkout --track origin/datacite_doi_registration); otherwise you can go ahead and create a branch for your work: git checkout -b <new_branch_name> (eg, git checkout -b mybranch)
7. Run `git status` regularly to verify you are on the right branch
8. After switching branches, refresh the server with make deploy or a combination of docker compose build --pull and docker-compose up -d which should keep your containers up to date with the current version of code
9. Keep your fork in sync with the upstream repository by following these steps: https://github.com/comses-education/github-starter-course/blob/main/README.md#keep-your-fork-synced-with-upstream

## Checkout another person's fork and switch to a branch on that fork

1. Add their fork as a remote to your repository: e.g., `git remote add al git@github.com:alee/comses.net`
2. Update your local repository with a fetch: `git fetch al`
3. Checkout the branch you're interested in: `git checkout --track al/<branch-name>`
4. Build the code and restart the containers: `docker compose build --pull && docker compose up -d`
5. Commit and push as needed, but don't rewrite history without all devs being aware + onboard with it
6. Switch back to your main branch (or any other) when you're done: e.g., `git switch <branch-name>`

Follow commit guidelines https://www.conventionalcommits.org/en/v1.0.0/ and broad guidance from https://cbea.ms/git-commit/

## Additional Environment Setup (editor, tooling, etc.)

> Note that much of this setup is optional and only serves to give a sensible dev environment. Configuration can be customized to suit one's preferred workflow.

### Visual Studio Code

[VSCode](https://code.visualstudio.com/) is recommended as a primary editor/IDE for this project due to native plugin support for Vue/Typescript and Python/Django as well as collaboration tools like Live Share. Optionally, something like [pycharm](https://www.jetbrains.com/pycharm/) can be used as a more full-fledged IDE for Django development if needed.

### Recommended VSCode Plugins

Vue/Typescript
- [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) - Vue language features
- [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) and [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) - code linting/formatting
- [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) - blame annotations and more for git
- [Live Share](https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare) - collaboration

Python/Django:
- [python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) - Python language server, debugging, etc.
- [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) - Python code formatting with [black](https://github.com/psf/black)
- [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) - Support for [jinja](https://palletsprojects.com/p/jinja/) templating

### VSCode Plugin Setup

The following VSCode settings will configure formatting on save for vue/js/ts with prettier and python with black.

`.vscode/settings.json` in the project root
```json
{
  "editor.formatOnSave": false,
  "editor.formatOnPaste": false,
  "prettier.configPath": "frontend/.prettierrc",
  "[typescript]": {
      "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
      "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[vue]": {
      "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[python]": {
      "editor.defaultFormatter": "ms-python.black-formatter",
      "editor.formatOnSave": true
  },
}
```

### Browser Plugins

- Vue Devtools for [chrome](https://chrome.google.com/webstore/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd?hl=en) or [firefox](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

### Git Blame Ignore Revisions

Being able to see git history is extremely useful in understanding a codebase or specific piece of code. This can be done on Github, with `git blame` or in your editor with something like Gitlens. Large changes that provide no context (formatting, for example) can be ignored with `git blame --ignore-rev`. In order to have Gitlens and `git blame` ignore these revisions by default add the `.git-blame-ignore-revs` file, which indexes commit hashes we want to ignore, to your git config with:
```bash
$ git config blame.ignoreRevsFile .git-blame-ignore-revs
```

## Resolving dependencies locally

Since comses.net uses docker to containerize the application, Python and JS dependencies will only exist inside the containers and you will encounter issues with unknown modules. 

VSCode has some support for developing within containers that you can customize so that library dependencies in your editor resolve properly. Install the `Dev Containers` extension and follow the steps here: https://code.visualstudio.com/docs/devcontainers/containers to attach to either the `server` or `js` (frontend) container depending on where you need to work.

Another way to get around this and have access to code completion is to mirror dependencies on the host/locally which we'll go over below:

#### Frontend dependencies

Install node with [Node Version Manager](https://github.com/nvm-sh/nvm) (recommended)

Follow the steps at https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script to install nvm despite the security cringe of a `curl ... | bash` script.

E.g.,

```bash
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
$ source ~/.bashrc # for bash shell, alternatively close and re-open the terminal
$ nvm install lts/gallium # install node 16 lts and npm
$ nvm use lts/gallium
# check to make sure everything worked
$ node --version # should be v16.x.x
$ npm --version
```

Install project dependencies
```bash
$ cd comses.net # make sure you are in the project root
# install packages from the lockfiles generated by the containers
$ cd frontend
$ npm ci
```
If you encounter a `permission denied` error, remove `node_modules/` and try again

#### Python dependencies

First, install [Python 3](https://www.python.org/downloads/). Then create a new [virtual environment](https://docs.python.org/3/library/venv.html) for comses.net and activate it.

Then install the project dependencies with `pip` from the project root:

```bash
$ pip3 install -r django/requirements-dev.txt
```

# Codebase Overview

## Frontend

Alongside django views using jinja2 templates which render the base of the site, Vue.js 3 is used for certain interactive pieces better suited to a modern frontend framework. Several 'mini' vue apps are defined in `frontend/src/apps/` which are comprised of one or more vue components and are mounted on existing pages. These range from simple UI elements like an image carousel to an entire multi-route app with a store and several forms. 

Components are built (or served) and mounted with the help of [vite](https://github.com/vitejs/vite) and [django-vite](https://github.com/MrBin99/django-vite).

The [vue 3 composition API](https://vuejs.org/api/composition-api-setup.html) is used to define components. For non-UI logic or shared code the `frontend/src/composables` directory holds [composable functions](https://vuejs.org/guide/reusability/composables.html), a significant portion of which is code that uses an [axios](https://axios-http.com/) client to interact with a REST api on the server (built with [Django REST Framework](https://www.django-rest-framework.org/))

## Frequently used Django Commands

The following should be run within the server container. Open an interactive shell on the server container with

`$ docker compose exec server bash`

- **check Django deployment tips**: `% ./manage.py check --deploy`
- **create an admin user for site/wagtail access**: `% ./manage.py createsuperuser` (additionally, you will need to verify the user's email, which can be done by attempting to log in and checking the server logs for the email containing the verification URL or setting it directly with `EmailAddress.objects.filter(email='fakeemail@example.com').update(verified=True)`)
- **start an interactive Django shell**: `% inv sh` or `% ./manage.py shell_plus`
- **create [Django database migrations](https://docs.djangoproject.com/en/4.1/topics/migrations/#module-django.db.migrations)**: `% ./manage.py makemigrations <django-app-label> -n <name-of-migration>`
- **create a [data migration](https://docs.djangoproject.com/en/4.1/topics/migrations/#data-migrations)**: `% ./manage.py makemigrations --empty <django-app-label> -n <name-of-data-migration>`
- **[run tests](https://docs.djangoproject.com/en/4.1/topics/testing/overview/#running-tests)**
- **[all django management commands](https://docs.djangoproject.com/en/4.1/ref/django-admin/#django-admin-and-manage-py)**
