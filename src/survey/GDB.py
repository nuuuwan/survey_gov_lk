import os
import sys

import fiona
import geopandas as gpd
from utils import JSONFile, Log

log = Log("GDB")


class GDB:
    def __init__(self, path):
        self.path = path

    def analyse(self):
        layers = fiona.listlayers(self.path)
        log.info(f"Found {len(layers)} layer(s) in {self.path}")
        for layer in layers:
            gdf = gpd.read_file(self.path, layer=layer)
            n_rows, n_cols = gdf.shape
            col_info = ", ".join(
                f"{col} ({dtype})" for col, dtype in gdf.dtypes.items()
            )
            log.info(
                f"  Layer: {layer!r}"
                f" | rows={n_rows:,}, cols={n_cols}"
                f" | crs={gdf.crs}"
                f" | columns: {col_info}"
            )

    def build_properties_json(self, layer, json_path, n_rows=None):
        gdf = gpd.read_file(self.path, layer=layer)
        if n_rows is not None:
            gdf = gdf.head(n_rows)
        properties_df = gdf.drop(columns="geometry")
        d_list = properties_df.to_dict(orient="records")
        JSONFile(json_path).write(d_list)
        log.info(
            f"Wrote {len(d_list):,} rows from layer {layer!r}"
            f" to {json_path}"
        )


if __name__ == "__main__":
    gdb_path = sys.argv[1]
    gdb = GDB(gdb_path)
    gdb.build_properties_json(
        layer="GN",
        json_path=os.path.join("" "data", "GN.properties.gdb.json"),
    )
