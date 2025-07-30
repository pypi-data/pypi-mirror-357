from typing import Any, Hashable

from xarray import DataArray, DataTree

from sentineltoolbox.datatree_utils import visit_datatree
from sentineltoolbox.typedefs import DataTreeVisitor

"""
Provide generic filters for reference and converted products.
These filter add or remove attributes to improve compare_datatree outputs.
For example, converted products are sometimes improved and have more information than reference products.
We do not want to display this information as an issue.

Other improvments:
  - alert if long_name is not present in converted product
  - remove _ARRAY_DIMENSIONS attribute from reference product
  - remove all _eopf_attrs attributes from reference product. It is not our responsability to check these attributes.
"""


class ReferenceFilterGeneric(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        # datarray /conditions/sid-216/packet_data_length
        # {'_eopf_attrs': {
        #   'coordinates': ['sensing_time'],
        #   'dimensions': ['packet_number']
        # }}
        changed = False

        other_attrs = self.other[path].attrs
        # if long_name is neither in reference nor in converted, we need to inform user it could be nice to add it.
        # create a fake long_name in reference product
        if isinstance(node, DataArray) and "long_name" not in other_attrs and "long_name" not in obj:
            obj["long_name"] = "TODO"
            changed = True

        try:
            del obj["_eopf_attrs"]["_ARRAY_DIMENSIONS"]
        except KeyError:
            pass
        else:
            changed = True

        if changed:
            return obj
        else:
            return None


class ConvertedFilterGeneric(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        changed = False
        other_attrs = self.other[path].attrs
        # if long_name is present in converted product and is not in reference product,
        # that means that converter has improved product so we do not want to diplay it as an issue
        # delete it from converted product
        if "long_name" not in other_attrs and "long_name" in obj:
            del obj["long_name"]
            changed = True

        for attr_name in ("long_name", "short_name"):
            try:
                del obj["_eopf_attrs"][attr_name]
            except KeyError:
                pass
            else:
                changed = True
        if changed:
            return obj
        else:
            return None


class ReferenceFilterS01GPSRAW(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other

    def visit_node(self, root: DataTree, path: str, obj: DataTree) -> None:
        """
        Fix isp shape to fit real data. Fix encoding information chunks and preferred_chunks
        """
        if path.startswith("/measurements/sid-"):
            current = self.other[path]
            packet_length = current.dims["packet_length"]  # type: ignore
            subset = obj.isel(packet_length=slice(0, packet_length)).chunk({"packet_length": packet_length})
            for var_path, var_ref in subset.data_vars.items():
                var_conv = current[var_path]
                var_ref.encoding["chunks"] = var_conv.encoding["chunks"]
                var_ref.encoding["preferred_chunks"] = var_conv.encoding["preferred_chunks"]
            root[path] = subset


class ConvertedFilterS01GPSRAW(DataTreeVisitor):
    def __init__(self, other: DataTree):
        self.other = other

    def visit_attrs(
        self,
        root: DataTree,
        path: str,
        obj: dict[Hashable, Any],
        node: Any = None,
    ) -> None | dict[Hashable, Any]:
        changed = False

        # obj.setdefault("_eopf_attrs", {})["_ARRAY_DIMENSIONS"] = ["C"]
        if "_eopf_attrs" in obj:
            for attr_id in ("long_name", "short_name"):
                try:
                    del obj["_eopf_attrs"][attr_id]
                except KeyError:
                    pass
                else:
                    changed = True
        if changed:
            return obj
        else:
            return None


DEFAULT_VALIDATION_VISITORS = {
    "S01GPSRAW": (
        [ReferenceFilterGeneric, ReferenceFilterS01GPSRAW],
        [ConvertedFilterGeneric, ConvertedFilterS01GPSRAW],
    ),
}


def apply_validation_visitors(ptype: str, xdt_ref: DataTree, xdt_conv: DataTree) -> tuple[DataTree, DataTree]:

    ref_visitors, conv_visitors = DEFAULT_VALIDATION_VISITORS.get(
        ptype,
        ([ReferenceFilterGeneric], [ConvertedFilterGeneric]),
    )

    for ref_visitor in ref_visitors:
        xdt_ref = visit_datatree(xdt_ref, ref_visitor(other=xdt_conv))

    for conv_visitor in conv_visitors:
        xdt_conv = visit_datatree(xdt_conv, conv_visitor(other=xdt_ref))

    return xdt_ref, xdt_conv
