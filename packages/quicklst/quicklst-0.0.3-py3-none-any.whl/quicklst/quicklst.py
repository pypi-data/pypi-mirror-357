from numba import uint32, int32, uint16, uint8, int64, boolean, njit
import numpy as np
import numba

if int(numba.__version__[2:4]) >= 50:
  from numba.experimental import jitclass
else:
  from numba import jitclass

import enum
import warnings
import os.path


# Types of list files
class ListFileType(enum.Enum):
  MPA3 = 0
  MPA4A = 1


class ListFile:
  """
  A class abstracting the reading of the ListFile in blocks
  """

  def __init__(self, file_name: str, block_size: uint32 = 2 ** 30):
    """
    Create a ListFile Object, this does not load any of the list file data immediately just parses the header.

    Note: you probably can safely ignore `block_size`, if your RAM fills up or you get an allocation error you can try
    reducing the block_size. `block_size` should be a multiple of 2.

    :param str file_name: name of ListFile
    :param uint32 block_size: Number of bytes to read at once
    """
    self._file_name = file_name
    if block_size % 2 != 0:
      raise RuntimeError("Block size must be a multiple of 2")
    self._block_size: uint32 = block_size

    # load start file up to `block_size`
    list_file = np.fromfile(file_name, dtype=np.uint8, count=block_size)

    # find start of data, type of the lst file (MPA3 or MPA4) and get the enabled adcs as a bit field
    self._data_start, self._ftype, self._active_adcs = _parse_header(list_file)
    self._file_size = os.path.getsize(file_name)

    # self._adc_map[i] will return the index of adc i in the adc field of ListFileBlock
    self._adc_map = np.full(8, -1, dtype='int32')
    mask = 1
    adci = 0
    for i in range(8):
      if self._active_adcs & mask == mask:
        self._adc_map[i] = adci
        adci += 1
      mask <<= 1

    self._cached_block = None
    self._total_time = None

  def get_file_type(self) -> str:
    """
    Get the type of mpa file.

    :return: either "MPA3" or "MPA4A" depending on the file
    """
    return "MPA3" if self._ftype == 0 else "MPA4A"

  def get_active_adcs(self) -> np.ndarray:
    """
    Returns a numpy array of bool, each index corresponds to an ADC the value is False if the ADC was disabled and true
    if it was enabled.

    :return: ndarray with status of each adc
    """
    active_adc_list = np.zeros(8, dtype='bool')
    mask = 1
    for i in range(8):
      active_adc_list[i] = self._active_adcs & mask == mask
      mask <<= 1
    return active_adc_list

  def blocks(self):
    if self._file_size <= (self._block_size - self._data_start):  # single block file
      if self._cached_block is None:
        block_data = np.fromfile(self._file_name, dtype="uint8", count=self._block_size, offset=self._data_start)
        if block_data.size % 2 == 1:
          warnings.warn("Data portion of the list file is not 16 bit aligned, truncated file")
          block_data = block_data[:-1]
        self._cached_block = ListFileBlock(block_data.view(np.uint16), 0, True, self._ftype, self._adc_map)
        self._total_time = self._cached_block.time[-1]
      yield self._cached_block
    else:
      block = None
      block_offset = self._data_start
      time_offset = 0
      while block_offset < self._file_size:
        block_data = np.fromfile(self._file_name, dtype="uint8", count=self._block_size, offset=block_offset)
        if block_data.size % 2 == 1:
          warnings.warn("Data portion of the list file is not 16 bit aligned, truncated file")
          block_data = block_data[:-1]
        read_to_end = self._file_size == block_offset + block_data.size
        block = ListFileBlock(block_data.view(np.uint16), time_offset, read_to_end, self._ftype, self._adc_map)
        block_offset += block.read_up_to
        if block.time.size > 0:  # the file might not contain a timer event in a block
          time_offset = block.time[-1]
        yield block
      self._total_time = block.time[-1] if block is not None else None

  def get_measured_time(self):
    """
    Get the time measured in ms

    can be slow if file has not been read fully yet

    :return: total measured time in ms
    """
    if self._total_time is None:
      for _ in self.blocks():
        pass  # once all blocks have been loaded the total time is set by the iterator
    return self._total_time

  def hist1d(self, adc: uint8, bin_size: uint16 = 1, coincident_adcs: uint8[:] = None):
    """
    Produces histogram from data of one adc.

    :param adc: index or indices of adc to put on the x axis
    :param bin_size: bin size adc1
    :param coincident_adcs: list of adc indices that are required to be coincident for an event to be counted
    :return: returns a (adc_x_max/bin_size) shaped histogram if adc is not an array otherwise returns a histogram of
      shape (len(adc), adc/bin_size)
    """
    try:
      if coincident_adcs is None:
        coincidence_bit_field = [1 << a for a in adc]
      else:
        len(adc)
        coincidence_bit_field: uint8 = 0
        try:
          for a in coincident_adcs:
            coincidence_bit_field |= 1 << a
          coincidence_bit_field = [coincidence_bit_field] * len(adc)
        except TypeError:
          coincidence_bit_field = [(1 << a) | (1 << coincident_adcs) for a in adc]
      n_bins = int(np.ceil(8192 / bin_size))
      hist = np.zeros((len(adc), n_bins), dtype='uint32')
      for block in self.blocks():
        _hist_index_range_many(block, hist, adc, bin_size, coincidence_bit_field, 0, block.time.size)
    except TypeError:
      # single adc
      if coincident_adcs is None:
        coincidence_bit_field = 1 << adc
      else:
        try:
          # make sure we have values for selected adcs
          coincidence_bit_field: uint8 = 0
          for a in coincident_adcs:
            coincidence_bit_field |= 1 << a
        except TypeError:
          # single adc
          coincidence_bit_field = (1 << adc) | (1 << coincident_adcs)

      n_bins = int(np.ceil(8192 / bin_size))
      hist = np.zeros(n_bins, dtype='uint32')
      for block in self.blocks():
        _hist_index_range(block, hist, adc, bin_size, coincidence_bit_field, 0, block.time.size)
    return hist

  def hist2d(self, adc_x: uint8, adc_y: uint8,
             bin_size_x: uint16 = 1, bin_size_y: uint16 = 1) -> uint32[:, :]:
    """
    Produces histogram from data of two adcs.

    :param adc_x: index of adc to put on the x axis
    :param adc_y: index of adc to put on the y axis
    :param bin_size_x: bin size adc1
    :param bin_size_y bin size adc2
    :return: returns a (adc_x_max/bin_x)X(adc_y_max/bin_y) histogram
    """
    x = int(np.ceil(8192 / bin_size_x))
    y = int(np.ceil(8192 / bin_size_y))
    hist = np.zeros((y, x), dtype='uint32')
    for block in self.blocks():
      _hist2d(block, hist, adc_x, adc_y, bin_size_x, bin_size_y)
    return hist

  def hist2d_area_of_interest(self, adc_x: uint8, adc_y: uint8, adc_aoi: uint8, aoi_min: uint16, aoi_max: uint16,
                              bin_size_x: uint16 = 1, bin_size_y: uint16 = 1) -> uint32[:, :]:
    """
    Produces histogram from data of two adcs for all events where the value of adc 3 lays within the range
    aoi_min..aoi_max.

    :param adc_x: index of adc to put on the x-axis
    :param adc_y: index of adc to put on the y-axis
    :param adc_aoi: index of adc to use for area of interest
    :param aoi_min: minimum area of interest (inclusive)
    :param aoi_max: maximum area of interest (inclusive)
    :param bin_size_x: bin size adc_x
    :param bin_size_y: bin size adc_y
    :return: returns a (adc_x_max/bin_x)X(adc_y_max/bin_y) histogram
    """

    x = int(np.ceil(8192 / bin_size_x))
    y = int(np.ceil(8192 / bin_size_y))
    hist = np.zeros((y, x), dtype='uint32')
    for block in self.blocks():
      _hist2d_area_of_interest(block, hist, adc_x, adc_y, adc_aoi, aoi_min, aoi_max, bin_size_x, bin_size_y)
    return hist

  def hist2d_time_of_interest(self, adc_x: uint8, adc_y: uint8, time_min: int64, time_max: int64,
                              bin_size_x: uint16 = 1, bin_size_y: uint16 = 1) -> uint32[:, :]:
    """
    Produces histogram from data of two adcs for all events where the value of adc 3 lays within the range
    aoi_min..aoi_max.

    :param adc_x: index of adc to put on the x-axis
    :param adc_y: index of adc to put on the y-axis
    :param time_min: minimum time since start of measurement in ms (inclusive)
    :param time_max: maximum time since start of measurement in ms (inclusive)
    :param bin_size_x: bin size adc_x
    :param bin_size_y: bin size adc_y
    :return: returns a (adc_x_max/bin_size_x)X(adc_y_max/bin_size_x) histogram
    """

    x = int(np.ceil(8192 / bin_size_x))
    y = int(np.ceil(8192 / bin_size_y))
    hist = np.zeros((y, x), dtype='uint32')
    for block in self.blocks():
      _hist2d_time_of_interest(block, hist, adc_x, adc_y, time_min, time_max, bin_size_x, bin_size_y)
    return hist

  def hist2d_time_adc(self, adc: uint8, time_bin_size: int64, time_min: int64 = 0, time_max: int64 = None,
                      adc_bin_size: uint16 = 1, coincident_adcs: uint8[:] = None, omit_incomplete_bin=None
                      ) -> uint32[:, :]:
    """
    Get a 2d histogram with time on one axis and the values of one adc on the other

    :param adc: adc for values
    :param time_bin_size: time span to bin in ms
    :param time_min: minimum time since measurement start in ms to be included in histogram
    :param time_max: maximum time since measurement start in ms to be included in histogram
    :param adc_bin_size: bin size adc
    :param coincident_adcs: indices of adcs that must be enabled for event to be counted
    :param omit_incomplete_bin: specify weather to include last time bin when it is smaller than the other ones.
     If set to `None` values are included but warning is emitted.
    """
    x = int(np.ceil(8192 / adc_bin_size))

    if coincident_adcs is None:
      coinc = 1 << adc
    else:
      # make sure we have values for selected adcs
      coinc: uint8 = 0
      for a in coincident_adcs:
        coinc |= 1 << a

    # TODO known array size
    hists = []
    make_new = True
    _iter = self.blocks()
    block = next(_iter)
    start = _seek_time(block, time_min)
    while True:
      stop = _seek_time(block, time_min + time_bin_size, start)
      if start == stop:
        print('wait')  # TODO handle properly
      if make_new:
        hists.append(np.zeros(x, dtype='uint32'))
      _hist_index_range(block, hists[-1], adc, adc_bin_size, coinc, start, stop)
      if stop == len(block.time):
        try:
          block = next(_iter)
        except StopIteration:
          break
        start = 0
        make_new = False
      else:
        start = stop
        time_min += time_bin_size
        if (time_max is not None and
                (time_min > time_max or (time_min + time_bin_size > time_max and omit_incomplete_bin))):
          break
        make_new = True

    if time_min + time_bin_size > block.time[-1] + 1:
      if omit_incomplete_bin is None:
        warnings.warn("Last time bin is shorter than the others")
        hist = np.array(hists)
      elif omit_incomplete_bin and time_max is None:
        hist = np.array(hists[:-1])
      else:
        hist = np.array(hists)
    else:
      hist = np.array(hists)
    return hist


