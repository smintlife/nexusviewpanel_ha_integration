# Nexus View Panel Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/smintlife/nexusviewpanel_ha_integration)](https://github.com/smintlife/nexusviewpanel_ha_integration/releases)
[![GitHub issues](https://img.shields.io/github/issues/smintlife/nexusviewpanel_ha_integration)](https://github.com/smintlife/nexusviewpanel_ha_integration/issues)

This integration connects your [Nexus View Panel](https://www.smintlife.de/nexus) application to Home Assistant, allowing you to control and automate your panel.



---

## 🚀 Features

This integration creates the following entities for your Nexus View Panel device:

* **Switch:** A `switch.display` to turn the screen on and off.
* **Number:** A `number.configured_brightness` slider to set the app's configured brightness (0-100).
* **Sensor:** A `sensor.battery` to monitor the device's battery level.
* **Binary Sensors:** Multiple sensors (e.g., `binary_sensor.kiosk_mode`, `binary_sensor.fullscreen`) that reflect the status of app settings. *(These are disabled by default and must be manually enabled after setup.)*
* **Buttons:**
    * **Control Buttons:** "Get Config", "Get Device Info", "Close Floating View".
    * **Dynamic Tab Buttons:** Creates "Reload" and "Float" buttons for every tab in your configuration.

---

## 🛠️ Prerequisites

1.  A running Home Assistant instance.
2.  [HACS (Home Assistant Community Store)](https://hacs.xyz/) must be installed.
3.  The **Nexus View Panel** app running on a device.
4.  The **API function** must be enabled within the app (this generates your API token and port).

---

## ⚙️ Installation

This integration is available as a "Custom Repository" in HACS.

1.  In your Home Assistant instance, go to **HACS**.
2.  Click on **"Integrations"** and then click the three-dot menu in the top right.
3.  Select **"Custom repositories"**.
4.  In the "Repository" field, paste the following URL: [https://github.com/smintlife/nexusviewpanel_ha_integration](https://github.com/smintlife/nexusviewpanel_ha_integration)
5.  In the "Category" field, select **"Integration"**.
6.  Click **"Add"**.
7.  Close the window. The "Nexus View Panel" integration will now appear in HACS.
8.  Click **"Install"** and follow the prompts.
9.  **Restart Home Assistant** when prompted by HACS.

### Manual Installation (Alternative)

1.  Download the [latest release](https://github.com/smintlife/nexusviewpanel_ha_integration/releases).
2.  Copy the `custom_components/nexus_view_panel` folder into the `config` directory of your Home Assistant instance.
3.  Restart Home Assistant.

---

## 🔧 Configuration

After installation, the integration is configured via the UI:

1.  Go to **Settings > Devices & Services**.
2.  Click **"Add Integration"** in the bottom right.
3.  Search for **"Nexus View Panel"** and select it.
4.  You will have two options to add your device:

### Option A: Via QR Code (Recommended)

1.  Select **"Connect using QR Code String"**.
2.  Open your Nexus View Panel app, go to API settings, and tap "Show QR Code".
3.  Scan this QR code with your **smartphone's native camera app** (not the Home Assistant app).
4.  Copy the text your camera provides (it starts with `http://...`).
5.  Paste this entire string into the field in Home Assistant.

### Option B: Manual Entry

1.  Select **"Connect by entering details manually"**.
2.  Enter the **IP Address**, **Port**, and **API Token** shown in your Nexus View Panel app's API settings.

### Final Step

1.  **Device Name:** Provide a friendly name for your device (e.g., "Living Room Wall Tablet").
2.  **Polling Intervals:** Adjust the intervals (in seconds) for how often Home Assistant should poll the device status (battery) and the config status (tabs, settings).
3.  Click "Submit".

The integration is now set up, and all entities are available!

---

## 🤝 Contributing

Issues and pull requests are warmly welcome. If you find a problem, please create an [Issue](https://github.com/smintlife/nexusviewpanel_ha_integration/issues).

## 📄 License

MIT License (See `LICENSE` file for details)