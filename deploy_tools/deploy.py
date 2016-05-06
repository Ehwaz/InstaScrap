import os, json
from jinja2 import Environment, FileSystemLoader

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

def install_dependency():
    os.system("sudo apt-get install nginx=1.4.6-1ubuntu3.4 uwsgi=1.9.17.1-5build5")
    os.system("pip install -r pip_dependency/deploy_env_ubuntu.txt")

# Create django settings.py file from template and deploy info.
def create_django_settings_file(jinja_env, deploy_info):
    settings_template = jinja_env.get_template("settings_py.template")
    settings_file = open("../InstaScrap/settings.py", 'w')
    settings_file.write(settings_template.render(deploy_info))
    settings_file.close()

def create_deploy_config_files(jinja_env, deploy_info, template_dir, result_dir, filepath_dict):
    # Create result directories
    os.makedirs(result_dir + "init")
    os.makedirs(result_dir + "nginx/sites-available")
    os.makedirs(result_dir + "uwsgi/sites")
  
    # Combine config templates and deploy info.
    for key in filepath_dict.keys():
        conf_file_template = jinja_env.get_template(template_dir + filepath_dict[key])
        new_file = open(result_dir + filepath_dict[key], 'w')
        new_file.write(conf_file_template.render(deploy_info))
        new_file.close()

def create_envfile_symlinks(result_dir, filepath_dict):
    for key in filepath_dict.keys():
        whole_path = "/" + result_dir + filepath_dict[key]
        if key == "upstart-conf-uwsgi":
            # Upstart explicitly doesn't support symlink file.
            # http://serverfault.com/a/459699
            os.system("sudo cp " + CUR_DIR + whole_path + " " + whole_path)
        else:
            os.system("sudo ln -fs " + CUR_DIR + whole_path + " " + whole_path)
            if key == "nginx-site":
                # Make nginx provide project website.
                os.system("sudo ln -fs " + whole_path + " /etc/nginx/sites-enabled/InstaScrap")

def run_uwsgi_and_nginx():
    os.system("sudo service uwsgi start")
    os.system("sudo service nginx start")

if __name__ == '__main__':
    install_dependency()
    
    # Directory containing templates of config files.
    template_dir = "etc_template/"
    # Directory to contain the results of (template + config variable).
    #   Those files are symlinked or copied and used by uwsgi, nginx and upstart.
    result_dir = "etc/"

    filepath_dict = {
            "upstart-conf-uwsgi": "init/uwsgi.conf",
            "uwsgi-site": "uwsgi/sites/instascrap.ini",
            "nginx-site": "nginx/sites-available/InstaScrap",
            }

    # Open deploy info json file and load it as Python dictionary.
    with open("deploy_info.json") as deploy_info_file:
        deploy_info = json.load(deploy_info_file)

    # Using jinja2 template engine to combine config template file and deploy info.
    jinja_env = Environment(loader=FileSystemLoader(CUR_DIR))

    create_django_settings_file(jinja_env, deploy_info)
    create_deploy_config_files(jinja_env, deploy_info, template_dir, result_dir, filepath_dict)
    create_envfile_symlinks(result_dir, filepath_dict)
    run_uwsgi_and_nginx()
