import os
import sys
import subprocess

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_path = os.path.join(repo_root, 'backend')
    sys.path.insert(0, backend_path)
    env = os.environ.copy()
    env['PYTHONPATH'] = backend_path + os.pathsep + env.get('PYTHONPATH', '')

    args = ['python', '-m', 'pytest', 'scripts/tests', '-v']
    print('Running tests with PYTHONPATH=', env['PYTHONPATH'])
    result = subprocess.run(args, env=env)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()

