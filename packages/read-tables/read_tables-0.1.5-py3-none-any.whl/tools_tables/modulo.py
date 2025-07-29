from pyspark.sql import SparkSession
from delta.tables import *
from config import tables_json_path 

def _get_dbutils():
    try:
        return dbutils
    except NameError:
        from pyspark.dbutils import DBUtils
        return DBUtils(SparkSession.builder.getOrCreate())

class Tooltables:

    def __init__(
        self,
        spark: SparkSession,
        container: str = 'stcprojectavolta',
        application_id: str = 'dd627f0a-9742-4307-8851-bc16e8d2bae7',
        tenant_id: str = 'fcc7aafa-b643-4510-955d-3374a25d0f41',
        secret_scope: str = None,
        secret_key: str = None,
        authentication_key: str = None,
        mount_prefix: str = '/mnt',
        raw_folder: str = 'tablesbigquery01'
    ):
        self.spark = spark
        self.container = container
        self.app_id = application_id
        self.tenant_id = tenant_id
        self.mount_point = f"{mount_prefix}/{container}"
        self.raw_folder = raw_folder
        self.dbutils = _get_dbutils()

        if secret_scope and secret_key:
            self.auth_key = self.dbutils.secrets.get(secret_scope, secret_key)
        elif authentication_key:
            self.auth_key = authentication_key
        else:
            raise ValueError("Se debe proporcionar 'authentication_key' o ('secret_scope' y 'secret_key')")

        self._mount_container()
        self._load_tables()

    def _mount_container(self):
        source = f"abfss://{self.container}@stcprojectlab001.dfs.core.windows.net/"
        existing = [mnt.mountPoint for mnt in self.dbutils.fs.mounts()]
        if self.mount_point in existing:
            print(f"Contenedor '{self.container}' ya montado en {self.mount_point}")
            return

        endpoint = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/token"
        configs = {
            "fs.azure.account.auth.type": "OAuth",
            "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
            "fs.azure.account.oauth2.client.id": self.app_id,
            "fs.azure.account.oauth2.client.secret": self.auth_key,
            "fs.azure.account.oauth2.client.endpoint": endpoint
        }
        try:
            self.dbutils.fs.mount(
                source=source,
                mount_point=self.mount_point,
                extra_configs=configs
            )
            print(f"Montado '{self.container}' en {self.mount_point}")
        except Exception as e:
            print(f"Error montando contenedor '{self.container}': {e}")

    def _unmount_container(self):
        try:
            self.dbutils.fs.unmount(self.mount_point)
            print(f"Desmontado contenedor '{self.container}' de {self.mount_point}")
        except Exception as e:
            print(f"Error desmontando contenedor '{self.container}': {e}")

    def _load_tables(self):

        base = f"{self.mount_point}/{self.raw_folder}"
        for entry in tables_json_path:
            uc_table = entry.get("uc_table")
            path = f"{base}/{uc_table}/"
            try:
                df = self.spark.read.format("delta").load(path)
                setattr(self, f"df_{uc_table}", df)
                df.createOrReplaceTempView(uc_table)
                print(f"Cargada tabla '{uc_table}' desde {path}")
            except Exception as e:
                print(f"Error cargando tabla '{uc_table}' desde {path}: {e}")

    def unmount(self):
        self._unmount_container()

