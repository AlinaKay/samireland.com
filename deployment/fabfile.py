from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
from config import db, user, password, host
import random

REPO_URL = "https://github.com/samirelanduk/samireland.com.git"


def deploy():
    site_folder = "/home/%s/sites/%s" % (env.user, env.host)
    source_folder = site_folder + "/source"
    base_path = source_folder + "/samireland/templates/base.html"
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _add_google_analytics(env.host, )
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)


def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ["static", "source", "virtualenv"]:
        run("mkdir -p %s/%s" % (site_folder, subfolder))


def _get_latest_source(source_folder):
    if exists(source_folder + "/.git"):
        run("cd %s && git fetch" % source_folder)
    else:
        run("git clone %s %s" % (REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run("cd %s && git reset --hard %s" % (source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + "/samireland/settings.py"
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(
     settings_path,
     'ALLOWED_HOSTS =.+$',
     'ALLOWED_HOSTS = ["%s"]' % site_name
    )
    sed(
     settings_path,
     '"default": \{.+\}$',
     '"default": \{"ENGINE": "django.db.backends.postgresql_psycopg2", "NAME": \
     "%s", "USER": "%s", "PASSWORD": "%s", "HOST": "%s"\}' % (
      db, user, password, host
     )
    )
    sed(
     settings_path,
     '"media", "images"',
     '"../../samireland-media"'
    )
    append(
     settings_path,
     'STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../static"))'
    )
    secret_settigs_file = source_folder + "/samireland/secret_settings.py"
    if not exists(secret_settigs_file):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_settigs_file, "SECRET_KEY = '%s'" % key)


def _add_google_analytics(host, base_path):
    if host == "samireland.com":
        with open("analytics.html") as f:
            sed(
             base_path,
             "<!--google-analytics-->",
             f.read()
            )

def _update_virtualenv(source_folder):
    virtualenv_folder = source_folder + "/../virtualenv"
    if not exists(virtualenv_folder + "/bin/pip"):
        run("virtualenv --python=python3 %s" % virtualenv_folder)
    run("%s/bin/pip install -r %s/requirements.txt" % (
     virtualenv_folder, source_folder
    ))


def _update_static_files(source_folder):
    run("cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput" %
     source_folder
    )


def _update_database(source_folder):
    run("cd %s && ../virtualenv/bin/python3 manage.py migrate --noinput" %
     source_folder
    )
