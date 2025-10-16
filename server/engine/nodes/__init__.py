"""Package initializer for server.engine.nodes.

This file performs safe, explicit imports of known node submodules so that
module-level registration (via decorators like ``@register_node``) runs when
the package is imported. Imports are wrapped in try/except to avoid breaking
package import if an optional dependency is missing; failures are printed to
stderr so they are visible during startup.
"""

from __future__ import annotations

import importlib
import sys

# List of submodules (relative to this package) that define node classes.
# Keep this explicit so the import order is predictable and easy to control.
_SUBMODULES = [
	"BaseNode",
	"DataType",
	"Exceptions",
	"Utils",
	"Utility.Utility",

	# generators
	"Generate.Const",
	"Generate.String",
	"Generate.Table",

	# compute
	"Compute.Prim",
	"Compute.String",
	"Compute.Table",

	# visualization
	"Visualize.Plot",
	"Visualize.WordCloud",

	# table processors
	"TableProcess.ColProcess",
	"TableProcess.RowProcess",
]

for mod in _SUBMODULES:
	name = f"{__name__}.{mod}"
	try:
		importlib.import_module(name)
	except Exception as e:
		# don't raise to keep package import resilient; print warning to stderr
		print(f"Warning: failed to import node module {name}: {e}", file=sys.stderr)
