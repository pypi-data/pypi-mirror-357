from .const import (
    API_ENDPOINT_LIST_DEVICE_DETAILS,
    PARAM_PAGE_SIZE,
    PARAM_PAGE,
    PARAM_DEVICE_ID,
    PARAM_CHANNEL_ID,
    API_ENDPOINT_CONTROL_DEVICE_PTZ,
    API_ENDPOINT_MODIFY_DEVICE_ALARM_STATUS,
    API_ENDPOINT_GET_DEVICE_STATUS,
    API_ENDPOINT_SET_DEVICE_STATUS,
    API_ENDPOINT_GET_DEVICE_NIGHT_VISION_MODE,
    API_ENDPOINT_DEVICE_STORAGE,
    API_ENDPOINT_RESTART_DEVICE,
    API_ENDPOINT_BIND_DEVICE_LIVE,
    API_ENDPOINT_GET_DEVICE_ONLINE,
    API_ENDPOINT_GET_DEVICE_LIVE_INFO,
    API_ENDPOINT_SET_DEVICE_SNAP,
    PARAM_MODE,
    PARAM_ENABLE_TYPE,
    PARAM_ENABLE,
    PARAM_COUNT,
    PARAM_DEVICE_LIST,
    PARAM_DEVICE_NAME,
    PARAM_DEVICE_STATUS,
    PARAM_DEVICE_ABILITY,
    PARAM_DEVICE_VERSION,
    PARAM_BRAND,
    PARAM_DEVICE_MODEL,
    PARAM_CHANNEL_LIST,
    PARAM_CHANNEL_NAME,
    PARAM_CHANNEL_STATUS,
    PARAM_CHANNEL_ABILITY,
    PARAM_STREAM_ID,
    PARAM_OPERATION,
    PARAM_DURATION,
    API_ENDPOINT_GET_DEVICE_ALARM_PARAM,
    API_ENDPOINT_SET_DEVICE_NIGHT_VISION_MODE,
    PARAM_PRODUCT_ID,
    PARAM_PROPERTIES,
    API_ENDPOINT_GET_IOT_DEVICE_PROPERTIES,
    API_ENDPOINT_SET_IOT_DEVICE_PROPERTIES,
    API_ENDPOINT_DEVICE_SD_CARD_STATUS,
    PARAM_CHANNEL_NUM,
    PARAM_PARENT_PRODUCT_ID,
    PARAM_PARENT_DEVICE_ID,
    PARAM_REF,
    PARAM_CONTENT,
    API_ENDPOINT_IOT_DEVICE_CONTROL,
    PARAM_MULTI_FLAG,
    API_ENDPOINT_GET_DEVICE_POWER_INFO,
    API_ENDPOINT_GET_PRODUCT_MODEL,
    API_ENDPOINT_GET_IOT_DEVICE_DETAIL_INFO,
    PARAM_ABILITY_REFS,
    PARAM_CHANNELS,
    PARAM_ACCESS_TYPE, API_ENDPOINT_WAKE_UP_DEVICE, PARAM_URL,
)
from .openapi import ImouOpenApiClient


class ImouChannel:
    def __init__(
        self,
        channel_id: str,
        channel_name: str,
        channel_status: str,
        channel_ability: str,
    ):
        self._channel_id = channel_id
        self._channel_name = channel_name
        self._channel_status = channel_status
        self._channel_ability = channel_ability
        self._channel_ability_refs = "unknown"

    @property
    def channel_id(self) -> str:
        return self._channel_id

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @property
    def channel_status(self) -> str:
        return self._channel_status

    @property
    def channel_ability(self) -> str:
        return self._channel_ability

    @property
    def channel_ability_refs(self) -> str:
        return self._channel_ability_refs

    def set_channel_ability_refs(self, channel_ability_refs: str):
        self._channel_ability_refs = channel_ability_refs


