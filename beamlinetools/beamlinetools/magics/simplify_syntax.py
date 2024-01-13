import ast
import os
import re
import ast
import os
from IPython import get_ipython

# from beamlinetools.BEAMLINE_CONFIG.base import *
# from beamlinetools.BEAMLINE_CONFIG.beamline import *
# from beamlinetools.BEAMLINE_CONFIG.plans import *
# from beamlinetools.BEAMLINE_CONFIG.tools import *


class Simplify():
    """This class is used to simplify the Bluesky syntax

    The class automatically generates magics from all the imports in a certain file.
    I tested it by autogenerating magics from all the files present in the startup
    file plans.py. It can be used on any file, it will autogenerate magics from all 
    the objects imported in the file.

    The class also automatically check that no pre-existent magic is overwritten

    Example: if dscan is defined, the normal syntax is
    RE(dscan([det1], motor1, -1, 1, 10))
    and now one can use
    %dscan [det1] motor1 -1 1 10
    or grouping some detectors is list would also work
    detectors=[det1,det2]
    %dscan detectors motor1 -1 1 10

    Example Usage: in a ipython startup file:
    
    from beamlinetools.magics.simplify_syntax import Simplify
    from IPython import get_ipython
    simplify = Simplify(get_ipython())
    simplify.autogenerate_magics( <'path_to_file'>)

    Args:
            shell (): IPython.get_ipython()

    
    """    
    def __init__(self, shell):      
        self.shell = shell
        self.magics = []
        self.path_to_file = None
    
    def make_command(self,line):
        """this method takes a string and write it using correct bluesky syntax

        example:
        dscan [det1] motor1 -1 1 10
        becomes 
        dscan([det1], motor1, -1, 1, 10)

        Additionally it automatically takes care of the case
        where the user has defined a list with detectors

        Args:
            line (str): this is the ipython line for which an autogenerated
                        magic exists

        Returns:
            str: a string representing a correct bluesky command
        """        
        # check if there are too many spaces and remove them
        count = 1
        while count > 0: 
            line, count = re.subn('  ', ' ', line)
        if " [" in line:
            line = re.sub(' \[', '([', line)
            line = re.sub(' ', ',', line)
        else:
            line = line.replace(" ", "(", 1)
            line = line.replace(" ", ",")
        line +=')'
        return line
    

    def get_defined_magics(self):
        """Get a list of magics already present in the ipython environment

        Returns:
            list: list of strings, names of the magics found
        """        
        ipython = get_ipython()
        magics = []
        for name, func in ipython.magics_manager.magics['line'].items():
            magics.append(name)
        return magics

    def get_imported_objects(self):
        """This method returns a list of the objects imported in the file self.path_to_file

        Returns:
            list: the imports found the in the file
        """        
        imported_objects = []
        
        # Parse the AST of the file
        with open(self.path_to_file, 'r') as file:
            tree = ast.parse(file.read())
        
        # Traverse the AST nodes
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                # Iterate over the imported names
                for alias in node.names:
                    if alias.asname:
                        imported_objects.append(alias.asname)
                    else:
                        imported_objects.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                # Check if the import statement is not a relative import
                if node.module:
                    # Iterate over the imported names
                    for alias in node.names:
                        if alias.asname:
                            imported_objects.append(alias.asname)
                        else:
                            imported_objects.append(alias.name)
        return imported_objects

    def generate_magics(self):
        """Generates magics

        The method uses the self.get_imported_objects method to get a list of 
        magics to implement, all the imports in self.file_path. It excludes the 
        objects starting with "_"

        Returns:
            _type_: _description_
        """        
        imported_objects = self.get_imported_objects()
        strings = [obj for obj in imported_objects if not obj.startswith('_')]
        defined_magics = self.get_defined_magics()
        for string in strings:
            if string not in defined_magics:
                def magic_func(line, magic_name=string):
                    line = magic_name + ' ' + line
                    command = self.make_command(line)
                    # the command is now eavaluated in the 
                    # ipython user namespace
                    ipython_ns = get_ipython().user_ns
                    return RE(eval(command, ipython_ns))
                self.magics.append((string, magic_func))
    
    def load_magics(self):
        """This method register the magics in the ipython session of the user, self.shell
        """        
        for name, magic_func in self.magics:
            self.shell.register_magic_function(magic_func, magic_kind='line', magic_name=name)
    def autogenerate_magics(self, path_to_file):
        """This method autogenerates the magics and register them by cin the current Ipython session

        Args:
            path_to_file (str): path to the file from which magics will be generated
        """        
       
        self.path_to_file = path_to_file
        self.generate_magics()
        self.load_magics()

    def execute_magic(self, magic_string):
        if magic_string.startswith('%'):
            magic_string=magic_string[1:]  # Remove the first character
        cmd_string = self.make_command(magic_string)
        if magic_string.startswith('mov'):
            cmd_string = cmd_string.replace("mov", "mv")
            print(f"Moving: {cmd_string}")
            return RE(eval(cmd_string, self.shell.user_ns))
        else:
            return RE(eval(cmd_string, self.shell.user_ns))



