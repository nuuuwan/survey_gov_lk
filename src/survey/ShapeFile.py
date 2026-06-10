import os
import sys

import geopandas as gpd
from utils import JSONFile, Log

log = Log("ShapeFile")


class ShapeFile:
    def __init__(self, shp_file_path: str):
        if not os.path.isfile(shp_file_path) or not shp_file_path.endswith(
            ".shp"
        ):
            raise ValueError("Please provide a valid .shp file path.")
        self.shp_file_path = shp_file_path

    def build_geojson(self, geojson_path: str, n_rows: int = None):
        gdf = gpd.read_file(self.shp_file_path)
        if n_rows is not None:
            gdf = gdf.head(n_rows)
        gdf.to_file(geojson_path, driver="GeoJSON")
        n_rows = gdf.shape[0]
        geojson_file_size_m = os.path.getsize(geojson_path) / 1_000_000
        log.info(
            f"Wrote {n_rows:,} rows"
            + f" from {self.shp_file_path}"
            + f" to {geojson_path} ({geojson_file_size_m:.2f} MB)"
        )

    def build_properties_json(self, json_path: str, n_rows: int = None):
        gdf = gpd.read_file(self.shp_file_path)
        properties_df = gdf.drop(columns="geometry")
        d_list = properties_df.to_dict(orient="records")

        def expand(d):
            if d["GND_C"] is None or d["DSD_C"] is None:
                log.warning(f"Skipping row: {d}")
                gnd_id = None
            else:
                gnd_c = int(d["GND_C"])
                dsd_c = int(d["DSD_C"])
                district_c = int(d["DISTRICT_C"])
                province_c = int(d["PROVINCE_C"])

                gnd_id = f"LK-{
                    province_c:01d}{
                    district_c:01d}{
                    dsd_c:02d}{
                    gnd_c:03d}"
            d = dict(gnd_id=gnd_id) | d
            return d

        d_list = [expand(d) for d in d_list]
        d_list.sort(
            key=lambda d: (
                str(d["PROVINCE_C"]),
                str(d["DISTRICT_C"]),
                str(d["DSD_C"]),
                str(d["GND_C"]),
            )
        )
        if n_rows is not None:
            d_list = d_list[:n_rows]

        json_file = JSONFile(json_path)
        json_file.write(d_list)

        n_rows = properties_df.shape[0]
        log.info(
            f"Wrote {n_rows:,} rows "
            + f" to {json_file}"
            + f" from {self.shp_file_path}"
        )


if __name__ == "__main__":
    shp_file_path = sys.argv[1]
    shape_utils = ShapeFile(shp_file_path)
    # shape_utils.build_geojson(os.path.join("" "data", "GN.geojson"))
    # shape_utils.build_geojson(
    #     os.path.join("" "data", "GN.sample10.geojson"),
    #     n_rows=10,
    # )
    shape_utils.build_properties_json(
        os.path.join("" "data", "GN.properties.json"),
    )
    shape_utils.build_properties_json(
        os.path.join("" "data", "GN.properties.sample10.json"),
        n_rows=10,
    )
