import component_specs.component_spec_pb2 as pb
from component_specs.format_types import format_xtype_for_proto
from component_specs.utils import (
  capitalize_first_letter,
  upper_camel_case,
)


def generate_ng_ts(spec: pb.ComponentSpec) -> str:
  """
  Read from component_name.ts
  Do simple string replacements
  Build event handlers
  """

  # TODO: should use runfiles
  with open(
    "/Users/will/Documents/GitHub/mesop/component_specs/fixtures/component_name.ts",
  ) as f:
    ts_template = f.read()

  # default_value_prop = [
  #   prop for prop in spec.input_props if prop.name == "value"
  # ][0]
  symbols = ",".join(
    [spec.input.ng_module.module_name]
    + list(spec.input.ng_module.other_symbols)
  )
  symbols = "{" + symbols + "}"

  ts_template = (
    f"import {symbols} from '{spec.input.ng_module.import_path}'\n"
    + ts_template
  )
  # Do simple string replacements
  ts_template = (
    ts_template.replace("component_name", spec.input.name)
    .replace("ComponentName", upper_camel_case(spec.input.name))
    # .replace(
    #   "value!: any;",
    #   f"value!: {format_type_ts(default_value_prop.type)};",
    # )
    .replace("// INSERT_EVENT_METHODS:", generate_ts_methods(spec))
    .replace("// GENERATE_NG_IMPORTS:", generate_ng_imports(spec))
  )

  return ts_template


def generate_ng_imports(spec: pb.ComponentSpec) -> str:
  return f"imports: [{spec.input.ng_module.module_name}]"


def generate_ts_methods(spec: pb.ComponentSpec) -> str:
  out = ""
  for input_prop in spec.input_props:
    out += generate_ts_getter_method(input_prop)
  for prop in spec.output_props:
    out += generate_ts_event_method(prop)
  return out


def generate_ts_getter_method(prop: pb.Prop) -> str:
  string_literals = list(prop.type.string_literals.string_literal)
  type = "|".join(["'" + literal + "'" for literal in string_literals])
  capitalized_name = capitalize_first_letter(prop.name)
  if string_literals:
    return f"""
    get{capitalized_name}(): {type} {{
      return this.config().get{capitalized_name}() as {type};
    }}
    """
  return ""


def generate_ts_event_method(prop: pb.OutputProp) -> str:
  arg = (
    "event"
    if prop.event_js_type.is_primitive
    else f"event.{prop.event_props[0].name}"
  )
  return f"""
  on{prop.event_name}(event: {prop.event_js_type.type_name}): void {{
    const userEvent = new UserEvent();
    userEvent.set{format_xtype_for_proto(prop.event_props[0].type).capitalize()}({arg})
    userEvent.setHandlerId(this.config().getOn{prop.event_name}HandlerId())
    userEvent.setKey(this.key);
    this.channel.dispatch(userEvent);
  }}
  """
