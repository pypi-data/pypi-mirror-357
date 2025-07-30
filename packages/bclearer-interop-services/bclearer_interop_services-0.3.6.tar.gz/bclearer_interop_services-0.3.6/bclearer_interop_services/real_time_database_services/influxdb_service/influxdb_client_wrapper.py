import os
from datetime import datetime

__all__ = ["InfluxDBWrapper"]


class InfluxDBWrapper:
    """
    Simple wrapper around the InfluxDBClient to write time series data.
    Reads connection parameters from environment:
      INFLUXDB_URL (default: http://localhost:8086)
      INFLUXDB_TOKEN
      INFLUXDB_ORG
      INFLUXDB_BUCKET
    """

    def __init__(
        self,
        url: str = None,
        token: str = None,
        org: str = None,
        bucket: str = None,
    ):
        self.url = url or os.getenv(
            "INFLUXDB_URL",
            "http://localhost:8086",
        )
        self.token = token or os.getenv(
            "INFLUXDB_TOKEN"
        )
        self.org = org or os.getenv(
            "INFLUXDB_ORG"
        )
        self.bucket = (
            bucket
            or os.getenv(
                "INFLUXDB_BUCKET"
            )
        )
        if not all(
            [
                self.token,
                self.org,
                self.bucket,
            ]
        ):
            raise ValueError(
                "INFLUXDB_TOKEN, INFLUXDB_ORG, and INFLUXDB_BUCKET must be set"
            )
        # Delay import of influxdb_client until runtime
        try:
            from influxdb_client import (
                InfluxDBClient,
            )
            from influxdb_client.client.write_api import (
                SYNCHRONOUS,
            )
        except ImportError as e:
            raise RuntimeError(
                "influxdb-client package is required for InfluxDBWrapper"
            ) from e
        self.client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org,
        )
        self.write_api = self.client.write_api(
            write_options=SYNCHRONOUS
        )
        self.delete_api = (
            self.client.delete_api()
        )

    def write_points(
        self,
        measurement: str,
        records: list,
        tag_keys: list = None,
        timestamp_field: str = None,
    ):
        """
        Write a list of record dicts to InfluxDB under the given measurement.
        All keys except tags and timestamp are treated as fields.
        :param measurement: name of the measurement
        :param records: list of dicts representing points
        :param tag_keys: list of keys to treat as tags
        :param timestamp_field: key to use for point timestamp (ISO8601 string)
        """
        # Delay import of Point
        from influxdb_client import (
            Point,
        )

        points = []
        for rec in records:
            p = Point(measurement)
            # tags
            if tag_keys:
                for key in tag_keys:
                    if key in rec:
                        p.tag(
                            key,
                            rec[key],
                        )
            # fields
            for (
                key,
                value,
            ) in rec.items():
                if (
                    key
                    == timestamp_field
                ):
                    continue
                if (
                    tag_keys
                    and key in tag_keys
                ):
                    continue
                # only numeric or string fields; skip lists/dicts
                p.field(key, value)
            # timestamp
            if (
                timestamp_field
                and timestamp_field
                in rec
            ):
                try:
                    # expect ISO format
                    from datetime import (
                        datetime,
                    )

                    dt = datetime.fromisoformat(
                        rec[
                            timestamp_field
                        ]
                    )
                    p.time(dt)
                except Exception:
                    # skip setting time if parse fails
                    pass
            points.append(p)
        if points:
            self.write_api.write(
                bucket=self.bucket,
                org=self.org,
                record=points,
            )

    def delete_all_data(
        self, measurement: str = None
    ) -> None:
        """
        Delete all data from the bucket, optionally filtered by measurement.

        Args:
            measurement: Optional measurement name to limit deletion to one measurement
                        If None, deletes all data in the bucket
        """
        # Set very early start time and future end time to cover all possible data
        start = "1970-01-01T00:00:00Z"  # Unix epoch start
        stop = "2099-12-31T23:59:59Z"  # Far future

        # Build predicate if measurement specified
        predicate = None
        if measurement:
            predicate = f'_measurement="{measurement}"'
            print(
                f"Deleting all data for measurement '{measurement}' from bucket '{self.bucket}'"
            )
        else:
            print(
                f"Deleting ALL data from bucket '{self.bucket}'"
            )

        # Execute delete operation
        try:
            self.delete_api.delete(
                start=start,
                stop=stop,
                predicate=predicate,
                bucket=self.bucket,
            )
            print(
                f"Data deletion completed successfully"
            )
        except Exception as e:
            print(
                f"Error deleting data: {e}"
            )
            raise
