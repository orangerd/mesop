from typing import Sequence

from absl import app, flags

import mesop.protos.ui_pb2 as pb
from mesop.cli.execute_module import (
  clear_app_modules,
  execute_module,
  get_module_name_from_runfile_path,
)
from mesop.exceptions import format_traceback
from mesop.runtime import enable_debug_mode, runtime
from mesop.server import dev_server
from mesop.server.flags import port
from mesop.server.server import configure_flask_app
from mesop.utils.runfiles import get_runfile_location

FLAGS = flags.FLAGS

flags.DEFINE_string("path", "", "path to main python module of Mesop app.")


def main(argv: Sequence[str]):
  flask_app = configure_flask_app(prod_mode=False)
  if len(FLAGS.path) < 1:
    raise Exception("Required flag 'path'. Received: " + FLAGS.path)

  enable_debug_mode()

  try:
    module_name = get_module_name_from_runfile_path(FLAGS.path)
    clear_app_modules(module_name=module_name)
    execute_module(
      module_path=get_runfile_location(FLAGS.path),
      module_name=module_name,
    )
  except Exception as e:
    runtime().add_loading_error(
      pb.ServerError(exception=str(e), traceback=format_traceback())
    )
    print("Exception executing module:", e)

  print("Starting dev server...")
  dev_server.configure_dev_server(flask_app)
  flask_app.debug = True
  flask_app.run(host="::", port=port(), use_reloader=False)


if __name__ == "__main__":
  app.run(main)
