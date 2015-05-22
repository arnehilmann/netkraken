from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.frosted")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "netkraken"
default_task = "publish"


@init
def set_properties(project):
    project.build_depends_on("mock")

    project.set_property("flake8_verbose_output", True)
    project.set_property("flake8_break_build", True)