"""
Layout of a ListFileBlock
"""
spec_block = [
  ('time', int64[:]),
  ('adc', uint16[:, :]),
  ('active_adcs', uint16[:]),
  ('read_up_to', int64),
  ('adc_map', int32[:])
]


@jitclass(spec_block)
class ListFileBlock:
  """
  Stores a block of a ListFile

  This is more of an internal class. Use only if the already defined methods for ListFile are not meeting your use case.
  """

  def __init__(self,
               file: uint16[:],
               time_offset: int64,
               file_end: boolean,
               file_type: uint32,
               adc_map: int32[:]):
    """
    Reads a ListFile block from an uint16 array.

    The start of the array should be aligned with one of the Signals. If
    `file_end` is true it is assumed that the end of the array is the end
    of the ListFile, if it is false the reader makes sure to stop reading
    once the content of a data Signal might be cut off. The index up to which
    was read is stored in `read_up_to`. When reading the next block the array
    should start from that index.

    Note: This reader does not support ListFiles with realtime clock data
    (not hard to add but would cost unnecessary time)

    Signals:
      MPA3: A Signal here refers to a Timer, Sync or Data event with all its
            corresponding data and padding I.e. a 0xFFFFFFFF for Sync etc.
      MPA4: Here its ether the 1ms timer, the single ADC event or the coinc adc,
            or put into other words the alignment should never fall within a data element.

    :param file: a numpy array/view of the data section of a list file
    :param time_offset: a time offset to add to all time entries
    :param file_end: boolean if the array end is aligned with Signal end
    :param file_type: one of MPA3 or MPA4A representing the type of .lst file
    :param adc_map: a map from adc index to the index in the resulting `adc` array
    """
    self.adc_map = adc_map
    if file_type == ListFileType.MPA3:
      self._read_mpa3(file, time_offset, file_end)
    elif file_type == ListFileType.MPA4A:
      self._read_mpa4a(file, time_offset, file_end)

  def _read_mpa3(self, file, time_offset, file_end):
    # estimate the required storage (2 words header, 1 word padding, 1 word data)
    capacity: int64 = len(file) // 4
    i: int64 = 1
    # prevent reading a data event that might be cut off
    # 2 words for the Signal header and active_adcs for the maximum of possible data words
    max_i = len(file) if file_end else len(file) - 10

    self.active_adcs = np.empty(capacity, dtype=np.uint16)
    self.time = np.empty(capacity, dtype=np.int64)
    self.adc = np.zeros((capacity, self.adc_map.max() + 1), dtype=np.uint16)

    # Actual read
    ctime: int64 = time_offset
    j: int64 = 0
    while i < max_i:
      # Sync
      if file[i] == 0xFFFF:
        i += 2
      # Timer
      elif file[i] & 0x4000:
        ctime += 1
        i += 2
      # Data
      else:
        self.active_adcs[j] = file[i - 1]
        self.time[j] = ctime

        # skip padding
        if file[i] & 0x8000:
          i += 1

        mask: uint16 = 1
        for k in range(8):
          if self.active_adcs[j] & mask:
            i += 1
            self.adc[j, self.adc_map[k]] = file[i]
          mask <<= 1

        j += 1
        i += 2
    # read up to index in bytes
    self.read_up_to = (i - 1) * 2
    self.active_adcs = self.active_adcs[:j]
    self.time = self.time[:j]
    self.adc = self.adc[:j, :]

  def _read_mpa4a(self, file, time_offset, file_end):
    i: int64 = 0
    # prevent reading a data event that might be cut off
    # 1 word header, 8 words data, 3 words padding for alignment
    max_i = len(file) if file_end else len(file) - 12

    capacity = len(file) // 4

    # allocate arrays
    self.active_adcs = np.empty(capacity, dtype=np.uint16)
    self.time = np.empty(capacity, dtype=np.int64)
    self.adc = np.zeros((capacity, self.adc_map.max() + 1), dtype=np.uint16)

    ctime: int64 = time_offset
    j: int64 = 0
    while i < max_i:
      # Timer
      if file[i] & 0b1111 == 0x8:
        ctime += 1
        i += 4
      # Data
      else:
        self.time[j] = ctime
        # Single ADC
        if file[i] & 0x40 == 0:
          active_adc = file[i] >> 3 & 0b111
          self.active_adcs[j] = 1 << active_adc
          self.adc[j, self.adc_map[active_adc]] = file[i+1] & 0x1FFF
          i += 4
        # Coincidence ADC
        else:
          active_adc: uint8 = file[i] >> 8
          self.active_adcs[j] = active_adc
          mask: uint8 = 1
          for k in range(8):
            if active_adc & mask:
              i += 1
              # if file[i] < 8192:
              self.adc[j, self.adc_map[k]] = file[i] & 0x1FFF
            mask <<= 1

          # skip padding
          i += 4 - i % 4

        j += 1
    # read up to index in bytes
    self.read_up_to = i * 2
    self.active_adcs = self.active_adcs[:j]
    self.time = self.time[:j]
    self.adc = self.adc[:j, :]


