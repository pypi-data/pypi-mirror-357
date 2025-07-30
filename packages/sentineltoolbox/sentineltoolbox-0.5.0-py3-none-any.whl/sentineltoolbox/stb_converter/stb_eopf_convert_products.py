from pathlib import Path
from typing import Any

import click
from eopf import EOSafeStore, EOZarrStore, OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.store.mapping_factory import EOPFMappingFactory
from eopf.store.mapping_manager import EOPFMappingManager
from xarray import DataTree

from sentineltoolbox.attributes import guess_product_type
from sentineltoolbox.readers.open_datatree import open_datatree
from sentineltoolbox.resources.reference import PRODUCT
from sentineltoolbox.tools.stb_dump_product import convert_datatree_to_structure_str
from sentineltoolbox.verification.cli_compare_products import compare_product_datatrees
from sentineltoolbox.verification.logger import get_validation_logger
from sentineltoolbox.verification.preprocessing_visitors import (
    apply_validation_visitors,
)


@click.command()
@click.argument(
    "input",
    type=str,
    nargs=1,
)
@click.option(
    "-m",
    "--mapping",
    type=str,
)
@click.option(
    "-o",
    "--output-dir",
    type=str,
)
@click.option(
    "--dry-run",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "-n",
    "--name",
    type=str,
)
@click.option(
    "-d",
    "--dump",
    is_flag=True,
    show_default=True,
    default=False,
)
@click.option(
    "-c",
    "--cache",
    type=str,
)
def main(input: Any, mapping: Any, output_dir: Any, dry_run: Any, name: Any, dump: Any, cache: Any) -> None:
    convert_input(input, mapping, output_dir, dry_run, name, dump, cache)


def convert_input(
    input: str | Path,
    mapping: str | None = None,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    name: str | None = None,
    dump: bool = False,
    cache: Path | str | None = None,
) -> None:
    if output_dir is None:
        path_output_dir = Path(".").absolute()
    else:
        path_output_dir = Path(output_dir)
    if not path_output_dir.exists():
        path_output_dir.mkdir(parents=True, exist_ok=True)

    if cache:
        open_datatree_args: dict[str, Any] = dict(local_copy_dir=Path(cache), cache=True)
    else:
        open_datatree_args = {}

    print(f"{input=}, {mapping=}, {path_output_dir=}, {dry_run=}")
    mask_and_scale = True
    if mapping:
        # add tutorial mapping files to mapping manager
        mp = AnyPath(mapping)
        mf = EOPFMappingFactory(mapping_path=mp)
        mm = EOPFMappingManager(mf)
    else:
        mm = None
    product_path = AnyPath.cast(input)
    safe_store = EOSafeStore(
        product_path,
        mask_and_scale=True,
        mapping_manager=mm,
    )  # legacy store to access a file on the given URL
    eop = safe_store.load(name="NEWMAPPING")  # create and return the EOProduct
    target_store_kwargs: dict[Any, Any] = {}
    target_store = EOZarrStore(path_output_dir.as_posix(), mask_and_scale=mask_and_scale, **target_store_kwargs)
    target_store.open(mode=OpeningMode.CREATE_OVERWRITE)
    if not name:
        product_type = eop.attrs["stac_discovery"]["properties"]["product:type"]
        if product_type in [
            "S01RFCANC",
            "S01SM1RAW",
            "S01SM2RAW",
            "S01SM3RAW",
            "S01SM4RAW",
            "S01SM5RAW",
            "S01SM6RAW",
            "S01N1RAW_",
            "S01N2RAW_",
            "S01N3RAW_",
            "S01N4RAW_",
            "S01N5RAW_",
            "S01N6RAW_",
        ]:
            datatake_id = hex(eop.attrs["stac_discovery"]["properties"]["eopf:datatake_id"]).replace("0x", "").zfill(5)
            mission_specific = f"{datatake_id.upper()}_DH"
            name = eop.get_default_file_name_no_extension(mission_specific=mission_specific)
            name = name[:-12] + "XXX" + name[-9:]
        else:
            name = eop.get_default_file_name_no_extension()[:-3] + "XXX"
    target_store[name] = eop
    target_store.close()
    # eop.to_datatree().to_zarr(name, mode="w")
    if dump:
        dump_name = name  # [:-4] + "LAST"
        path_converted_prod = (path_output_dir / name).as_posix() + ".zarr"
        xdt_conv = open_datatree(path_converted_prod)

        products: dict[str, DataTree] = {}
        products[dump_name + "_zarr"] = xdt_conv
        # if isinstance(eop, EOProduct):
        #    products[dump_name + "_eop"] = eop.to_datatree()

        try:
            reference_path = PRODUCT.map()[guess_product_type(eop.attrs)]
        except KeyError:
            pass
        else:
            xdt_ref = open_datatree(reference_path, **open_datatree_args)
            products[dump_name + "_ref"] = xdt_ref
            xdt_ref, xdt_conv = apply_validation_visitors("S01GPSRAW", xdt_ref, xdt_conv)
            name = name + ".diff.log"
            with open(path_output_dir / name, "w") as fp:
                failed_logger = get_validation_logger(stream=fp, fmt="TO CHECK: %(message)s")
                passed_logger = get_validation_logger(stream=fp, fmt="SUCCESS: %(message)s")
                logger = get_validation_logger(stream=fp, fmt="INFO: %(message)s")
                compare_product_datatrees(
                    xdt_ref,
                    xdt_conv,
                    logger=logger,
                    passed_logger=passed_logger,
                    failed_logger=failed_logger,
                )

        """
        try:
            reference = PRODUCT[guess_product_type(eop.attrs)]
        except KeyError:
            pass
        else:
            products[dump_name + "_ref_metadata"] = reference
        """

        for name, datatree in products.items():
            struct_name = name + ".structure.out"
            with open(path_output_dir / struct_name, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree))

            struct_name = name + ".structure_and_type.out"
            with open(path_output_dir / struct_name, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree, dtype=True))

            detail_name = f"{name}.structure-details.out"
            final_path = path_output_dir / "details" / detail_name
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_path, "w") as fp:
                fp.write(convert_datatree_to_structure_str(datatree, details=True, dtype=True))
