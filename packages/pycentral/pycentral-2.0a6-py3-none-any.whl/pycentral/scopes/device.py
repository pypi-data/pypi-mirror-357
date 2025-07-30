# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

from .scope_base import ScopeBase
from ..utils import NewCentralURLs
from .scope_maps import ScopeMaps
from ..utils.scope_utils import fetch_attribute


urls = NewCentralURLs()
scope_maps = ScopeMaps()

API_ATTRIBUTE_MAPPING = {
    "scopeId": "id",
    "deviceName": "name",
    "deviceGroupName": "group_name",
    "deviceGroupId": "group_id",
    "serialNumber": "serial",
    "deployment": "deployment",
    "siteName": "site_name",
    "siteId": "site_id",
    "macAddress": "mac",
    "model": "model",
    "persona": "persona",
    "softwareVersion": "software-version",
    "role": "role",
    "partNumber": "part-number",
    "isProvisioned": "provisioned_status",
    "status": "status",
    "deviceType": "device_type",
    "ipv4": "ipv4",
    "deviceFunction": "device_function",
}

REQUIRED_ATTRIBUTES = ["name", "serial"]


class Device(ScopeBase):
    """
    This class holds device and all of its attributes & related methods.
    """

    def __init__(
        self,
        device_attributes=None,
        central_conn=None,
        serial=None,
        from_api=False,
    ):
        """
        Constructor for Device object

        :param serial: Serial number of the device (required if device_attributes is not provided).
        :type serial: str
        :param device_attributes: Attributes of the Device.
        :type device_attributes: dict
        :param central_conn: Instance of class:`pycentral.NewCentralBase`
        to establish connection to Central.
        :type central_conn: class:`NewCentralBase`, optional
        :param from_api: Boolean indicates if the device_attributes is from the
        Central API response.
        :type from_api: bool, optional
        """

        # If device_attributes is provided, use it to set attributes
        self.materialized = from_api
        self.central_conn = central_conn
        if from_api:
            # Rename keys if attributes are from API
            device_attributes = self.__rename_keys(
                device_attributes, API_ATTRIBUTE_MAPPING
            )
            device_attributes["assigned_profiles"] = []
            for key, value in device_attributes.items():
                setattr(self, key, value)

        # If only serial is provided, set it and defer fetching other details
        elif serial:
            self.serial = serial

        # If neither serial nor device_attributes is provided, raise an error
        else:
            raise ValueError(
                "Either 'serial' or 'device_attributes(from api response)' must be provided to create a Device."
            )

    def get_serial(self):
        """
        returns the value of self.serial

        :return: value of self.serial
        :rtype: str
        """
        return fetch_attribute(self, "serial")

    def get(self):
        """
        Fetches the device details from the Central API using the serial number.

        :return: Device attributes as a dictionary.
        :rtype: dict
        """
        if self.central_conn is None:
            raise Exception(
                "Unable to get device without Central connection. Please provide the central connection with the central_conn variable."
            )
        device_data = Device.get_devices(
            self.central_conn,
            search=str(self.get_serial()),
            limit=1,
        )
        self.materialized = len(device_data["items"]) == 1
        if not self.materialized:
            self.materialized = False
            self.central_conn.logger.error(
                f"Unable to fetch device {self.get_serial()} from Central"
            )
        else:
            device_attributes = self.__rename_keys(
                device_data["items"][0], API_ATTRIBUTE_MAPPING
            )
            device_attributes["assigned_profiles"] = []
            for key, value in device_attributes.items():
                setattr(self, key, value)
            self.central_conn.logger.info(
                f"Successfully fetched device {self.get_serial()}'s data from Central."
            )
        return device_data

    @staticmethod
    def get_all_devices(central_conn, new_central_configuration=True):
        """
        Fetches all devices from Central, optionally filtering for new Central configured devices.

        :param central_conn: Instance of class:`pycentral.NewCentralBase` to establish connection to Central.
        :type central_conn: class:`NewCentralBase`
        :param new_central_configuration: If True, only devices that are configured via New Central are returned.
        :type new_central_configuration: bool, optional
        :return: List of device dictionaries fetched from Central.
        :rtype: list
        """
        limit = 100
        next_cursor = 1
        device_list = []

        while True:
            device_resp = Device.get_devices(
                central_conn, limit=limit, next_cursor=next_cursor
            )
            if device_resp is None:
                central_conn.logger.error("Error fetching list of devices")
                device_list = []
                break
            device_list.extend(device_resp["items"])
            if len(device_list) == device_resp["total"]:
                central_conn.logger.info(
                    f"Total devices fetched from account: {len(device_list)}"
                )
                break
            next_cursor += 1

        if new_central_configuration:
            new_central_device_list = [
                device
                for device in device_list
                if device.get("persona") != "-"
            ]
            return new_central_device_list
        return device_list

    @staticmethod
    def get_devices(
        central_conn,
        filter_string=None,
        sort=None,
        search=None,
        site_assigned=None,
        limit=20,
        next_cursor=1,
    ):
        """
        Fetch device inventory from New Central with optional filtering, sorting, and pagination.

        :param filter: Dictionary of attributes to filter devices by.
        :param sort: Sorting criteria for the device list.
        :param search: Search term to apply to device attributes. Search term to filter devices. Supported fields are: "deviceName", "persona", "model", "serialNumber", "macAddress", "ipv4", "softwareVersion"
        :param site_assigned: Specifies the site assignment status of the devices. Can be either "ASSIGNED" or "UNASSIGNED".
        :param limit: Maximum number of devices to return.
        :param next: Pagination cursor for fetching the next set of devices. Minimum is 1

        :return: List of devices matching the criteria.
        :rtype: list
        """
        # Construct API parameters with only non-None values
        api_params = {}
        if filter_string is not None:
            api_params["filter"] = filter_string
        if sort is not None:
            api_params["sort"] = sort
        if search is not None:
            api_params["search"] = search
        if site_assigned is not None:
            api_params["site-assigned"] = site_assigned
        if limit is not None:
            api_params["limit"] = limit
        if next_cursor is not None:
            api_params["next"] = next_cursor

        # Call the Central API
        resp = central_conn.command(
            api_method="GET",
            api_path="network-monitoring/v1alpha1/device-inventory",
            api_params=api_params,
        )

        if resp["code"] != 200:
            central_conn.logger.error(
                f"Error fetching devices: {resp['code']} - {resp['msg']}"
            )
            return []

        return resp["msg"]

    def __rename_keys(self, api_dict, api_attribute_mapping):
        """
        Renames the keys of the attributes from the API response.

        :param api_dict: dict from Central API Response
        :type api_dict: dict
        :param api_attribute_mapping: Dict mapping API keys to object attributes
        :type api_attribute_mapping: dict
        :return: Renamed dictionary of object attributes
        :rtype: dict
        """
        integer_attributes = {"id"}
        renamed_dict = {}

        for key, value in api_dict.items():
            new_key = api_attribute_mapping.get(key)
            if not new_key:
                continue  # Skip unknown keys
            if key in integer_attributes and value is not None:
                value = int(value)
            renamed_dict[new_key] = value
        return renamed_dict
