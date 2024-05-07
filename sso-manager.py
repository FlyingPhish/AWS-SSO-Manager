import argparse
import configparser
import ast
import subprocess
import os

def prep_config(args):
    """Prepare the AWS CLI SSO configuration for multiple profiles."""
    config_file_path = os.path.expanduser('~/.aws/config')
    config = configparser.ConfigParser()
    config.read(config_file_path)

    print("Preparing AWS configuration...")
    for account_id in ast.literal_eval(args.ids):
        profile_name = f'profile aws_{account_id}'
        config[profile_name] = {
            'sso_start_url': args.url,
            'sso_region': args.sso_region,
            'sso_account_id': account_id,
            'sso_role_name': args.role,
            'output': 'json'
        }
        if args.region:
            config[profile_name]['region'] = args.region.strip()

    with open(config_file_path, 'w') as configfile:
        config.write(configfile)
    print("AWS configuration updated successfully for profiles:", ", ".join(ast.literal_eval(args.ids)))

def authenticate(args):
    """Authenticate all profiles using AWS SSO."""
    config_file_path = os.path.expanduser('~/.aws/config')
    config = configparser.ConfigParser()
    config.read(config_file_path)

    for section in config.sections():
        if section.startswith('profile aws_'):
            profile_name = section.split('profile ')[1]
            print(f"Authenticating {profile_name}...")
            result = subprocess.run(['aws', 'sso', 'login', '--profile', profile_name], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Failed to authenticate {profile_name}: {result.stderr}")
            else:
                identity_result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--profile', profile_name], capture_output=True, text=True)
                if identity_result.returncode == 0:
                    print(f"Successfully authenticated. AWS caller identity for {profile_name}: {identity_result.stdout}")
                else:
                    print(f"Failed to get caller identity for {profile_name}: {identity_result.stderr}")

def create_steampipe_connections(args):
    """Create and update Steampipe connections within the aws.spc file for each AWS profile."""
    config_file_path = os.path.expanduser('~/.aws/config')
    config = configparser.ConfigParser()
    config.read(config_file_path)

    steampipe_config_dir = os.path.expanduser('~/.steampipe/config')
    os.makedirs(steampipe_config_dir, exist_ok=True)
    aws_spc_file = os.path.join(steampipe_config_dir, 'aws.spc')

    connections_content = []
    connection_names = []
    for section in config.sections():
        if section.startswith('profile aws_'):
            profile_name = section.split('profile ')[1]
            connection_name = f'aws_{profile_name}'
            if 'region' in config[section]:
                regions = [config[section]['region']]
            else:
                regions = ['["*"]']
            connection_names.append(connection_name)
            connections_content.append(f"""
connection "{connection_name}" {{
    plugin = "aws"
    profile = "{profile_name}"
    regions = {regions[0]}
}}
""")

    with open(aws_spc_file, 'w') as f:
        f.writelines(connections_content)
        f.write(f"""
connection "aws" {{
    plugin = "aws"
    type = "aggregator"
    connections = [{', '.join([f'"{name}"' for name in connection_names])}]
}}
""")
    print("Steampipe aws.spc file updated with all profiles.")
    print("Steampipe aws.spc file updated with all profiles.")

def clear_config(args):
    """Clear the AWS configuration file."""
    config_file_path = os.path.expanduser('~/.aws/config')
    if os.path.exists(config_file_path):
        os.remove(config_file_path)
        print("AWS configuration cleared.")
    else:
        print("Configuration file not found.")

def clear_steampipe_config(args):
    """Clear the Steampipe AWS connection file."""
    steampipe_config_file = os.path.expanduser('~/.steampipe/config/aws.spc')
    if os.path.exists(steampipe_config_file):
        os.remove(steampipe_config_file)
        print("Steampipe AWS connection file cleared.")
    else:
        print("Steampipe AWS connection file not found.")

def main():
    parser = argparse.ArgumentParser(description="Manage AWS CLI SSO configuration.")
    subparsers = parser.add_subparsers(help='commands')

    # Prepare configuration command
    prep_parser = subparsers.add_parser('prep', help='Prepare AWS configuration')
    prep_parser.add_argument("-r", "--role", required=True, help="Role name to use with AWS SSO")
    prep_parser.add_argument("-i", "--ids", required=True, help="Formatted list of AWS account IDs")
    prep_parser.add_argument("-u", "--url", required=True, help="SSO start URL")
    prep_parser.add_argument("-sr", "--sso-region", required=True, help="SSO region for the AWS SSO configuration")
    prep_parser.add_argument("-re", "--region", help="AWS region for the profile")
    prep_parser.set_defaults(func=prep_config)

    # Authenticate command
    auth_parser = subparsers.add_parser('auth', help='Authenticate all profiles')
    auth_parser.set_defaults(func=authenticate)

    # Create Steampipe connections command
    steampipe_parser = subparsers.add_parser('steampipe', help='Create Steampipe connections')
    steampipe_parser.set_defaults(func=create_steampipe_connections)

    # Clear configuration command
    clear_parser = subparsers.add_parser('clear', help='Clear AWS configuration')
    clear_parser.set_defaults(func=clear_config)

    # Clear Steampipe configuration command
    steampipe_clear_parser = subparsers.add_parser('clear_steampipe', help='Clear Steampipe AWS connection file')
    steampipe_clear_parser.set_defaults(func=clear_steampipe_config)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()