class ImouDevice:
    def __init__(
        self,
        device_id: str,
        device_name: str,
        device_status: str,
        brand: str,
        device_model: str,
    ):
        self._device_id = device_id
        self._device_name = device_name
        self._device_status = device_status
        self._device_ability = "unknown"
        self._device_ability_refs = "unknown"
        self._brand = brand
        self._device_model = device_model
        self._device_version = "unknown"
        self._channel_number = 0
        self._channels = []
        self._product_id = None
        self._parent_product_id = None
        self._parent_device_id = None
        self._is_multi = False
        self._is_ipc = False
        self._access_type = "PaaS"

    @property
    def device_id(self) -> str:
        return self._device_id

    @property
    def device_name(self) -> str:
        return self._device_name

    @property
    def device_status(self) -> str:
        return self._device_status

    @property
    def channels(self) -> []:
        return self._channels

    @property
    def device_ability(self) -> str:
        return self._device_ability

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def device_model(self) -> str:
        return self._device_model

    @property
    def device_version(self) -> str:
        return self._device_version

    @property
    def product_id(self) -> str:
        return self._product_id

    @property
    def parent_product_id(self) -> str:
        return self._parent_product_id

    @property
    def parent_device_id(self) -> str:
        return self._parent_device_id

    @property
    def is_ipc(self) -> bool:
        return (
            self._channel_number is not None and self._channel_number == 1
        ) or self._is_multi

    @property
    def device_ability_refs(self) -> str:
        return self._device_ability_refs

    @property
    def access_type(self) -> str:
        return self._access_type

    def set_product_id(self, product_id: str) -> None:
        self._product_id = product_id

    def set_channels(self, channels: []) -> None:
        self._channels = channels

    def set_channel_number(self, channel_number: int):
        self._channel_number = channel_number

    def set_device_ability(self, device_ability: str):
        self._device_ability = device_ability

    def set_device_version(self, device_version: str):
        self._device_version = device_version

    def set_parent_product_id(self, parent_product_id: str):
        self._parent_product_id = parent_product_id

    def set_parent_device_id(self, parent_device_id: str):
        self._parent_device_id = parent_device_id

    def set_is_multi(self, is_multi: bool):
        self._is_multi = is_multi

    def set_device_ability_refs(self, device_ability_refs: str):
        self._device_ability_refs = device_ability_refs

    def set_access_type(self, access_type: str):
        self._access_type = access_type


