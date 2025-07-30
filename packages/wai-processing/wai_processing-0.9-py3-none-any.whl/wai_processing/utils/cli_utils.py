import argparse
import inspect
from collections.abc import Callable
from dataclasses import dataclass, fields, MISSING as dataclass_field_missing
from typing import get_args, get_origin


@dataclass
class RerunArgs:
    rr_session_name: str = "WAI generic rerun session"
    rr_address: str = "0.0.0.0:9081"
    rr_local_developement: bool = False


# TODO (duncanzauss): It would be very useful to have similar functionality that handles
# a yaml to enable convenient yaml overrides from cli


# convenience function to create a CLI from a dataclass
def dataclass_to_argparse(conf_dataclass):
    """
    Generate an argparse parser from a dataclass.
    Can handle bool, str, int, float as well as tuples and list of the aforementioned types.
    Args:
        conf_dataclass: The dataclass to generate the parser from.
    Returns:
        conf: An instance of the dataclass with the values from the parser.
    """
    parser = argparse.ArgumentParser()

    # TODO (duncanzauss): Add support for help section in the parser
    # TODO (duncanzauss): Add support for optional dataclass args
    # TODO (duncanzauss): Add support for subcommands and a logic to generate a help
    # section and support a wider variety of types (e.g. dicts, enums etc.)

    # Iterate over the fields of the dataclass to build the parser
    for field in fields(conf_dataclass):
        # The dataclass field is a default_factory or Callable --> only accept tuple
        # or list of str, int, float, bool and use nargs to allow multiple arguments
        if isinstance(field.default_factory, Callable):
            # Inspect the function signature of the default factory
            signature = inspect.signature(field.default_factory)
            if len(signature.parameters) != 0:
                raise ValueError(
                    f"Default factory {field.default_factory.__name__} must not accept "
                    "any arguments"
                )
            # Use get_origin to get list[str] --> list
            if get_origin(field.type) in [list, tuple]:
                if get_args(field.type)[0] not in [str, int, float, bool]:
                    raise ValueError(
                        f"Unsupported type {field.type} for automatic parser creation "
                        "based on a dataclass"
                    )
                parser.add_argument(
                    f"--{field.name}", nargs="+", default=field.default_factory()
                )
            else:
                raise ValueError(f"Unsupported type {field.type} for default factory")

        elif field.default is not dataclass_field_missing:
            if field.type is bool:
                # For bools a dataclass field like this
                #   this_is_boolean_flag: bool = True
                # will result in a cli arg like this "--set_to_false_this_is_boolean_flag"
                # which will call the store_false action if the cli arg is set
                parser.add_argument(
                    f"--set_to_false_{field.name}"
                    if field.default
                    else f"--set_to_true_{field.name}",
                    default=field.default,
                    action="store_false" if field.default else "store_true",
                )
            else:
                parser.add_argument(
                    f"--{field.name}",
                    # pyre-ignore
                    type=type(field.default),
                    default=field.default,
                )

        elif field.type in [int, float, str]:
            parser.add_argument(f"--{field.name}", type=field.type, required=True)
        elif field.type is bool:
            raise RuntimeError("bools are only support with a default value.")
        else:
            RuntimeError(
                f"Unsupported type {field.type} for automatic parser creation based on "
                "a dataclass"
            )

    args = parser.parse_args()
    args_dict_cleaned = {
        key.removeprefix("set_to_true_").removeprefix("set_to_false_"): value
        for key, value in vars(args).items()
    }
    conf = conf_dataclass(**args_dict_cleaned)
    return conf
