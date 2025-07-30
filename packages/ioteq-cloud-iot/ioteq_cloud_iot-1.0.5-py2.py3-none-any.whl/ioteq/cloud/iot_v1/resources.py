"""
"Copyright 2025 IO-TEQ, LLC."

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from enum import Enum
from datetime import datetime

class MqttState():
    r"""Indicates whether an MQTT connection is enabled or disabled.
    See the field description for details.
    """
    MQTT_STATE_UNSPECIFIED = "MQTT_STATE_UNSPECIFIED"
    MQTT_ENABLED = "MQTT_ENABLED"
    MQTT_DISABLED = "MQTT_DISABLED"


class HttpState():
    r"""Indicates whether DeviceService (HTTP) is enabled or disabled
    for the registry. See the field description for details.
    """
    HTTP_STATE_UNSPECIFIED = "HTTP_STATE_UNSPECIFIED"
    HTTP_ENABLED = "HTTP_ENABLED"
    HTTP_DISABLED = "HTTP_DISABLED"


class LogLevel:
    r"""**Beta Feature**

    The logging verbosity for device activity. Specifies which events
    should be written to logs. For example, if the LogLevel is ERROR,
    only events that terminate in errors will be logged. LogLevel is
    inclusive; enabling INFO logging will also enable ERROR logging.
    """
    LOG_LEVEL_UNSPECIFIED = "LOG_LEVEL_UNSPECIFIED"
    NONE = "NONE"
    ERROR = "ERROR"
    INFO = "INFO"
    DEBUG = "DEBUG"


class PublicKeyCertificateFormat():
    r"""The supported formats for the public key."""
    UNSPECIFIED_PUBLIC_KEY_CERTIFICATE_FORMAT = "UNSPECIFIED_PUBLIC_KEY_CERTIFICATE_FORMAT"
    X509_CERTIFICATE_PEM = "X509_CERTIFICATE_PEM"


class PublicKeyFormat(Enum):
    r"""The supported formats for the public key."""
    UNSPECIFIED_PUBLIC_KEY_FORMAT = "UNSPECIFIED_PUBLIC_KEY_FORMAT"
    RSA_PEM = "RSA_PEM"
    RSA_X509_PEM = "RSA_X509_PEM"
    ES256_PEM = "ES256_PEM"
    ES256_X509_PEM = "ES256_X509_PEM"

class PublicKeyCredential():
    def __init__(self, format: PublicKeyFormat, key: bytes):
        self.format = format
        self.key = key
    
    def __getitem__(self, arg):
        return getattr(self, arg)

    def get(self, arg):
        return getattr(self, arg)

