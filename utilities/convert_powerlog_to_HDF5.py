#!/usr/bin/env python3
'''
Convert an existing DBBC3 power logfile from ASCII into a HDF5 data structure,
compatible with EHT 2021+ VLBI power logs.

Hdf5:
 /samples_per_second int32
 /start_vdif_epoch   int32
 /start_vdif_second  int32
 /lsb/high/lcp/attn/
       ./placeholder   uint8
       ./scale         float32
       ./data  [N x 1] uint8
 /lsb/high/lcp/pwr/
       ./placeholder   uint32
       ./scale         float32
       ./data  [N x 1] uint32
 /lsb/high/rcp/attn/
       ...
 /lsb/high/rcp/pwr/
       ...

 /lsb/low/lcp/attn/
 /lsb/low/lcp/pwr/
 /lsb/high/rcp/attn/
 /lsb/high/rcp/pwr/

and same for /usb

'''

from collections import OrderedDict
import datetime
import h5py
import sys

class VDIFTime(object):
	'''Part of the VDIFTime class included in vlbicontrol and written by A. Young'''

	EPOCH_0_YEAR = 2000
	EPOCH_0_MONTH = 1
	EPOCH_0_DAY = 1
	EPOCH_0_HOUR = 0
	EPOCH_0_MINUTE = 0
	EPOCH_0_SECOND = 0
	MONTHS_PER_EPOCH = 6
	EPOCHS_PER_YEAR = 2
	DEFAULT_FRAME_RATE = 125000

	def __init__(self, epoch, sec, frame=0, frame_rate=DEFAULT_FRAME_RATE):
		self.epoch = epoch
		self.sec = sec
		self.frame = frame
		self.frame_rate = frame_rate
		self.nsec = (frame * (1.0/self.frame_rate) * 1e9)

	def to_datetime(self):
		# Create datetime that corresponds to start of epoch
		epoch_date = datetime.datetime(year=self.EPOCH_0_YEAR + self.epoch//self.EPOCHS_PER_YEAR,
		  month=self.EPOCH_0_MONTH + self.MONTHS_PER_EPOCH*(self.epoch % self.EPOCHS_PER_YEAR), day=self.EPOCH_0_DAY,
		  hour=self.EPOCH_0_HOUR, minute=self.EPOCH_0_MINUTE, second=self.EPOCH_0_SECOND)

		# Add offset since start of epoch
		usec = int(self.nsec / 1e3)
		epoch_offset = datetime.timedelta(seconds=self.sec, microseconds=usec)
		date = epoch_date + epoch_offset

		return date

	@classmethod
	def from_datetime(cls, date, frame_rate=DEFAULT_FRAME_RATE):
		# Calculate epoch number
		epoch = 2 * (date.year - cls.EPOCH_0_YEAR) + 1 * (date.month > cls.MONTHS_PER_EPOCH)

		# Calculate seconds offset
		epoch_date = cls(epoch, 0).to_datetime()
		delta = date - epoch_date
		sec = delta.days * 24 * 60 * 60 + delta.seconds

		# Calculate frame offset
		frame_period = 1.0/frame_rate
		frame = int(date.microsecond * 1e-6 / frame_period)

		return cls(epoch, sec, frame=frame, frame_rate=frame_rate)


