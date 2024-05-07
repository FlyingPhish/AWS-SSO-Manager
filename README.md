# AWS SSO Manager

AWS SSO Manager is a Python-based command-line tool that simplifies the management of AWS CLI SSO configurations and Steampipe connections. It allows you to easily set up and manage multiple AWS profiles, authenticate them using AWS SSO, and create corresponding Steampipe connections for seamless integration with Steampipe.

## Features

- Prepare AWS CLI SSO configuration for multiple profiles
- Authenticate all profiles using AWS SSO
- Create and update Steampipe connections for each AWS profile
- Clear AWS configuration and Steampipe connection files

## Prerequisites

- Python 3.x
- AWS CLI
- Steampipe

## Installation

1. Clone the repository:
    ``` git clone https://github.com/FlyingPhish/AWS-SSO-Manager && cd AWS-SSO-Manager```
2. Add this alias to bash or zrc: ```alias format-aws-ids="grep -o '[0-9]\{12\}' | sort | uniq | awk 'BEGIN { ORS=\"\"; print \"[\" } { print \"\\\"\" \$0 \"\\\", \" } END { print \"]\" }' | sed 's/, ]/]/'"```

## Usage

```
usage: sso-manager.py [-h] {prep,auth,steampipe,clear,clear_steampipe} ...

Manage AWS CLI SSO configuration.

positional arguments:
  {prep,auth,steampipe,clear,clear_steampipe}
                        commands
    prep                Prepare AWS configuration
    auth                Authenticate all profiles
    steampipe           Create Steampipe connections
    clear               Clear AWS configuration
    clear_steampipe     Clear Steampipe AWS connection file

options:
  -h, --help            show this help message and exit
```
### Prepare AWS Configuration
1. Browse to the AWS access portal
2. Select table contents and copy
3. Either paste the content into a file (cat > file.txt; cat file.txt | format-aws-ids) or paste your clipboard and pipe into the alias (pbpaste | format-aws-ids)
4. Copy formatted list of accounts IDs ["x","x","x"]
5. Run this command ```python3 sso-manager.py prep -r SecurityAudit (roleName) -sr eu-west-2 (sso login region) -u https://x.awsapps.com/start/# (sso url) -i '["x", "x", "x"] (formatted list of IDs)'```

### Authenticate Profiles
1. ```python3 sso-manager.py auth```
2. This will open the link in your browser and wait for you to click through the approval pages. This will repeat for every account and then will run get-caller-identity in CLI to show you the details.

### Steampipe Configuration
1. ```python3 sso-manager.py steampipe```
2. This will copy the profiles from aws/config, then create a connection for each, then will either create or modify the default aws connection to include all the new connections so you can run steampipe against all profiles.
3. You can modify the command to run ```python3 sso-manager.py steampipe -re (--regions) "eu-west-1,eu-west-2"``` to limit the scope to the set regions as the default value will use all regions.

### Clear Configurations
#### AWS Config
1. ```python3 sso-manager.py clear```
#### Steampipe
1. ```python3 sso-manager.py clear_steampipe```