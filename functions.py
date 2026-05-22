# src/wii_remote_pkg/functions.py
"""
Wii Remote manager for Windows.

Public API:
	WiiRemoteManager() - class to manage opening/closing, reading, writing, calibration, rumble, etc.
"""

import time
import platform
import hid
try:
	import hid  # cython-hid or hidapi wrapper
except Exception as e:
	hid = None  # Raise informative error only when used

from .constants import WiiRemoteConstants

class WiiRemoteManager:
	"""
	Manager for a Wii Remote HID device.

	Notes:
	- Designed for Windows only (as requested).
	- Requires `cython-hid` or compatible `hid`/`hidapi` package to be installed.
	"""

	def __init__(self):
		if platform.system().lower() != "windows":
			raise OSError("This package is intended for Windows only.")

		if hid is None:
			raise ImportError(
				"Missing HID backend. Install the dependency (e.g. `pip install cython-hid`) before using WiiRemoteManager."
			)

		self.device = None
		self.wd = WiiRemoteConstants()

		# Calibration flags/values
		self.is_collecting_data = True
		self.yaw_zero = 0x1F7F
		self.roll_zero = 0x1F7F
		self.pitch_zero = 0x1F7F

		self.x0 = 1
		self.y0 = 1
		self.z0 = 1

		self.x_scale = 1
		self.y_scale = 1
		self.z_scale = 1

	# ------------------------
	# Connection
	# ------------------------
	def open(self):
		"""Open connection to Wii Remote. Returns True on success."""
		try:
			self.device = hid.device() # type: ignore
			# open(VENDOR_ID, PRODUCT_ID)
			self.device.open(self.wd.VENDOR_ID, self.wd.PRODUCT_ID)
			# Optional: set non-blocking reads if desired:
			try:
				self.device.set_nonblocking(True)
			except Exception:
				# not all backends implement set_nonblocking
				pass
			print("Wii Remote connected.")
			return True
		except Exception as e:
			self.device = None
			raise ConnectionError(f"Failed to connect to Wii Remote: {e}")

	def is_connected(self):
		return self.device is not None

	def close(self):
		"""Gracefully close the connection."""
		if self.device:
			# Try to restore a safe report mode (core buttons)
			try:
				self.write_cmd(self.wd.CMD_BTN)
			except Exception:
				# ignore write errors during close
				pass
			try:
				self.device.close()
			except Exception:
				pass
			self.device = None
			print("Wii Remote closed.")
		else:
			print("No Wii Remote connection to close.")

	# ------------------------
	# Calibration
	# ------------------------
	def calibrate_motion_plus(self, duration=2, sample_rate=100):
		"""Calibrate Motion Plus by keeping the remote still.

		Collects samples for `duration` seconds at approximately `sample_rate` Hz.
		"""
		print(f"Calibrating Motion Plus... Keep still for {duration}s")
		yaw_vals, pitch_vals, roll_vals = [], [], []
		start = time.time()
		while time.time() - start < duration:
			raw = self.read_raw()
			if raw and len(raw) >= 12:
				gyro_data = raw[6:12]
				# preserve your original bit math
				yaw_speed = (gyro_data[3] & 0xFC) << 6 | gyro_data[0]
				pitch_speed = (gyro_data[5] & 0xFC) << 6 | gyro_data[2]
				roll_speed = (gyro_data[4] & 0xFC) << 6 | gyro_data[1]
				yaw_vals.append(yaw_speed)
				pitch_vals.append(pitch_speed)
				roll_vals.append(roll_speed)
			time.sleep(1 / sample_rate)
		if yaw_vals:
			self.yaw_zero = sum(yaw_vals) / len(yaw_vals)
			self.pitch_zero = sum(pitch_vals) / len(pitch_vals)
			self.roll_zero = sum(roll_vals) / len(roll_vals)
			print("Motion Plus calibration complete.")
		else:
			print("No samples collected for Motion Plus calibration.")

	def calibrate_accelerometer(self, duration=2):
		"""Interactive accelerometer calibration with 3 orientations."""
		def collect(position):
			input(f"Place Wii Remote {position} and press Enter...")
			print(f"Collecting data for {position}...")
			data = []
			start = time.time()
			while time.time() - start < duration:
				d = self.read()
				if d:
					data.append((d.get("raw_acc_x"), d.get("raw_acc_y"), d.get("raw_acc_z")))
			if not data:
				return 0, 0, 0
			xs, ys, zs = zip(*data)
			return sum(xs)/len(xs), sum(ys)/len(ys), sum(zs)/len(zs)

		x1, y1, z1 = collect("flat with A button facing up")
		x2, y2, z2 = collect("IR sensor down on table")
		x3, y3, z3 = collect("on its side (left side up)")

		self.x0 = (x1 + x2) / 2
		self.y0 = (y1 + y3) / 2
		self.z0 = (z2 + z3) / 2
		self.x_scale = x3 - self.x0 if (x3 - self.x0) != 0 else 1
		self.y_scale = y2 - self.y0 if (y2 - self.y0) != 0 else 1
		self.z_scale = z1 - self.z0 if (z1 - self.z0) != 0 else 1

		print("Accelerometer calibration complete.")

	def manually_calibrate_motion_plus(self, yaw_zero, pitch_zero, roll_zero):
		self.yaw_zero = yaw_zero
		self.pitch_zero = pitch_zero
		self.roll_zero = roll_zero

	def manually_calibrate_accelerometer(self, x0, y0, z0, x_scale, y_scale, z_scale):
		self.x0 = x0
		self.y0 = y0
		self.z0 = z0
		self.x_scale = x_scale
		self.y_scale = y_scale
		self.z_scale = z_scale

	# ------------------------
	# I/O
	# ------------------------
	def write_raw(self, address, data):
		report_id = 0x16
		write_cmd = [report_id, 0x04, (address >> 16) & 0xFF, (address >> 8) & 0xFF, address & 0xFF, len(data)] + data
		self.device.write(write_cmd) # type: ignore

	def write_cmd_raw(self, command_array: list, cmd_err_descr = "No command specified"):
		try:
			if self.device:
				self.device.write(command_array)
		except IOError as e:
			print("Failed command: " + cmd_err_descr + "Raw Command: " + str(command_array))

	def write_cmd(self, command_dict: dict):
		"""Write a command to the device.

		command_dict is expected to contain a "command" key with a list of ints.
		This function attempts multiple reasonable encodings for compatibility.
		"""
		if not self.device:
			raise RuntimeError("No device connected.")
		cmd = command_dict.get("command")
		if cmd is None:
			raise ValueError("command_dict must contain a 'command' key.")

		# Try sending as-is
		try:
			self.device.write(cmd)
			return
		except Exception:
			# fallback to bytes
			pass

		# If list/iterable of ints convert to bytes
		try:
			if isinstance(cmd, (bytes, bytearray)):
				buf = bytes(cmd)
			else:
				buf = bytes(bytearray(cmd))
			self.device.write(buf)
			return
		except Exception as e:
			raise IOError(f"Failed to write command to device: {e}")

	def read(self):
		"""Read parsed data (dict). Returns None if no data."""
		if not self.device:
			return None
		try:
			# Read up to 256 bytes. Depending on backend this returns list[int] or bytes.
			data = self.device.read(256)
			if not data:
				return None

			# Normalize to list of ints
			if isinstance(data, (bytes, bytearray)):
				hex_data = list(data)
			else:
				hex_data = list(data)

			d = {
				"timestamp": time.time(),
				"report_mode": hex_data[0] if len(hex_data) > 0 else None,
				"buttons": self.extract_buttons(hex_data),
				"acc_x": None, "acc_y": None, "acc_z": None,
				"roll": None, "pitch": None, "yaw": None
			}
			# report_mode values for core + accel etc.
			if hex_data and hex_data[0] in [0x31, 0x33, 0x35, 0x37]:
				try:
					raw = self.convert_acc(hex_data)
					d["raw_acc_x"], d["raw_acc_y"], d["raw_acc_z"], d["acc_x"], d["acc_y"], d["acc_z"] = raw
				except Exception:
					# don't fail entire read if accel parsing fails
					pass
			if hex_data and hex_data[0] == 0x35:
				try:
					d["roll"], d["pitch"], d["yaw"] = self.convert_motion_plus(hex_data)
				except Exception:
					pass
			return d
		except Exception:
			# Non-fatal read failure
			return None

	def read_raw(self):
		"""Return raw byte list or None."""
		if not self.device:
			return None
		try:
			data = self.device.read(256)
			if not data:
				return []
			if isinstance(data, (bytes, bytearray)):
				return list(data)
			return list(data)
		except Exception:
			return None

	# ------------------------
	# Utilities
	# ------------------------
	def rumble(self, duration=0.5):
		"""Rumble motor for up to MAX_RUMBLE_TIME seconds."""
		self.write_cmd(self.wd.CMD_RUMBLE_ON)
		time.sleep(min(duration, self.wd.MAX_RUMBLE_TIME))
		self.write_cmd(self.wd.CMD_RUMBLE_OFF)

	def extract_buttons(self, hex_data):
		"""Return a list of pressed button labels (from constants)."""
		buttons = []
		if len(hex_data) < 3:
			return buttons
		if hex_data[1] & 0x10: buttons.append(self.wd.BTN_PLUS)
		if hex_data[1] & 0x08: buttons.append(self.wd.BTN_UP)
		if hex_data[1] & 0x04: buttons.append(self.wd.BTN_DOWN)
		if hex_data[1] & 0x02: buttons.append(self.wd.BTN_RIGHT)
		if hex_data[1] & 0x01: buttons.append(self.wd.BTN_LEFT)
		if hex_data[2] & 0x10: buttons.append(self.wd.BTN_MINUS)
		if hex_data[2] & 0x08: buttons.append(self.wd.BTN_A)
		if hex_data[2] & 0x04: buttons.append(self.wd.BTN_B)
		if hex_data[2] & 0x02: buttons.append(self.wd.BTN_1)
		if hex_data[2] & 0x01: buttons.append(self.wd.BTN_2)
		if hex_data[2] & 0x80: buttons.append(self.wd.BTN_HOME)
		return buttons

	def convert_motion_plus(self, data):
		"""Parse motion-plus bytes into roll, pitch, yaw (degrees/sec-ish)."""
		if len(data) != 22:
			# Some backends return variable lengths; be conservative
			raise ValueError(f"Expected 22 bytes, got {len(data)}.")
		yaw = (data[9] & 0xFC) << 6 | data[6]
		roll = (data[10] & 0xFC) << 6 | data[7]
		pitch = (data[11] & 0xFC) << 6 | data[8]
		yaw -= self.yaw_zero; roll -= self.roll_zero; pitch -= self.pitch_zero
		scale = 13.768
		return roll/scale, pitch/scale, yaw/scale

	def convert_acc(self, data):
		"""Parse accelerometer bytes and apply calibration offsets/scales."""
		if len(data) != 22:
			raise ValueError(f"Expected 22 bytes, got {len(data)}.")
		x_raw = (data[3] << 2) | ((data[1] >> 5) & 0x03)
		y_raw = (data[4] << 1) | ((data[2] >> 4) & 0x01)
		z_raw = (data[5] << 1) | ((data[2] >> 6) & 0x01)
		x = (x_raw - self.x0) / (self.x_scale if self.x_scale != 0 else 1)
		y = (y_raw - self.y0) / (self.y_scale if self.y_scale != 0 else 1)
		z = (z_raw - self.z0) / (self.z_scale if self.z_scale != 0 else 1)
		return x_raw, y_raw, z_raw, x, y, z

	# ------------------------
	# Extension Functions
	# ------------------------
	def initialize_motion_plus(self):
		self.write_raw(0xA600F0, [0x55])

	def activate_motion_plus(self):
		self.write_raw(0xA600FE, [0x04])

	def deactivate_motion_plus(self):
		self.write_raw(0xA400F0, [0x55])
		self.write_cmd(self.wd.CMD_BTN_ACC)
