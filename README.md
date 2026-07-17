# Creality Print Viewer

Custom Home Assistant integration for local monitoring of Creality 3D printers.

The integration communicates directly with the printer over the local network. No Creality Cloud connection is required.

> [!WARNING]
> This project is currently in an early development stage.
> It has been tested with the Creality Ender-3 V3 KE. Support for other printers has not yet been confirmed.

## Features

The integration currently provides:

- nozzle temperature
- target nozzle temperature
- bed temperature
- target bed temperature
- print progress
- current layer
- total number of layers
- elapsed print time
- remaining print time
- current file name
- feedrate percentage
- printer camera

All entities belonging to one printer are grouped under a single Home Assistant device.

## Requirements

- Home Assistant
- HACS
- a supported Creality printer available on the same local network
- WebSocket access to the printer on port `9999`

## Installation through HACS

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open the menu in the upper-right corner.
4. Select **Custom repositories**.
5. Add this repository:

   `https://github.com/Shidogn/creality-print-viewer`

6. Select the category **Integration**.
7. Install **Creality Print Viewer**.
8. Restart Home Assistant.

## Configuration

After installation:

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Creality Print Viewer**.
4. Enter the local IP address or hostname of the printer.

The integration verifies the connection before creating the configuration entry.

## Companion dashboard card

A dedicated Lovelace card is being developed separately.

The card automatically discovers the entities associated with the selected printer device and does not require individual entity configuration.

## Tested printers

| Manufacturer | Model | Status |
|---|---|---|
| Creality | Ender-3 V3 KE | Tested |

Other Creality printers may use a similar local protocol, but they have not yet been verified.

## Troubleshooting

Before reporting an issue, check that:

- the printer is powered on,
- the printer and Home Assistant are on the same local network,
- the printer's IP address has not changed,
- port `9999` is reachable from Home Assistant,
- the integration logs do not contain connection errors.

Issues can be reported in the GitHub issue tracker.

## Privacy

The integration communicates with the printer locally.

It does not intentionally send printer data to an external service.

## License

This project is licensed under the MIT License.
