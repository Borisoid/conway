import sys


def main(implementation=None):

    if implementation == 'py':
        from python_source.py.py_cellular import main as _main
    elif implementation == 'py_opt':
        from python_source.py.py_opt_cellular import main as _main
    elif implementation == 'cy':
        from python_source.cy.cy_py_cellular import main as _main
    elif implementation == 'cy_opt':
        from python_source.cy.cy_py_opt_cellular import main as _main
    elif implementation == 'cy_opt_old':
        from python_source.cy.cy_py_opt_old_cellular import main as _main
    elif implementation == 'cppyy_opt':
        from python_source.cppyy.cppyy_opt_cellular import main as _main
    elif implementation == 'pybind11_opt':
        from python_source.pybind11.pybind11_opt_cellular import main as _main
    else:
        print('Unknown implementation: ', implementation)
        exit(0)

    _main()


if __name__ == '__main__':
    main(sys.argv[1])
