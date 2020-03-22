from flask import current_app
import os
import psycopg2
from geojson import Feature, FeatureCollection, loads


class DB_GeoJson(object):
    """
    Helper to retrieve data in GeoJson format from PostgreSQL/Postgis DB
    Useful to load all this in Leaflet in front-end
    """
    def __init__(self, database, user, password, port, host):
        self.connection = psycopg2.connect(database=database, user=user, password=password, port=port, host=host)
        self.cursor = self.connection.cursor()

    def get_table_as_geojson(self, table_name):
        """Get all rows of table in Geojson format"""
        self.cursor.execute("""SELECT ST_AsGeoJson(geom) AS geometry ,
                                        * 
                               FROM {}""".format(table_name))
        
        datas = []
        for row in self.cursor.fetchall():
            if row[0]:
                geom = loads(row[0])
            else:
                geom = None
            fields = [field[0] for field in self.cursor.description]
            props = dict(zip(fields,row))
            datas.append(Feature(properties=props,
                                    geometry=geom))
        
        return FeatureCollection(datas)

    def get_single_data_as_geojson(self, table_name, pk):
        """Get a single row in Geojson format"""
        self.cursor.execute("""SELECT ST_AsGeoJson(geom) AS geometry ,
                                        * 
                               FROM {}
                               WHERE id = {}""".format(table_name, pk))
        
        datas = []
        for row in self.cursor.fetchall():
            if row[0]:
                geom = loads(row[0])
            else:
                geom = None
            fields = [field[0] for field in self.cursor.description]
            props = dict(zip(fields, row))
            datas.append(Feature(properties=props,
                                 geometry=geom))
        
        return FeatureCollection(datas)


def get_app_base_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

def get_instance_folder_path():
    return os.path.join(get_app_base_path(), 'instance')