class ImouDeviceManager:
    def __init__(self, imou_api_client: ImouOpenApiClient):
        self._imou_api_client = imou_api_client

    async def async_get_devices(
        self, page: int = 1, page_size: int = 10
    ) -> list[ImouDevice]:
        """GET DEVICE LIST"""
        params = {
            PARAM_PAGE: page,
            PARAM_PAGE_SIZE: page_size,
        }
        data = await self._imou_api_client.async_request_api(
            API_ENDPOINT_LIST_DEVICE_DETAILS, params
        )
        if data[PARAM_COUNT] == 0:
            return []
        devices = []
        for device in data[PARAM_DEVICE_LIST]:
            device_id = device[PARAM_DEVICE_ID]
            device_name = device[PARAM_DEVICE_NAME]
            device_status = device[PARAM_DEVICE_STATUS]
            brand = device[PARAM_BRAND]
            device_model = device.get(PARAM_DEVICE_MODEL, "unknown")
            imou_device = ImouDevice(
                device_id, device_name, device_status, brand, device_model
            )
            if PARAM_DEVICE_ABILITY in device:
                imou_device.set_device_ability(device[PARAM_DEVICE_ABILITY])
            if PARAM_DEVICE_VERSION in device:
                imou_device.set_device_version(device[PARAM_DEVICE_VERSION])
            if PARAM_PARENT_PRODUCT_ID in device:
                imou_device.set_parent_product_id(device[PARAM_PARENT_PRODUCT_ID])
            if PARAM_PARENT_DEVICE_ID in device:
                imou_device.set_parent_device_id(device[PARAM_PARENT_DEVICE_ID])
            if PARAM_CHANNEL_NUM in device:
                imou_device.set_channel_number(device[PARAM_CHANNEL_NUM])
            if PARAM_MULTI_FLAG in device:
                imou_device.set_is_multi(device[PARAM_MULTI_FLAG])
            if PARAM_ACCESS_TYPE in device:
                imou_device.set_access_type(device[PARAM_ACCESS_TYPE])
            if PARAM_CHANNEL_LIST in device:
                channel_list = device[PARAM_CHANNEL_LIST]
                channels = []
                for channel in channel_list:
                    channel_id = (
                        str(channel[PARAM_CHANNEL_ID])
                        if isinstance(channel[PARAM_CHANNEL_ID], int)
                        else channel[PARAM_CHANNEL_ID]
                    )
                    channel_name = channel[PARAM_CHANNEL_NAME]
                    channel_status = channel[PARAM_CHANNEL_STATUS]
                    channel_ability = channel.get(PARAM_CHANNEL_ABILITY, "unknown")
                    channel = ImouChannel(
                        channel_id, channel_name, channel_status, channel_ability
                    )
                    channels.append(channel)
                imou_device.set_channels(channels)
            # If it is an iot device, update the abilityRefs field to determine the entity
            # that needs to be registered based on this field
            if PARAM_PRODUCT_ID in device:
                imou_device.set_product_id(device[PARAM_PRODUCT_ID])
                await self._async_update_device_ability_refs(imou_device)
            devices.append(imou_device)
        # If the return quantity is equal to the requested quantity, continue to request the next page
        if data[PARAM_COUNT] == page_size:
            devices.extend(await self.async_get_devices(page + 1, page_size))
        return devices

    async def async_control_device_ptz(
        self, device_id: str, channel_id: str, operation: int, duration: int
    ) -> None:
        """control ptz"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_OPERATION: operation,
            PARAM_DURATION: duration,
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_CONTROL_DEVICE_PTZ, params
        )

    async def async_modify_device_alarm_status(
        self, device_id: str, channel_id: str, enabled: bool
    ) -> None:
        """SET DEVICE ALARM STATUS"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_ENABLE: enabled,
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_MODIFY_DEVICE_ALARM_STATUS, params
        )

    async def async_get_device_status(
        self, device_id: str, channel_id: str, enable_type: str
    ) -> dict[any, any]:
        """obtain device capability switch status"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_ENABLE_TYPE: enable_type,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_STATUS, params
        )

    async def async_get_device_online_status(self, device_id: str) -> dict[any, any]:
        """GET DEVICE ONLINE STATUS"""
        params = {
            PARAM_DEVICE_ID: device_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_ONLINE, params
        )

    async def async_set_device_status(
        self, device_id: str, channel_id: str, enable_type: str, enable: bool
    ) -> None:
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_ENABLE_TYPE: enable_type,
            PARAM_ENABLE: enable,
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_SET_DEVICE_STATUS, params
        )

    async def async_get_device_night_vision_mode(
        self, device_id: str, channel_id: str
    ) -> dict[any, any]:
        """obtain device night vision mode"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_NIGHT_VISION_MODE, params
        )

    async def async_set_device_night_vision_mode(
        self, device_id: str, channel_id: str, night_vision_mode: str
    ) -> None:
        """set device night vision mode"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_MODE: night_vision_mode,
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_SET_DEVICE_NIGHT_VISION_MODE, params
        )

    async def async_get_device_storage(self, device_id: str) -> dict[any, any]:
        """obtain device storage media capacity information"""
        params = {PARAM_DEVICE_ID: device_id}
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_DEVICE_STORAGE, params
        )

    async def async_restart_device(self, device_id: str) -> None:
        """reboot device"""
        params = {PARAM_DEVICE_ID: device_id}
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_RESTART_DEVICE, params
        )

    async def async_get_stream_url(
        self, device_id: str, channel_id: str
    ) -> dict[any, any]:
        """obtain the hls stream address of the device"""
        params = {PARAM_DEVICE_ID: device_id, PARAM_CHANNEL_ID: channel_id}
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_LIVE_INFO, params
        )

    async def async_get_device_snap(
        self, device_id: str, channel_id: str
    ) -> dict[any, any]:
        params = {PARAM_DEVICE_ID: device_id, PARAM_CHANNEL_ID: channel_id}
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_SET_DEVICE_SNAP, params
        )

    async def async_create_stream_url(
        self, device_id: str, channel_id: str, stream_id: int = 0
    ) -> dict[any, any]:
        """create device hls stream address"""
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_CHANNEL_ID: channel_id,
            PARAM_STREAM_ID: stream_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_BIND_DEVICE_LIVE, params
        )

    async def async_get_device_alarm_param(
        self, device_id: str, channel_id: str
    ) -> None:
        """set device alarm status"""
        params = {PARAM_DEVICE_ID: device_id, PARAM_CHANNEL_ID: channel_id}
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_ALARM_PARAM, params
        )

    async def async_get_iot_device_properties(
        self, device_id: str, channel_id: str | None, product_id: str, properties: []
    ) -> dict[any, any]:
        params = {
            PARAM_DEVICE_LIST: [
                {
                    PARAM_DEVICE_ID: device_id,
                    PARAM_CHANNEL_ID: channel_id,
                    PARAM_PRODUCT_ID: product_id,
                    PARAM_PROPERTIES: properties,
                }
            ]
        }
        return (
            await self._imou_api_client.async_request_api(
                API_ENDPOINT_GET_IOT_DEVICE_PROPERTIES, params
            )
        ).get(PARAM_DEVICE_LIST, [{}])[0]

    async def async_set_iot_device_properties(
        self, device_id: str, channel_id: str | None, product_id: str, properties: dict
    ) -> None:
        params = {
            PARAM_DEVICE_LIST: [
                {
                    PARAM_DEVICE_ID: device_id,
                    PARAM_CHANNEL_ID: int(channel_id)
                    if channel_id is not None
                    else channel_id,
                    PARAM_PRODUCT_ID: product_id,
                    PARAM_PROPERTIES: properties,
                }
            ]
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_SET_IOT_DEVICE_PROPERTIES, params
        )

    async def async_get_device_sd_card_status(self, device_id: str) -> dict[any, any]:
        params = {PARAM_DEVICE_ID: device_id}
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_DEVICE_SD_CARD_STATUS, params
        )

    async def async_iot_device_control(
        self, device_id: str, product_id: str, ref: str, content: dict
    ) -> dict[str, any]:
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_PRODUCT_ID: product_id,
            PARAM_REF: ref,
            PARAM_CONTENT: content,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_IOT_DEVICE_CONTROL, params
        )

    async def async_get_device_power_info(self, device_id: str) -> dict[any, any]:
        params = {
            PARAM_DEVICE_ID: device_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_DEVICE_POWER_INFO, params
        )

    async def async_wake_up_device(self, device_id: str) -> None:
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_URL: "/device/wakeup",
        }
        await self._imou_api_client.async_request_api(
            API_ENDPOINT_WAKE_UP_DEVICE, params
        )



    async def async_get_product_model(self, product_id: str) -> dict[any, any]:
        params = {
            PARAM_PRODUCT_ID: product_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_PRODUCT_MODEL, params
        )

    async def async_get_iot_device_detail_info(
        self, device_id: str, product_id: str
    ) -> dict[any, any]:
        params = {
            PARAM_DEVICE_ID: device_id,
            PARAM_PRODUCT_ID: product_id,
        }
        return await self._imou_api_client.async_request_api(
            API_ENDPOINT_GET_IOT_DEVICE_DETAIL_INFO, params
        )

    async def _async_update_device_ability_refs(self, imou_device: ImouDevice) -> None:
        device_id = imou_device.device_id
        if imou_device.parent_product_id is not None:
            device_id = (
                imou_device.device_id
                + "_"
                + imou_device.parent_device_id
                + "_"
                + imou_device.parent_product_id
            )
        device_detail = await self.async_get_iot_device_detail_info(
            device_id,
            imou_device.product_id,
        )
        imou_device.set_device_ability_refs(
            device_detail.get(PARAM_ABILITY_REFS, "unknown")
        )
        if device_detail.get(PARAM_CHANNELS) and imou_device.channels:
            channels_detail = device_detail.get(PARAM_CHANNELS)
            channel_detail_map = {
                channel_detail.get(PARAM_CHANNEL_ID): channel_detail.get(
                    PARAM_ABILITY_REFS, "unknown"
                )
                for channel_detail in channels_detail
            }
            for channel in imou_device.channels:
                channel_id = channel.channel_id
                if channel_id in channel_detail_map:
                    channel.set_channel_ability_refs(channel_detail_map[channel_id])
