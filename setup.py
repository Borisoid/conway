import sys
import subprocess


SS = 'setup_scripts'


def main(implementation=None):

    if implementation == 'cy':
        cmd = ["python", f"{SS}/cy_setup.py", "build_ext", "--build-lib", "cython_target"]
    elif implementation == 'cy_opt':
        cmd = ["python", f"{SS}/cy_opt_setup.py", "build_ext", "--build-lib", "cython_target"]
    elif implementation == 'cy_opt_old':
        cmd = ["python", f"{SS}/cy_opt_old_setup.py", "build_ext", "--build-lib", "cython_target"]
    elif implementation == 'pybind11_opt':
        cmd = ["python", f"{SS}/pybind11_opt_setup.py", "build_ext", "--build-lib", "pybind11_target"]
    else:
        print('Unknown implementation: ', implementation)
        exit(0)

    subprocess.run(cmd)


if __name__ == '__main__':
    main(sys.argv[1])
