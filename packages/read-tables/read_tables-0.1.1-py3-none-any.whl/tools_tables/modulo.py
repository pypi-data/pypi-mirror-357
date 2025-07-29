from pyspark.sql import SparkSession
from delta.tables import *

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
        authentication_key: str = 'hbw8Q~wwdJ5xy.QxaiwtivEM6shUJnS3~3DhpbmN',
        tenant_id: str = 'fcc7aafa-b643-4510-955d-3374a25d0f41',
        mount_prefix: str = '/mnt',
        raw_folder: str = 'tablesbigquery01'
    ):
        self.spark = spark
        self.container = container
        self.app_id = application_id
        self.auth_key = authentication_key
        self.tenant_id = tenant_id
        self.mount_point = f"{mount_prefix}/{container}"
        self.raw_folder = raw_folder
        self.dbutils = _get_dbutils()

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
        # Lista de tablas a cargar (nombres de carpetas)
        tabla_nombres = [
            'ta_app', 'ta_campaign', 'ta_delivery', 'ta_delivery_kpis', 'ta_delivery_log',
            'ta_deliveryrt_log', 'ta_emporium_store', 'ta_fnb_purchases', 'ta_geo_push',
            'ta_geo_push_customer', 'ta_hist_suscription', 'ta_magento_transaction_lines',
            'ta_magento_transactions', 'ta_online_orders', 'ta_partners_accounts', 'ta_profile',
            'ta_program', 'ta_promotion_code', 'ta_promotion_code_redemption',
            'ta_purchase_transaction_details', 'ta_push_notification', 'ta_push_profile_center',
            'ta_push_tracking_notification', 'ta_service', 'ta_tracking_log', 'ta_trackingrt_log',
            'ta_workflow', 'DBR_Config', 'DBR_Control', 'ta_attribution_window', 'ta_labels_master',
            'ta_user_campaign_info', 'ta_ga_transactions', 'ta_labels_handy_match',
            'STG_delivery_log_AWS', 'STG_tracking_log2_AWS', 'ta_red_status_segment',
            'ta_red_segment_grouped', 'ta_labels_push_handy_match', 'va_emails_kpis_daily',
            'va_upgrade_campaign_kpis_daily'
        ]
        for nombre in tabla_nombres:
            ruta = f"{base}/{nombre}/"
            try:
                df = self.spark.read.format("delta").load(ruta)
                # Atributo con nombre dinámico
                setattr(self, f"df_{nombre}", df)
                # Crear vista temporal utilizando el mismo nombre
                df.createOrReplaceTempView(nombre)
                print(f"Cargada tabla '{nombre}' desde {ruta}")
            except Exception as e:
                print(f"Error cargando tabla '{nombre}': {e}")

    def unmount(self):
        self._unmount_container()