_mpa4a_header = np.frombuffer("[MPA4A]".encode('utf-8'), dtype='uint8')
# if any of these get longer than LISTDATA] you need to update the range check in _parse_header
_data_mpa4a_str = np.frombuffer("DATA]\r\n".encode('utf-8'), dtype='uint8')
_data_mpa3_str = np.frombuffer("LISTDATA]\r\n".encode('utf-8'), dtype='uint8')
_adc_header_str = np.frombuffer("ADC".encode('utf-8'), dtype='uint8')
_active_str = np.frombuffer("active=".encode('utf-8'), dtype='uint8')


@njit
def _parse_header(list_file: uint8[:]) -> tuple[int64, uint32, uint8]:
  """
  Currently not actually parsing. Just returns the index of where the header ends, file type and bit field of adcs.

  :param list_file: numpy array/view of ListFile in bytes
  :return: a triple containing the index where the data segment starts, the type of .lst file and a bitfield of active
   adcs
  """

  assert (len(list_file) > 8), "File to short to be a valid lst file"
  if np.all(list_file[:len(_mpa4a_header)] == _mpa4a_header):
    list_file_type = ListFileType.MPA4A
    data_str = _data_mpa4a_str
  else:
    list_file_type = ListFileType.MPA3
    data_str = _data_mpa3_str

  data_start: int64 = 0
  current_adc = -1
  adc_bitfield: uint8 = 0

  j = 0
  while j < (len(list_file) - len(_data_mpa3_str)):
    if list_file[j] == 0x5B:  # [
      j += 1
      if np.all(np.equal(list_file[j:j + len(data_str)], data_str)):
        data_start = j + len(data_str)
        break
      elif np.all(np.equal(list_file[j:j + len(_adc_header_str)], _adc_header_str)):
        current_adc = list_file[j + len(_adc_header_str)] - 48  # ascii to number
        j = j + len(_adc_header_str)
        continue
      else:
        # this is another section nothing to do with the previous adc
        current_adc = -1
    ok = True
    for k in range(len(_active_str)):
      if list_file[j + k] != _active_str[k]:
        ok = False
        break
    if ok:
      j += len(_active_str)
      if list_file[j] != 0x30 and current_adc != -1:
        adc_bitfield |= 1 << (current_adc - 1)
    j += 1

  if data_start == 0:
    raise RuntimeError("data marker not found")
  else:
    return data_start, list_file_type, adc_bitfield