class LogHDF5:

	def __init__(self, logname):
		'''
		Create a HDF5 file and initialize the default EHT2021 header elements,
		using values specific to DBBC3:
		1) DBBC3 "agc" equivalent of the BDC/Attenuator: 1 integer step = 0.5 dB attenuation step
		2) DBBC3 "count" to absolute voltage: scale is ??? <todo>
		   "GCoMos sind von Michael so kalibriert das sie bei 32k counts -1.5dBm am Samplereingang bereitstellen"
		3) DBBC3 samples per second is equal to 1.0 -- no sub-second power readings, only integer seconds
		'''

		self.n_samples_per_second = 1
		self.vdif_start_epoch = 0
		self.vdif_start_sec = 0
		self.Ndatapoints = 0

		self.fout = h5py.File(logname, "w")

		self.fout.require_dataset("start_vdif_epoch", shape=(), dtype="i4", data=self.vdif_start_epoch)
		self.fout.require_dataset("start_vdif_second", shape=(), dtype="i4", data=self.vdif_start_sec)
		self.fout.require_dataset("samples_per_second", shape=(), dtype="i4", data=self.n_samples_per_second)
		self.att_datasets = OrderedDict()  # NB: under Python>=3.6 could switch back to normal dict/{}, it is ordered like OrderedDict
		self.pwr_datasets = OrderedDict()

		for rxSb in ['lsb','usb']:
			for if2Sb in ['high','low']:
				for pol in ['lcp','rcp']:
					key_root = '/%s/%s/%s/' % (rxSb,if2Sb,pol)

					# Header
					self.fout.require_dataset(key_root+'/attn/placeholder', shape=(), dtype="u1", data=255)
					self.fout.require_dataset(key_root+'/attn/scale', shape=(), dtype="f", data=0.5)
					self.fout.require_dataset(key_root+'/pwr/placeholder', shape=(), dtype="u4", data=2**32-1)
					self.fout.require_dataset(key_root+'/pwr/scale', shape=(), dtype="f", data=0.5)

					self.fout[key_root+'/attn/placeholder'].attrs["description"] = "Missing samples in attenuator data have this value."
					self.fout[key_root+'/pwr/placeholder'].attrs["description"] = "Missing samples in average power data have this value."

					self.fout[key_root+'/attn/scale'].attrs["description"] = "Multiplying with this constant scales attenuator values to decibel."
					self.fout[key_root+'/pwr/scale'].attrs["description"] = "Multiplying with this constant scales power data to mean-square of 8-bit samples."

					# Data time series
					self.att_datasets[key_root+'/attn/data'] = self.fout.create_dataset(key_root+'/attn/data', shape=(1,), maxshape=(None, ), dtype="u1", chunks=True)
					self.pwr_datasets[key_root+'/pwr/data'] = self.fout.create_dataset(key_root+'/pwr/data', shape=(1,self.n_samples_per_second), maxshape=(None, self.n_samples_per_second), dtype="u4", chunks=True)

					self.fout[key_root+'/attn/data'].attrs["description"] = "Attenuator values (arbitrary logarithmic scale). Time increases uniformly by 1-second intervals along 1st dimension."
					self.fout[key_root+'/pwr/data'].attrs["description"] = "Average power (arbitrary linear scale) computed over each sampling period. Time increases uniformly by sub-second intervals along 2nd dimension, and 1-second intervals along 1st dimension."


	def addDBBC3Readings(self, isotime, counts=[], attens=[]):

		# Need to map DBBC3 4 GHz IFs to equivalent R2DBE/EHT 2 GHz bands
		# 4 core3h --> 8 r2dbe
		# IF-A = usb/high/lcp + usb/low/lcp ?
		# IF-B = usb/high/rcp + usb/low/rcp ?
		# IF-C = lsb/high/lcp + usb/low/lcp ?
		# IF-D = lsb/high/rcp + usb/low/rcp ?
		counts_r2dbe = counts + counts  # TODO: [lsb:usb] x [high:low] x [lcp:rcp]
		attens_r2dbe = attens + attens

		for idx, key in zip( range(len(self.att_datasets)), list(self.att_datasets.keys())):
			dataset = self.att_datasets[key]
			dataset.resize((dataset.shape[0] + 1), axis=0)
			dataset[-1:] = attens_r2dbe[idx]
			# print(idx, key, dataset, self.Ndatapoints)

		for idx, key in zip( range(len(self.pwr_datasets)), list(self.pwr_datasets.keys())):
			dataset = self.pwr_datasets[key]
			dataset.resize((dataset.shape[0] + 1), axis=0)
			dataset[-1:] = counts_r2dbe[idx] // 2
			# print(idx, key, dataset, self.Ndatapoints)

		self.Ndatapoints += 1


def convertToHDF5(logname):

	hdfname = logname + '.hdf5'
	hdfout = LogHDF5(hdfname)
	fin = open(logname, "r")

	while True:
		s = fin.readline()
		if not s:
			break

		s = s.strip()
		if len(s)>0 and s[0] == '#':
			continue

		vals = s.split()
		if len(vals) < 2:
			continue

		vdif_time = VDIFTime.from_datetime(datetime.datetime.strptime(vals[0], "%Y-%m-%dT%H:%M:%S"))
		# vdif_time = VDIFTime.from_datetime(datetime.datetime.fromisoformat(vals[0])) # fromisoformat: Python 3.7+
		counts = [int(v) for v in vals[1::2]]
		attens = [int(v) for v in vals[2::2]]

		print('Adding log entry for time %s' % (vdif_time.to_datetime().isoformat()), end='\r')
		hdfout.addDBBC3Readings(vdif_time, counts, attens)

		#if hdfout.Ndatapoints > 1200:
		#	break

	print()
	print('Added %d power log entries to HDF5 output file: %s' % (hdfout.Ndatapoints,hdfname))


if len(sys.argv) > 1:
	if '-h' in sys.argv[1] or '--help' in sys.argv[1] or sys.argv[1][0] == '-':
		print ('Usage: convert_powerlog_to_HDF5.py <dbbc3_power.log>')
	else:
		convertToHDF5(sys.argv[1])
