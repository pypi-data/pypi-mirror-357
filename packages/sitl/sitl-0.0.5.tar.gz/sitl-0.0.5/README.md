# Python Wrapper for the Betaflight SITL

```bash
pip install sitl
```

Run
```bash
ui-server
```

Navigate to [http://localhost:13337](http://localhost:13337)

New terminal: Run
```bash
sitl-websockify
```

Navigate to [https://app.betaflight.com](https://app.betaflight.com). `Options` => `Enable manual connection mode`. Port: `Manual Selection` and paste `ws://127.0.0.1:6761`

Create gamepad mapping in the following form:

```json
{
    "throttle": {"axis": 1, "invert": true},
    "yaw": {"axis": 0, "invert": false},
    "roll": {"axis": 3, "invert": false},
    "pitch": {"axis": 4, "invert": true},
    "arm": {"button": 5, "invert": false}
}
```

You can identify the axes by running:
```bash
sitl-gamepad
```
And moving the axes and buttons around


New terminal: Run
```bash
sitl path/to/gamepad_mapping.json
```


# Troubleshooting

Ports in use:

```bash
netstat -tulpn | grep 13337
netstat -tulpn | grep 6761
netstat -tulpn | grep 5761
netstat -tulpn | grep 9002
netstat -tulpn | grep 9003
netstat -tulpn | grep 9004
```

```bash
kill -9 {PID (last number in row)}
```