@njit
def _hist2d(block: ListFileBlock, out_hist: uint32[:], adc1: uint8, adc2: uint8, adc1_bin_size: uint16,
            adc2_bin_size: uint16) -> uint32[:, :]:
  mask1 = 1 << adc1
  mask2 = 1 << adc2
  adc1i = block.adc_map[adc1]
  adc2i = block.adc_map[adc2]

  for i in range(len(block.time)):
    if block.active_adcs[i] & mask1 and block.active_adcs[i] & mask2:
      xv = block.adc[i, adc1i] // adc1_bin_size
      yv = block.adc[i, adc2i] // adc2_bin_size
      out_hist[yv, xv] += 1

  return out_hist


@njit
def _hist2d_area_of_interest(block: ListFileBlock, out_hist: uint32[:], adc1: uint8, adc2: uint8, adc3: uint8,
                             aoi_min: uint16, aoi_max: uint16, adc1_bin_size: uint16, adc2_bin_size: uint16
                             ) -> uint32[:, :]:
  mask1 = 1 << adc1
  mask2 = 1 << adc2
  mask3 = 1 << adc3
  adc1i = block.adc_map[adc1]
  adc2i = block.adc_map[adc2]
  adc3i = block.adc_map[adc3]

  for i in range(len(block.time)):
    if block.active_adcs[i] & mask1 and block.active_adcs[i] & mask2 and block.active_adcs[i] & mask3:
      if aoi_min <= block.adc[i, adc3i] <= aoi_max:
        xv = block.adc[i, adc1i] // adc1_bin_size
        yv = block.adc[i, adc2i] // adc2_bin_size
        out_hist[yv, xv] += 1

  return out_hist


