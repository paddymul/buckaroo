from buckaroo.serialization_utils import pd_to_obj    
def test_geop_serialization():
    from shapely.geometry import Point
    import geopandas
    d = {'col1': ['name1', 'name2'], 'geometry': [Point(1, 2), Point(2, 1)]}
    gdf = geopandas.GeoDataFrame(d, crs="EPSG:3857")
    gdf.to_json(orient='table')


expected_serialization = {
    "type": "FeatureCollection",
    "schema":{
        "fields":[  { "name":"id",       "type":"integer"  },
                    { "name":"col1",     "type":"string"  },
                    { "name":"geometry", "type": "FeatureCollection"}],
        "primaryKey":[ "id"  ],
        "pandas_version":"geo-1.4.0"
  },

    "data": [
        {"col1": "name1",
         "id": "0",
         "features": {"type": "Feature",
                      "geometry": {
                          "type": "Point",
                          "coordinates": [1.0, 2.0 ]}}},
        {"col1": "name2",
         "id": "1",
         "features": {"type": "Feature",
                      "geometry": {
                          "type": "Point",
                          "coordinates": [2.0, 1.0 ]}}}
    ]
}
