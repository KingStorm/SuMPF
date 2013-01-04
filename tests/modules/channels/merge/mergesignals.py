# SuMPF - Sound using a Monkeyforest-like processing framework
# Copyright (C) 2012-2013 Jonas Schulte-Coerne
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import unittest

import sumpf

from .connectiontester import ConnectionTester


class TestMergeSignals(unittest.TestCase):
	"""
	A test case for the MergeSignals module
	"""
	def setUp(self):
		self.merger = sumpf.modules.MergeSignals()
		self.signal1 = sumpf.Signal(channels=((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3)), samplingrate=42.0, labels=("1.1", "1.2", "1.3"))
		self.signal2 = sumpf.Signal(channels=((21.1, 21.2, 21.3), (22.1, 22.2, 22.3)), samplingrate=42.0, labels=("2.1", "2.2"))
		self.signal3 = sumpf.Signal(channels=((31.1, 31.2), (32.1, 32.2), (33.1, 33.2)), samplingrate=42.0)
		self.signal4 = sumpf.Signal(channels=((41.1, 41.2, 41.3), (42.1, 42.2, 42.3), (43.1, 43.2, 43.3)), samplingrate=23.0)
		self.signal5 = sumpf.Signal(channels=((51.1, 51.2, 51.3, 51.4), (52.1, 52.2, 52.3, 52.4)), samplingrate=42.0)

	def test_merge(self):
		"""
		Tests if the merge works as expected
		"""
		self.assertEqual(self.merger.GetOutput().GetChannels(), sumpf.Signal().GetChannels())		# this must not raise an error, instead it should return an empty Signal
		self.merger.SetMergeStrategy(sumpf.modules.MergeSignals.FIRST_SIGNAL_FIRST)
		id1 = self.merger.AddInput(self.signal1)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate())	# sampling rate should have been taken from the first signal
		self.assertEqual(self.merger.GetOutput().GetChannels(), self.signal1.GetChannels())			# channel data should have been taken from the first signal
		id2 = self.merger.AddInput(self.signal2)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate())	# sampling rate should not have changed
		channels = ((11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3), (21.1, 21.2, 21.3), (22.1, 22.2, 22.3))
		self.assertEqual(self.merger.GetOutput().GetChannels(), channels)							# channel data should be the channels from the first signal with the second signal's channels appended
		self.assertEqual(self.merger.GetOutput().GetLabels(), ("1.1", "1.2", "1.3", "2.1", "2.2"))	# the labels should have been taken from the input Signals
		self.merger.RemoveInput(id1)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal2.GetSamplingRate())	# sampling rate should not have changed
		self.assertEqual(self.merger.GetOutput().GetChannels(), self.signal2.GetChannels())			# The channel data from the first signal should have been removed
		id1 = self.merger.AddInput(self.signal1)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate())	# sampling rate should not have changed
		channels = ((21.1, 21.2, 21.3), (22.1, 22.2, 22.3), (11.1, 11.2, 11.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
		self.assertEqual(self.merger.GetOutput().GetChannels(), channels)								# now the second Signal should come before the first Signal
		self.merger.SetMergeStrategy(sumpf.modules.MergeSignals.FIRST_CHANNEL_FIRST)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal1.GetSamplingRate())
		channels = ((21.1, 21.2, 21.3), (11.1, 11.2, 11.3), (22.1, 22.2, 22.3), (12.1, 12.2, 12.3), (13.1, 13.2, 13.3))
		self.assertEqual(self.merger.GetOutput().GetChannels(), channels)							# now the order should have been changed according to the other merge strategy
		self.assertEqual(self.merger.GetOutput().GetLabels(), ("2.1", "1.1", "2.2", "1.2", "1.3"))	# the labels should have been taken from the input Signals
		self.merger.RemoveInput(id1)
		self.merger.RemoveInput(id2)
		id4 = self.merger.AddInput(self.signal4)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), self.signal4.GetSamplingRate())	# the sampling rate should have been taken from the fourth signal
		self.assertEqual(self.merger.GetNumberOfOutputChannels(), len(self.signal4.GetChannels()))	# the GetNumberOfOutputChannels should also work as expected

	def test_errors(self):
		"""
		Tests if errors are raised correctly
		"""
		self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR)
		id1 = self.merger.AddInput(self.signal1)
		self.assertRaises(ValueError, self.merger.RemoveInput, id1 + 42)		# this should fail because id does not exist
		self.assertRaises(ValueError, self.merger.AddInput, self.signal3)		# this should fail because channels do not have the same length
		self.assertRaises(ValueError, self.merger.AddInput, self.signal4)		# this should fail because sampling rate is not equal
		self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
		self.merger.AddInput(self.signal3)
		self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR)
		self.assertRaises(RuntimeError, self.merger.GetOutput)					# this should fail because channels do not have the same length

	def test_length_conflict_resolution(self):
		"""
		Tests if adding Signals with different lengths works as expected.
		"""
		self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.FILL_WITH_ZEROS)
		id1 = self.merger.AddInput(self.signal1)
		id3 = self.merger.AddInput(self.signal3)
		channels = self.merger.GetOutput().GetChannels()
		self.assertEqual(channels[0:3], self.signal1.GetChannels())			# the longer Signal should simply be copied
		self.assertEqual(channels[3][0:2], self.signal3.GetChannels()[0])	# first elements should be the same as in the shorter Signal
		self.assertEqual(channels[3][2], 0.0)								# zeros should be added to the shorter Signal
		self.merger.SetLengthConflictStrategy(sumpf.modules.MergeSignals.RAISE_ERROR_EXCEPT_EMPTY)
		self.assertRaises(RuntimeError, self.merger.GetOutput)				# this should fail because channels do not have the same length
		self.merger.RemoveInput(id3)
		self.assertRaises(ValueError, self.merger.AddInput, self.signal3)	# this should fail because channels are neither empty nor have the same length
		ide = self.merger.AddInput(sumpf.Signal())
		self.assertRaises(ValueError, self.merger.AddInput, self.signal3)	# this should fail because channels are neither empty nor have the same length
		channels = self.merger.GetOutput().GetChannels()
		samplingrate = self.merger.GetOutput().GetSamplingRate()
		self.assertEqual(channels[0:3], self.signal1.GetChannels())			# the first Signal should simply be copied
		self.assertEqual(channels[3], (0.0,) * len(self.signal1))			# the empty Signal should be stretched with zeros
		self.assertEqual(samplingrate, self.signal1.GetSamplingRate())		# the sampling rate should have been taken from the non empty Signal
		self.merger.RemoveInput(id1)
		id5 = self.merger.AddInput(self.signal5)
		self.assertRaises(ValueError, self.merger.AddInput, self.signal3)	# this should fail because channels are neither empty nor have the same length
		channels = self.merger.GetOutput().GetChannels()
		samplingrate = self.merger.GetOutput().GetSamplingRate()
		self.assertEqual(channels[0], (0.0,) * len(self.signal5))			# the empty Signal should again be stretched with zeros
		self.assertEqual(channels[1:3], self.signal5.GetChannels())			# the non empty Signal should simply be copied
		self.assertEqual(samplingrate, self.signal1.GetSamplingRate())		# the sampling rate should have been taken from the non empty Signal

	def test_connections(self):
		"""
		Tests if the connections work
		"""
		tester1 = ConnectionTester()
		tester2 = ConnectionTester()
		sumpf.connect(self.merger.GetOutput, tester1.Trigger)
		sumpf.connect(tester1.GetSignal, self.merger.AddInput)
		self.assertTrue(tester1.triggered)									# connecting to input should work and it should trigger the output
		self.assertEqual(len(self.merger.GetOutput().GetChannels()), 1)		# after adding one connection there should be one channel in the output signal
		tester1.SetSamplingRate(44100)
		self.assertEqual(self.merger.GetOutput().GetSamplingRate(), 44100)	# changing the sampling rate of the only signal in the merger should be possible
		tester1.SetSamplingRate(48000)
		sumpf.connect(tester2.GetSignal, self.merger.AddInput)
		self.assertEqual(len(self.merger.GetOutput().GetChannels()), 2)		# after adding a second connection there should be two channels in the output signal
		tester1.triggered = False
		sumpf.disconnect(tester1.GetSignal, self.merger.AddInput)
		self.assertTrue(tester1.triggered)									# disconnecting from input should should trigger the output aswell
		self.assertEqual(len(self.merger.GetOutput().GetChannels()), 1)		# after removing one connection there should be one channel left in the output signal