@njit
def _seek_time(block: ListFileBlock, time: uint32, start: int64 = 0, stop: int64 = -1) -> int64:
  """
  seek index of first event with set time or larger

  :param block: ListFileBlock to work on
  :param time: time to find
  :param start: the lowest index to search
  :param stop: the highest index to search (inclusive), if negative -1 means until end of block, -2 until end excluding
  last element etc.
  :return: index of first event with time larger than `time` or len(block.time) if time is out of range
  """
  if stop < 0:
    stop = len(block.time) + stop
  if block.time[stop] < time:
    return len(block.time)
  if block.time[stop] - time < time - block.time[start]:
    i = 0
    for i in range(stop, start - 1, -1):
      if time > block.time[i]:
        return i + 1
    return i
  else:
    i = 0
    for i in range(start, stop + 1):
      if time < block.time[i]:
        return i
    return i


@njit
def _hist_index_range(block: ListFileBlock, out_hist: uint32[:], adc: uint8, bin_size: uint16, coinc: uint8,
                      start: int64, stop: int64) -> uint32[:]:
  """
  Creates 1d-histogram for the given adc and block
  indices must be in range (no bounds checks are done)
  """
  adci = block.adc_map[adc]

  for i in range(start, stop):
    if block.active_adcs[i] & coinc == coinc:
      xv = block.adc[i, adci] // bin_size
      out_hist[xv] += 1

  return out_hist


