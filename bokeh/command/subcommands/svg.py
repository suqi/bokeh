'''
To generate standalone SVGs for a Bokeh application from a single
Python script, pass the script name to ``bokeh svg`` on the command
line:

.. code-block:: sh

    bokeh svg app_script.py

The generated SVGs will be saved in the current working directory with
the name ``app_script.svg``. If there are multiple SVGs within an application,
the subsequent ones will be named ``app_script_1.svg``, ``app_script_2.svg``,
etc.

It is also possible to run the same commmand with jupyter notebooks:

.. code-block:: sh

    bokeh svg app_notebook.ipynb

This will generate SVG files named ``app_notebook_{n}.svg`` just like
with a python script.

Applications can also be created from directories. The directory should
contain a ``main.py`` (and any other helper modules that are required) as
well as any additional assets (e.g., theme files). Pass the directory name
to ``bokeh svg`` to generate the SVG:

.. code-block:: sh

    bokeh svg app_dir

It is possible to generate SVG files for multiple applications at once:

.. code-block:: sh

    bokeh svg app_script.py app_dir

.. warning::
    Applications that use ``on_change`` callbacks require using the Bokeh
    server to execute the callback code. Though the application may render,
    the callbacks will not function. See :ref:`userguide_cli_serve` for
    more information on using ``bokeh serve``.

For all cases, it's required to explicitly add a Bokeh layout to
``bokeh.io.curdoc`` for it to appear in the output.

'''
from __future__ import absolute_import

import io
import os
import warnings

from bokeh.io import _get_svgs
from bokeh.models import Plot
from bokeh.util.string import decode_utf8
from .file_output import FileOutputSubcommand

class SVG(FileOutputSubcommand):
    ''' Subcommand to output applications as standalone PNG files.

    '''

    name = "svg"

    extension = "svg"

    help = "Create standalone SVG files for one or more applications"

    args = (

        FileOutputSubcommand.files_arg("SVG"),

        ('--height', dict(
            metavar='HEIGHT',
            type=int,
            help="The desired height of the exported layout obj only if it's a Plot instance",
            default=None,
        )),

        ('--width', dict(
            metavar='WIDTH',
            type=int,
            help="The desired width of the exported layout obj only if it's a Plot instance",
            default=None,
        )),

    ) + FileOutputSubcommand.other_args()

    def invoke(self, args):
        import selenium.webdriver as webdriver
        self.driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
        super(SVG, self).invoke(args)
        self.driver.quit()

    def write_file(self, args, filename, doc):
        contents = self.file_contents(args, doc)
        for i, svg in enumerate(contents):
            if filename == '-':
                print(decode_utf8(svg))
            else:
                if i == 0:
                    filename = filename
                else:
                    idx = filename.find(".svg")
                    filename = filename[:idx] + "_{}".format(i) + filename[idx:]
                with io.open(filename, "w", encoding="utf-8") as f:
                    f.write(decode_utf8(svg))
            self.after_write_file(args, filename, doc)

    def file_contents(self, args, doc):
        if args.width is not None or args.height is not None:
            layout = doc.roots
            if len(layout) != 1 or not isinstance(layout[0], Plot):
                warnings.warn("Export called with height or width kwargs on a non-single Plot layout. The size values will be ignored.")
            else:
                plot = layout[0]
                plot.plot_height = args.height or plot.plot_height
                plot.plot_width  = args.width or plot.plot_width
        return _get_svgs(doc, driver=self.driver)
