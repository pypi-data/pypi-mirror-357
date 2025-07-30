import argparse
import json
import logging
import os
import sys
from functools import partial

from r7_surcom_api.functions import PythonFunction
from r7_surcom_api.manifest import Manifest
from r7_surcom_api import constants, helpers, utils

# Try get the log level from env variable, default to INFO
log_level = os.getenv(constants.ENV_LOG_LEVEL, "INFO").upper()

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=getattr(logging, log_level))
LOG = logging.getLogger(constants.LOGGER_NAME)


def _invoke(userfunc, loop: bool = False, **kwargs):
    """
    Invoke the connector's function, optionally in a loop, and yield each page of result.
    """
    # TODO: add test
    # If we were passed a 'loop' flag, call repeatedly
    if loop:
        # Call until no more data.  (The function must take 'more_data' to enable looping).
        more_flag = True
        while more_flag:
            # Get results
            results = userfunc(**kwargs)
            more_data = results.get("more_data")
            more_flag = results.get("more_flag")
            # Yield the results
            yield results
            # Pass 'more_data' to the next iteration
            kwargs["more_data"] = more_data
    else:
        # Yield the results
        yield userfunc(**kwargs)


def _write_output_files(items: dict, outdir: str):
    """
    Write 'items' to 'outdir', in files named for each type in the items
    """
    # TODO: add test
    # Check that we can write the output directory (will raise if there's a file not a directory)
    os.makedirs(outdir, exist_ok=True)

    # Scan all the items for type names, then we'll write a file for each type
    typenames = set(map(lambda item: item["type"], items))

    for typename in sorted(typenames):
        # Unload each type to file(s)
        def _this_type(typeid, item):
            return item["type"] == typeid

        page = 0
        for group in helpers.grouper(
            filter(partial(_this_type, typename), items),
            blocksize=constants.UNLOAD_ITEMS_PER_FILE,
        ):
            if page == 0:
                filename = f"{typename}.json"
            else:
                filename = f"{typename}.{page:04}.json"
            page = page + 1

            LOG.info("Writing '%s'", filename)

            # Write in 'sample-data format' (not wrapped in items[]/type+content)
            dump = [item["content"] for item in list(filter(None, group))]

            with open(os.path.join(outdir, filename), "w", encoding="utf-8") as handle:
                json.dump(dump, handle, indent=2)


def surcom_function_cli(
    path_functions_module: str = None
):
    """
    To use: create a file __main__.py in your package, with:
    ```
        from r7_surcom_api import surcom_function_cli
        if __name__ == "__main__":
            surcom_function_cli()
    ```
    """
    if not path_functions_module:
        path_functions_module = os.path.dirname(sys.modules["__main__"].__file__)

    path_connector = os.path.dirname(path_functions_module)
    manifest_yaml = Manifest(path_connector)

    fns = {}

    for f in manifest_yaml.functions():
        fn = PythonFunction(f, path_functions_module)
        fns.update({fn.id_wo_ns: fn})

    parser = argparse.ArgumentParser(
        description=f"Run a specified function in {manifest_yaml.name}"
    )

    parser.add_argument(
        "fn",
        type=str,
        help="The name of the function to execute",
        choices=[fn.id_wo_ns for _, fn in fns.items()]
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--results-dir",
        type=str,
        default="/app/output",
        help="Directory to write the contents of the types to"
    )

    parser.add_argument(
        "--num-pages",
        type=int,
        default=constants.NUM_PAGES_DEFAULT,
        help="The max number of pages to get. Specify 0 to get all pages. Defaults to 0"
    )

    parser.add_argument(
        "--more-data",
        type=str,
        help="JSON string of more data to get"
    )

    for s in manifest_yaml.settings():
        s_flag = s.get("name")
        s_type = constants.PARAM_TYPE_MAP.get(s.get("type"))
        s_help = s.get("description") or s.get("title")
        s_default = os.getenv(f"{constants.SETTING_ENV_VAR_PREFIX}_{s_flag.upper()}", s.get("default"))
        s_choices = s.get("enum")

        # NOTE: If the type is a bool, we treat as a sting and
        # convert it to a boolean later on
        if s_type is bool:
            s_type = str

        parser.add_argument(
            f"--{s_flag}",
            type=s_type,
            help=s_help,
            default=s_default,
            choices=s_choices
        )

    args = parser.parse_args()

    if args.verbose:
        LOG.setLevel(logging.DEBUG)

    more_data = json.loads(args.more_data) if args.more_data else {}

    settings_dict = {}

    for s in manifest_yaml.settings():
        arg_value = getattr(args, s.get("name"))

        if s.get("type") == "boolean":
            # Convert boolean strings to actual booleans
            arg_value = utils.str_to_bool(arg_value, default=s.get("default"))

        settings_dict[s.get("name")] = arg_value

    for s_name, s in settings_dict.items():

        manifest_setting = manifest_yaml.get_setting(s_name)

        if settings_dict.get(s_name) is None and manifest_setting.get("nullable") is False:
            raise ValueError(f"Setting '{s_name}' is required but not provided")

    fn: PythonFunction = fns.get(args.fn)

    collected_items = []

    kwargs = {
        "__user_log": LOG
    }

    if settings_dict:
        kwargs.update(settings_dict)

    if fn.returns_items:
        kwargs["more_data"] = more_data

    i = 1

    for page in _invoke(fn.userfunc, loop=True, **kwargs):

        if fn.returns_items and isinstance(page, dict) and "items" in page:
            collected_items.extend(page["items"])

        if args.num_pages and i >= args.num_pages:
            # Stop after the specified number of pages
            break

        i += 1

    if collected_items:
        # Write the output to files in the output directory
        _write_output_files(collected_items, outdir=args.results_dir)