@njit
def _hist_index_range_many(block: ListFileBlock, out_hist: uint32[:], adcs: uint8, bin_size: uint16, coincs: uint8,
                      start: int64, stop: int64) -> uint32[:]:
  """
  Creates 1d-histogram for the given adcs and block
  indices must be in range (no bounds checks are done)
  """
  adcis = [block.adc_map[adc] for adc in adcs]

  for i in range(start, stop):
    for j, (adci, coinc) in enumerate(zip(adcis, coincs)):
      if block.active_adcs[i] & coinc == coinc:
        xv = block.adc[i, adci] // bin_size
        out_hist[j, xv] += 1

  return out_hist


@njit
def _hist2d_time_of_interest(block: ListFileBlock, out_hist: uint32[:], adc1: uint8, adc2: uint8, time_min: int64,
                             time_max: int64, adc1_bin_size: uint16, adc2_bin_size: uint16) -> uint32[:, :]:
  mask1 = 1 << adc1
  mask2 = 1 << adc2
  mask = mask1 & mask2
  adc1i = block.adc_map[adc1]
  adc2i = block.adc_map[adc2]

  i = 0
  while i < len(block.time) and block.time[i] < time_min:
    i += 1

  for j in range(i, len(block.time)):
    if block.time[j] > time_max:
      break
    if block.active_adcs[j] & mask == mask:
      xv = block.adc[j, adc1i] // adc1_bin_size
      yv = block.adc[j, adc2i] // adc2_bin_size
      out_hist[yv, xv] += 1

  return out_hist


@njit
def down_bin(hist, factor=8):
  """
  Crudely bins given 2d histogram
  """
  out = np.zeros((hist.shape[0] // factor + 1, hist.shape[1] // factor + 1), dtype=hist.dtype)
  for i in range(hist.shape[0]):
    for j in range(hist.shape[1]):
      out[i // factor, j // factor] += hist[i, j]
  return out
